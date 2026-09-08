#!/usr/bin/env python3
"""KappaRisk research API.

This service exposes the finance κ mapping as a transparent research
diagnostic. It is **not** investment advice, a production trading signal, or a
claim that κ has been validated for arbitrary symbols.

Current evidence state (2026-09-08):
- the historical March S&P validation claim was retired after adverse audit;
- KFIN-V2-20260908-001 is a preserved procedural failure;
- KFIN-V2_1-20260908-002 earned a bounded incremental-content PASS on one
  preregistered S&P holdout using average precision.

The live API does not inherit that bounded S&P result as symbol-general
predictive validation.
"""

from datetime import datetime, timedelta
from functools import lru_cache
from typing import List, Optional

import numpy as np
import pandas as pd
import yfinance as yf
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

app = FastAPI(
    title="KappaRisk Research API",
    description=(
        "Experimental κ-stability diagnostics for research. No investment "
        "advice, production trading signal, or symbol-general validation claim."
    ),
    version="1.1.0",
)

security = HTTPBearer()

# Demo credentials only. This repository is public; these are not secrets and
# must never be treated as production authentication.
API_KEYS = {
    "test_key_123": {"tier": "demo", "requests": 0, "limit": 100},
    "pro_key_456": {"tier": "demo_extended", "requests": 0, "limit": 10000},
}

kappa_cache = {}
CACHE_TTL = 300
MIN_HISTORY_ROWS = 60

EVIDENCE_STATE = {
    "historical_march": "ADVERSE_VALIDATION_RETIRED",
    "kfin_v2": "PROCEDURAL_FAIL_PRESERVED",
    "kfin_v2_1": "BOUNDED_INCREMENTAL_CONTENT_PASS_ON_FROZEN_SP500_AP_TEST",
    "symbol_general_api_validation": "NOT_ESTABLISHED",
}


class KappaRequest(BaseModel):
    symbol: str
    window: int = 20
    trend_period: int = 50


class SubscriptionRequest(BaseModel):
    symbols: List[str]
    threshold_type: str = "percentile"
    threshold_value: float = 95.0
    webhook_url: Optional[str] = None
    email: Optional[str] = None


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid demo API key")

    key_data = API_KEYS[token]
    if key_data["requests"] >= key_data["limit"]:
        raise HTTPException(status_code=429, detail="Demo rate limit exceeded")

    key_data["requests"] += 1
    return key_data


def _close_series(data: pd.DataFrame) -> pd.Series:
    if "Close" not in data.columns:
        raise ValueError("Close column missing")
    close = pd.to_numeric(data["Close"], errors="coerce")
    if isinstance(close, pd.DataFrame):
        # Defensive handling for provider MultiIndex/duplicate-column shapes.
        close = close.iloc[:, 0]
    return close.astype(float)


def compute_kappa_frame(data: pd.DataFrame, window: int = 20, trend_period: int = 50) -> pd.DataFrame:
    """Compute the declared finance β, D, ρ, κ series.

    The returned score is a research coordinate. This function does not assign
    a predictive or safety meaning to κ < 1 or any other universal threshold.
    """
    if window < 3 or trend_period < 3:
        raise ValueError("window and trend_period must both be >= 3")

    close = _close_series(data)
    returns = close.pct_change()

    beta = returns.rolling(window).std() * np.sqrt(252.0)
    trend = close.rolling(trend_period).mean()
    D = (close - trend).abs() / trend

    def safe_autocorr(values):
        s = pd.Series(values).dropna()
        if len(s) < 3:
            return np.nan
        value = s.autocorr(lag=1)
        return float(value) if pd.notna(value) else np.nan

    autocorr = returns.rolling(window).apply(safe_autocorr)
    rho = 1.0 - autocorr.abs()
    kappa = (beta * D) / (rho + 0.001)

    return pd.DataFrame(
        {
            "close": close,
            "beta": beta,
            "D": D,
            "rho": rho,
            "kappa": kappa,
        }
    )


def latest_diagnostic(data: pd.DataFrame, window: int = 20, trend_period: int = 50) -> dict:
    frame = compute_kappa_frame(data, window=window, trend_period=trend_period)
    valid = frame.replace([np.inf, -np.inf], np.nan).dropna(subset=["kappa", "beta", "D", "rho"])
    if len(valid) < 10:
        raise ValueError("Insufficient valid κ history for diagnostic percentile")

    current = valid.iloc[-1]
    # Critical correction: compare κ with the historical κ distribution, not
    # with a β/volatility threshold expressed in different units.
    threshold = float(valid["kappa"].quantile(0.95))
    score_state = "score_elevated" if float(current["kappa"]) > threshold else "score_nominal"

    return {
        "kappa": float(current["kappa"]),
        "beta": float(current["beta"]),
        "D": float(current["D"]),
        "rho": float(current["rho"]),
        "close": float(current["close"]),
        "historical_kappa_q95": threshold,
        "score_state": score_state,
        "valid_history_rows": int(len(valid)),
    }


@lru_cache(maxsize=128)
def get_historical_data(symbol: str, period: str = "2y"):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        if data is None or data.empty:
            raise ValueError("empty history")
        return data
    except Exception as exc:
        raise HTTPException(status_code=404, detail=f"Symbol/data unavailable: {symbol}: {exc}")


@app.get("/")
async def root():
    return {
        "service": "KappaRisk Research API",
        "version": "1.1.0",
        "status": "research_diagnostic_only",
        "evidence_state": EVIDENCE_STATE,
        "warning": "No investment advice or production trading/predictive claim.",
        "documentation": "/docs",
    }


@app.post("/calculate")
async def calculate_kappa(request: KappaRequest, api_key: dict = Depends(verify_api_key)):
    cache_key = f"{request.symbol}_{request.window}_{request.trend_period}"
    if cache_key in kappa_cache:
        cached_time, cached_result = kappa_cache[cache_key]
        if datetime.now() - cached_time < timedelta(seconds=CACHE_TTL):
            return cached_result

    data = get_historical_data(request.symbol, period="2y")
    if len(data) < max(MIN_HISTORY_ROWS, request.window, request.trend_period):
        raise HTTPException(status_code=400, detail="Insufficient historical data")

    try:
        diag = latest_diagnostic(data, request.window, request.trend_period)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Diagnostic calculation error: {exc}")

    result = {
        "symbol": request.symbol,
        "timestamp": datetime.now().isoformat(),
        "kappa": round(diag["kappa"], 6),
        "components": {
            "beta": round(diag["beta"], 6),
            "D": round(diag["D"], 6),
            "rho": round(diag["rho"], 6),
        },
        "score_state": diag["score_state"],
        "historical_kappa_q95": round(diag["historical_kappa_q95"], 6),
        "valid_history_rows": diag["valid_history_rows"],
        "evidence_state": "SYMBOL_GENERAL_PREDICTIVE_VALIDATION_NOT_ESTABLISHED",
        "interpretation": (
            "Descriptive score percentile only. This endpoint does not predict "
            "future volatility or authorize financial action."
        ),
        "tier": api_key["tier"],
    }

    kappa_cache[cache_key] = (datetime.now(), result)
    return result


@app.get("/status")
async def market_status(api_key: dict = Depends(verify_api_key)):
    symbols = [
        ("^GSPC", "S&P 500"),
        ("^DJI", "Dow Jones"),
        ("^IXIC", "NASDAQ"),
        ("^VIX", "VIX"),
        ("^RUT", "Russell 2000"),
    ]

    markets = []
    for symbol, name in symbols:
        try:
            data = get_historical_data(symbol, period="2y")
            diag = latest_diagnostic(data)
            markets.append(
                {
                    "symbol": symbol,
                    "name": name,
                    "kappa": round(diag["kappa"], 6),
                    "score_state": diag["score_state"],
                    "historical_kappa_q95": round(diag["historical_kappa_q95"], 6),
                    "close": round(diag["close"], 2),
                    "predictive_validation": "NOT_ESTABLISHED",
                }
            )
        except Exception as exc:
            markets.append(
                {
                    "symbol": symbol,
                    "name": name,
                    "score_state": "unavailable",
                    "error": str(exc),
                    "predictive_validation": "NOT_ESTABLISHED",
                }
            )

    return {
        "timestamp": datetime.now().isoformat(),
        "status": "research_diagnostic_only",
        "markets": markets,
        "warning": "Do not interpret score state as investment or risk-management advice.",
    }


@app.post("/subscribe")
async def create_subscription(request: SubscriptionRequest, api_key: dict = Depends(verify_api_key)):
    # Historical endpoint retained for API compatibility. No actual webhook or
    # email delivery is executed by this prototype.
    subscription_id = f"demo_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return {
        "subscription_id": subscription_id,
        "status": "prototype_only_no_delivery",
        "symbols": request.symbols,
        "requested_threshold": request.threshold_value,
        "created_at": datetime.now().isoformat(),
        "warning": "No production alerting or predictive validation is active.",
    }


@app.get("/historical")
async def get_historical(symbol: str, days: int = 30, api_key: dict = Depends(verify_api_key)):
    if days < 1 or days > 730:
        raise HTTPException(status_code=400, detail="days must be between 1 and 730")

    # Always fetch enough warm-up history for the declared 50-day trend and
    # 20-day autocorrelation, then return only the requested tail.
    period = "2y" if days > 365 else "1y"
    data = get_historical_data(symbol, period=period)
    try:
        frame = compute_kappa_frame(data).replace([np.inf, -np.inf], np.nan)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Diagnostic calculation error: {exc}")

    valid = frame.dropna(subset=["kappa", "beta", "D", "rho"])
    tail = valid.tail(days)
    results = [
        {
            "date": idx.strftime("%Y-%m-%d"),
            "kappa": round(float(row.kappa), 6),
            "close": round(float(row.close), 2),
            "beta": round(float(row.beta), 6),
            "D": round(float(row.D), 6),
            "rho": round(float(row.rho), 6),
        }
        for idx, row in tail.iterrows()
    ]

    return {
        "symbol": symbol,
        "data": results,
        "evidence_state": "DESCRIPTIVE_HISTORY_ONLY__SYMBOL_GENERAL_PREDICTIVE_VALIDATION_NOT_ESTABLISHED",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
