#!/usr/bin/env python3
"""
KappaRisk API Server
FastAPI implementation of κ-stability analytics

Run: uvicorn api_server:app --reload
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import json
import asyncio
from functools import lru_cache

app = FastAPI(
    title="KappaRisk API",
    description="Real-time κ-stability analytics for financial markets",
    version="1.0.0"
)

security = HTTPBearer()

# Simple in-memory API key storage (replace with database in production)
API_KEYS = {
    "test_key_123": {"tier": "free", "requests": 0, "limit": 100},
    "pro_key_456": {"tier": "pro", "requests": 0, "limit": 10000},
}

# Cache for calculated kappa values
kappa_cache = {}
CACHE_TTL = 300  # 5 minutes

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

class AlertResponse(BaseModel):
    symbol: str
    timestamp: datetime
    kappa: float
    status: str
    message: str

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    key_data = API_KEYS[token]
    if key_data["requests"] >= key_data["limit"]:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    key_data["requests"] += 1
    return key_data

def compute_kappa(data, window=20, trend_period=50):
    """Calculate κ-stability metric"""
    try:
        # Calculate returns
        data['returns'] = data['Close'].pct_change()
        
        # Beta: rolling volatility (annualized)
        beta = data['returns'].rolling(window).std() * np.sqrt(252)
        
        # D: deviation from trend
        trend = data['Close'].rolling(trend_period).mean()
        D = abs(data['Close'] - trend) / trend
        
        # Rho: mean reversion strength
        def safe_autocorr(x):
            if len(x) < 2:
                return 0
            try:
                return x.autocorr(lag=1)
            except:
                return 0
        
        autocorr = data['returns'].rolling(window).apply(safe_autocorr)
        rho = 1 - abs(autocorr)
        
        # Kappa calculation
        kappa = (beta * D) / (rho + 0.001)
        
        return kappa.iloc[-1], beta.iloc[-1], D.iloc[-1], rho.iloc[-1]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@lru_cache(maxsize=128)
def get_historical_data(symbol: str, period: str = "1y"):
    """Fetch and cache historical data"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Symbol not found: {symbol}")

@app.get("/")
async def root():
    return {
        "service": "KappaRisk API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs"
    }

@app.post("/calculate")
async def calculate_kappa(
    request: KappaRequest,
    api_key: dict = Depends(verify_api_key)
):
    """Calculate κ for a specific symbol"""
    
    # Check cache
    cache_key = f"{request.symbol}_{request.window}_{request.trend_period}"
    if cache_key in kappa_cache:
        cached_time, cached_result = kappa_cache[cache_key]
        if datetime.now() - cached_time < timedelta(seconds=CACHE_TTL):
            return cached_result
    
    # Fetch data
    data = get_historical_data(request.symbol)
    
    if len(data) < request.window + request.trend_period:
        raise HTTPException(status_code=400, detail="Insufficient historical data")
    
    # Calculate kappa
    kappa, beta, D, rho = compute_kappa(data, request.window, request.trend_period)
    
    # Determine threshold and status
    kappa_series = data['Close'].pct_change().rolling(request.window).std() * np.sqrt(252)
    threshold = kappa_series.quantile(0.95)
    
    if np.isnan(kappa):
        status = "unknown"
    elif kappa > threshold:
        status = "elevated"
    else:
        status = "stable"
    
    result = {
        "symbol": request.symbol,
        "timestamp": datetime.now().isoformat(),
        "kappa": round(kappa, 4) if not np.isnan(kappa) else None,
        "components": {
            "beta": round(beta, 4) if not np.isnan(beta) else None,
            "D": round(D, 4) if not np.isnan(D) else None,
            "rho": round(rho, 4) if not np.isnan(rho) else None
        },
        "status": status,
        "threshold": round(threshold, 4),
        "tier": api_key["tier"]
    }
    
    # Cache result
    kappa_cache[cache_key] = (datetime.now(), result)
    
    return result

@app.get("/status")
async def market_status(api_key: dict = Depends(verify_api_key)):
    """Get current status of major markets"""
    
    symbols = [
        ("^GSPC", "S&P 500"),
        ("^DJI", "Dow Jones"),
        ("^IXIC", "NASDAQ"),
        ("^VIX", "VIX"),
        ("^RUT", "Russell 2000")
    ]
    
    markets = []
    for symbol, name in symbols:
        try:
            data = get_historical_data(symbol, period="5d")
            kappa, _, _, _ = compute_kappa(data)
            
            # Determine status
            kappa_series = data['Close'].pct_change().rolling(20).std() * np.sqrt(252)
            threshold = kappa_series.quantile(0.95)
            
            status = "elevated" if kappa > threshold else "stable"
            
            markets.append({
                "symbol": symbol,
                "name": name,
                "kappa": round(kappa, 4) if not np.isnan(kappa) else None,
                "status": status,
                "close": round(data['Close'].iloc[-1], 2)
            })
        except:
            continue
    
    return {
        "timestamp": datetime.now().isoformat(),
        "markets": markets
    }

@app.post("/subscribe")
async def create_subscription(
    request: SubscriptionRequest,
    api_key: dict = Depends(verify_api_key)
):
    """Create alert subscription"""
    
    # In production: save to database
    subscription_id = f"sub_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "subscription_id": subscription_id,
        "status": "active",
        "symbols": request.symbols,
        "threshold": request.threshold_value,
        "created_at": datetime.now().isoformat()
    }

@app.get("/historical")
async def get_historical(
    symbol: str,
    days: int = 30,
    api_key: dict = Depends(verify_api_key)
):
    """Get historical κ values"""
    
    data = get_historical_data(symbol, period=f"{days}d")
    
    # Calculate kappa for each day
    results = []
    for i in range(len(data)):
        if i < 50:  # Skip until we have enough data
            continue
        
        window_data = data.iloc[:i+1]
        kappa, beta, D, rho = compute_kappa(window_data)
        
        results.append({
            "date": data.index[i].strftime("%Y-%m-%d"),
            "kappa": round(kappa, 4) if not np.isnan(kappa) else None,
            "close": round(data['Close'].iloc[i], 2),
            "beta": round(beta, 4) if not np.isnan(beta) else None,
            "D": round(D, 4) if not np.isnan(D) else None,
            "rho": round(rho, 4) if not np.isnan(rho) else None
        })
    
    return {
        "symbol": symbol,
        "data": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
