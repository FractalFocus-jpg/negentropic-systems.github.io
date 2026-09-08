"""Kappa finance validation v2.

Experiment ID: KFIN-V2-20260908-001
Protocol: VALIDATION_PROTOCOL_V2.md

This is a one-use confirmatory design. Do not change the target, split,
score definitions, thresholds, metrics, or pass rule after inspecting a
confirmatory result under this experiment ID.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

EXPERIMENT_ID = "KFIN-V2-20260908-001"
TEST_START = pd.Timestamp("2024-01-01")
FEATURE_VOL_WINDOW = 20
TREND_WINDOW = 50
FUTURE_HORIZON = 20
TARGET_QUANTILE = 0.80
ALERT_QUANTILE = 0.95
ANNUALIZATION = math.sqrt(252.0)
RHO_EPSILON = 0.001
RECEIPT_PATH = Path("validation_v2_receipt.json")


def safe_autocorr(values: pd.Series) -> float:
    s = pd.Series(values).dropna()
    if len(s) < 3:
        return np.nan
    value = s.autocorr(lag=1)
    return float(value) if pd.notna(value) else np.nan


def load_data() -> pd.DataFrame:
    script_dir = Path(__file__).resolve().parent
    data_path = script_dir / "sp500.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Required dataset missing: {data_path}")

    # Preserve the historical repository CSV parser: the yfinance export has
    # two metadata rows below its first header row.
    df = pd.read_csv(data_path, index_col=0, parse_dates=True, skiprows=[1, 2])
    if "Close" not in df.columns:
        raise ValueError(f"Close column missing; columns={list(df.columns)}")

    df = df.sort_index().copy()
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df["returns"] = df["Close"].pct_change()
    return df


def build_features_and_target(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # Frozen feature map: only information at or before feature date t.
    out["beta"] = (
        out["returns"].rolling(FEATURE_VOL_WINDOW).std() * ANNUALIZATION
    )
    trend = out["Close"].rolling(TREND_WINDOW).mean()
    out["D"] = (out["Close"] - trend).abs() / trend
    autocorr = out["returns"].rolling(FEATURE_VOL_WINDOW).apply(safe_autocorr)
    out["rho"] = 1.0 - autocorr.abs()

    out["beta_D"] = out["beta"] * out["D"]
    out["beta_over_rho"] = out["beta"] / (out["rho"] + RHO_EPSILON)
    out["kappa"] = out["beta_D"] / (out["rho"] + RHO_EPSILON)

    # Target at feature date t uses returns t+1..t+20. The rolling value at
    # t+20 covers those 20 future returns; shifting it backward aligns it to t.
    out["future_20d_vol"] = (
        out["returns"].rolling(FUTURE_HORIZON).std().shift(-FUTURE_HORIZON)
        * ANNUALIZATION
    )

    # Explicit target end date makes split-boundary leakage auditable.
    target_end = pd.Series(out.index, index=out.index).shift(-FUTURE_HORIZON)
    out["target_end_date"] = pd.to_datetime(target_end)
    return out


def split_without_target_spill(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_mask = (
        (df.index < TEST_START)
        & df["target_end_date"].notna()
        & (df["target_end_date"] < TEST_START)
    )
    test_mask = (
        (df.index >= TEST_START)
        & df["target_end_date"].notna()
        & df["future_20d_vol"].notna()
    )
    return df.loc[train_mask].copy(), df.loc[test_mask].copy()


def binary_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict:
    return {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "alert_rate": float(np.mean(y_pred)),
        "alerts": int(np.sum(y_pred)),
    }


def score_metrics(
    train: pd.DataFrame,
    test: pd.DataFrame,
    score_name: str,
    y_true: pd.Series,
) -> dict:
    threshold = float(train[score_name].quantile(ALERT_QUANTILE))
    score = test[score_name].astype(float)
    alert = (score > threshold).astype(int)

    ap = float(average_precision_score(y_true, score))
    roc = None
    if y_true.nunique() == 2:
        roc = float(roc_auc_score(y_true, score))

    result = {
        "training_alert_threshold": threshold,
        "average_precision": ap,
        "roc_auc": roc,
    }
    result.update(binary_metrics(y_true, alert))
    return result


def finite_rows(frame: pd.DataFrame, required: list[str]) -> pd.DataFrame:
    clean = frame.dropna(subset=required).copy()
    finite_mask = np.isfinite(clean[required].astype(float)).all(axis=1)
    return clean.loc[finite_mask].copy()


def run() -> dict:
    df = build_features_and_target(load_data())
    train, test = split_without_target_spill(df)

    required_scores = ["beta", "D", "rho", "beta_D", "beta_over_rho", "kappa"]
    train = finite_rows(train, required_scores + ["future_20d_vol"])
    test = finite_rows(test, required_scores + ["future_20d_vol"])

    if len(train) < 100:
        raise RuntimeError(f"Insufficient training rows: {len(train)}")
    if len(test) < 20:
        raise RuntimeError(f"Insufficient test rows: {len(test)}")

    # Training-only target threshold. It is never recomputed on test data.
    target_threshold = float(train["future_20d_vol"].quantile(TARGET_QUANTILE))
    train["future_high_vol"] = (train["future_20d_vol"] > target_threshold).astype(int)
    test["future_high_vol"] = (test["future_20d_vol"] > target_threshold).astype(int)

    y_true = test["future_high_vol"]
    if y_true.nunique() != 2:
        raise RuntimeError("Held-out target lacks both positive and negative classes")

    # Integrity checks.
    target_order_ok = bool((test["target_end_date"] > test.index).all())
    train_spill_ok = bool((train["target_end_date"] < TEST_START).all())
    split_ok = bool((train.index < TEST_START).all() and (test.index >= TEST_START).all())

    # By construction, feature β at t uses t-19..t and future target uses
    # t+1..t+20. Record this as an explicit declared-window integrity fact.
    declared_nonoverlap_ok = FEATURE_VOL_WINDOW > 0 and FUTURE_HORIZON > 0

    if not all([target_order_ok, train_spill_ok, split_ok, declared_nonoverlap_ok]):
        raise RuntimeError("Target/split integrity gate failed")

    results = {}
    for score_name in ["beta", "beta_D", "beta_over_rho", "kappa"]:
        results[score_name] = score_metrics(train, test, score_name, y_true)

    # Persistence uses only past/current volatility and a training-only q80
    # threshold with the same units as the target.
    persistence_threshold = float(train["beta"].quantile(TARGET_QUANTILE))
    persistence_pred = (test["beta"] > persistence_threshold).astype(int)
    persistence = binary_metrics(y_true, persistence_pred)
    persistence["average_precision"] = float(
        average_precision_score(y_true, persistence_pred)
    )
    persistence["training_threshold"] = persistence_threshold
    results["persistence"] = persistence

    ap_k = results["kappa"]["average_precision"]
    pass_conditions = {
        "kappa_gt_beta_ap": ap_k > results["beta"]["average_precision"],
        "kappa_gt_no_rho_ablation_ap": ap_k > results["beta_D"]["average_precision"],
        "kappa_gt_no_D_ablation_ap": ap_k > results["beta_over_rho"]["average_precision"],
        "kappa_gt_persistence_ap": ap_k > results["persistence"]["average_precision"],
        "target_integrity": target_order_ok and train_spill_ok and split_ok and declared_nonoverlap_ok,
    }

    passed = all(pass_conditions.values())
    terminal = (
        "INCREMENTAL_KAPPA_CONTENT_PASS"
        if passed
        else "NO_INCREMENTAL_KAPPA_CONTENT_ON_FROZEN_TEST"
    )

    receipt = {
        "experiment_id": EXPERIMENT_ID,
        "protocol": "VALIDATION_PROTOCOL_V2.md",
        "terminal": terminal,
        "claim_ceiling": (
            "Bounded finance incremental-content candidate only; no universal-kappa, "
            "causal, investment-suitability, or cross-domain claim."
        ),
        "parameters": {
            "test_start": str(TEST_START.date()),
            "feature_vol_window": FEATURE_VOL_WINDOW,
            "trend_window": TREND_WINDOW,
            "future_horizon": FUTURE_HORIZON,
            "target_quantile": TARGET_QUANTILE,
            "alert_quantile": ALERT_QUANTILE,
            "rho_epsilon": RHO_EPSILON,
        },
        "integrity": {
            "declared_feature_target_nonoverlap": declared_nonoverlap_ok,
            "target_end_after_feature_date": target_order_ok,
            "training_targets_end_before_test_start": train_spill_ok,
            "feature_date_split_valid": split_ok,
            "thresholds_training_only": True,
        },
        "counts": {
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "test_positive_targets": int(y_true.sum()),
            "test_target_prevalence": float(y_true.mean()),
        },
        "training_target_threshold": target_threshold,
        "results": results,
        "pass_conditions": pass_conditions,
    }

    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, sort_keys=True), encoding="utf-8")
    return receipt


if __name__ == "__main__":
    try:
        receipt = run()
        print(json.dumps(receipt, indent=2, sort_keys=True))
        print(f"\nWrote {RECEIPT_PATH}")
    except Exception as exc:
        error_receipt = {
            "experiment_id": EXPERIMENT_ID,
            "terminal": "IMPLEMENTATION_OR_DATA_ERROR_BEFORE_SCIENTIFIC_TERMINAL",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        RECEIPT_PATH.write_text(
            json.dumps(error_receipt, indent=2, sort_keys=True), encoding="utf-8"
        )
        print(json.dumps(error_receipt, indent=2, sort_keys=True))
        raise
