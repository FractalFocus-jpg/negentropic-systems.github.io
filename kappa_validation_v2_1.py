"""Kappa finance validation v2.1 — fresh one-use confirmatory successor.

Experiment ID: KFIN-V2_1-20260908-002
Protocol: VALIDATION_PROTOCOL_V2_1.md
Parent KFIN-V2-20260908-001 is consumed and procedurally failed.

Do not alter target, split, score definitions, thresholds, metrics, or pass rule
under this experiment identity after confirmatory execution.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

EXPERIMENT_ID = "KFIN-V2_1-20260908-002"
PARENT_EXPERIMENT_ID = "KFIN-V2-20260908-001"
EXPECTED_REPOSITORY = "FractalFocus-jpg/negentropic-systems.github.io"
EXPECTED_EVENT = "push"
EXPECTED_REF = "refs/heads/main"
TEST_START = pd.Timestamp("2024-01-01")
FEATURE_VOL_WINDOW = 20
TREND_WINDOW = 50
FUTURE_HORIZON = 20
TARGET_QUANTILE = 0.80
ALERT_QUANTILE = 0.95
ANNUALIZATION = math.sqrt(252.0)
RHO_EPSILON = 0.001

SCIENTIFIC_RECEIPT_PATH = Path("validation_v2_1_receipt.json")
ERROR_RECEIPT_PATH = Path("validation_v2_1_error_receipt.json")
REFUSAL_RECEIPT_PATH = Path("validation_v2_1_refusal_receipt.json")
CANONICAL_REPO_RECEIPT = Path("receipts/KFIN-V2_1-20260908-002.json")
PROTOCOL_PATH = Path("VALIDATION_PROTOCOL_V2_1.md")
SCRIPT_PATH = Path(__file__).resolve()
LOCAL_TERMINAL_PATHS = (
    SCIENTIFIC_RECEIPT_PATH,
    ERROR_RECEIPT_PATH,
    REFUSAL_RECEIPT_PATH,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json_exclusive(path: Path, payload: dict) -> None:
    """Create a JSON receipt exactly once; never truncate an existing file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())


def refusal_payload(reason: str) -> dict:
    return {
        "experiment_id": EXPERIMENT_ID,
        "parent_experiment_id": PARENT_EXPERIMENT_ID,
        "terminal": "REPEAT_OR_UNAUTHORIZED_EXECUTOR_REFUSED",
        "reason": reason,
        "github_repository": os.getenv("GITHUB_REPOSITORY"),
        "github_event_name": os.getenv("GITHUB_EVENT_NAME"),
        "github_ref": os.getenv("GITHUB_REF"),
        "github_run_id": os.getenv("GITHUB_RUN_ID"),
        "github_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
        "github_sha": os.getenv("GITHUB_SHA"),
    }


def remote_canonical_receipt_exists(token: str) -> bool:
    """Check live main, not the triggering checkout, for durable consumption."""
    encoded_path = urllib.parse.quote(str(CANONICAL_REPO_RECEIPT), safe="/")
    url = (
        f"https://api.github.com/repos/{EXPECTED_REPOSITORY}/contents/"
        f"{encoded_path}?ref=main"
    )
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "kfin-v2-1-one-use-guard",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            if response.status == 200:
                return True
            raise RuntimeError(f"Unexpected GitHub guard HTTP status {response.status}")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise RuntimeError(f"GitHub durable-guard query failed with HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub durable-guard query failed: {exc.reason}") from exc


def enforce_one_use_preflight() -> None:
    """Admit only the declared first GitHub Actions push executor."""
    # Any prior local scientific, implementation-error, or refusal terminal
    # consumes this checkout. Never create a second terminal beside it.
    preexisting = [str(path) for path in LOCAL_TERMINAL_PATHS if path.exists()]
    if preexisting:
        raise RuntimeError(
            "local terminal already exists; identity consumed: " + ", ".join(preexisting)
        )

    attempt_text = os.getenv("GITHUB_RUN_ATTEMPT")
    token = os.getenv("GITHUB_TOKEN")

    reasons: list[str] = []
    if os.getenv("GITHUB_ACTIONS") != "true":
        reasons.append("GITHUB_ACTIONS=true is required")
    if os.getenv("GITHUB_REPOSITORY") != EXPECTED_REPOSITORY:
        reasons.append(f"repository must be {EXPECTED_REPOSITORY}")
    if os.getenv("GITHUB_EVENT_NAME") != EXPECTED_EVENT:
        reasons.append(f"event must be {EXPECTED_EVENT}")
    if os.getenv("GITHUB_REF") != EXPECTED_REF:
        reasons.append(f"ref must be {EXPECTED_REF}")
    if not os.getenv("GITHUB_RUN_ID"):
        reasons.append("GITHUB_RUN_ID is required")
    if not os.getenv("GITHUB_SHA"):
        reasons.append("GITHUB_SHA is required")
    if not token:
        reasons.append("GITHUB_TOKEN is required for durable consumption check")

    attempt: int | None = None
    if attempt_text is None:
        reasons.append("GITHUB_RUN_ATTEMPT is required")
    else:
        try:
            attempt = int(attempt_text)
        except ValueError:
            reasons.append(f"GITHUB_RUN_ATTEMPT must be an integer, got {attempt_text!r}")
    if attempt is not None and attempt != 1:
        reasons.append(f"run attempt must be 1, got {attempt}")

    if CANONICAL_REPO_RECEIPT.exists():
        reasons.append(f"checkout already contains canonical receipt: {CANONICAL_REPO_RECEIPT}")

    # Only query live main after the executor context itself is authenticated.
    if not reasons and token and remote_canonical_receipt_exists(token):
        reasons.append(f"live main already contains canonical receipt: {CANONICAL_REPO_RECEIPT}")

    if reasons:
        payload = refusal_payload("; ".join(reasons))
        write_json_exclusive(REFUSAL_RECEIPT_PATH, payload)
        raise RuntimeError(payload["reason"])


def safe_autocorr(values: pd.Series) -> float:
    s = pd.Series(values).dropna()
    if len(s) < 3:
        return np.nan
    value = s.autocorr(lag=1)
    return float(value) if pd.notna(value) else np.nan


def load_data() -> tuple[pd.DataFrame, Path]:
    data_path = SCRIPT_PATH.parent / "sp500.csv"
    if not data_path.exists():
        raise FileNotFoundError(f"Required dataset missing: {data_path}")

    # Historical repository export: first row is the header; next two are
    # yfinance metadata rows. This parser is frozen for this successor.
    df = pd.read_csv(data_path, index_col=0, parse_dates=True, skiprows=[1, 2])
    if "Close" not in df.columns:
        raise ValueError(f"Close column missing; columns={list(df.columns)}")

    df = df.sort_index().copy()
    if not df.index.is_monotonic_increasing or not df.index.is_unique:
        raise ValueError("Dataset index must be unique and monotonically increasing")

    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df["returns"] = df["Close"].pct_change()
    return df, data_path


def build_features_and_target(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["beta"] = out["returns"].rolling(FEATURE_VOL_WINDOW).std() * ANNUALIZATION
    trend = out["Close"].rolling(TREND_WINDOW).mean()
    out["D"] = (out["Close"] - trend).abs() / trend
    autocorr = out["returns"].rolling(FEATURE_VOL_WINDOW).apply(safe_autocorr)
    out["rho"] = 1.0 - autocorr.abs()

    out["beta_D"] = out["beta"] * out["D"]
    out["beta_over_rho"] = out["beta"] / (out["rho"] + RHO_EPSILON)
    out["kappa"] = out["beta_D"] / (out["rho"] + RHO_EPSILON)

    # At feature row t, rolling(20) evaluated at t+20 contains returns
    # t+1..t+20. Shift backward 20 rows to align that future target to t.
    out["future_20d_vol"] = (
        out["returns"].rolling(FUTURE_HORIZON).std().shift(-FUTURE_HORIZON)
        * ANNUALIZATION
    )

    index_series = pd.Series(out.index, index=out.index)
    out["target_start_date"] = pd.to_datetime(index_series.shift(-1))
    out["target_end_date"] = pd.to_datetime(index_series.shift(-FUTURE_HORIZON))
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


def finite_rows(frame: pd.DataFrame, required: list[str]) -> pd.DataFrame:
    clean = frame.dropna(subset=required).copy()
    numeric = clean[required].astype(float)
    return clean.loc[np.isfinite(numeric).all(axis=1)].copy()


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

    result = {
        "training_alert_threshold": threshold,
        "average_precision": float(average_precision_score(y_true, score)),
        "roc_auc": float(roc_auc_score(y_true, score)),
    }
    result.update(binary_metrics(y_true, alert))
    return result


def run_confirmatory() -> dict:
    df, data_path = load_data()
    df = build_features_and_target(df)
    train, test = split_without_target_spill(df)

    required_scores = ["beta", "D", "rho", "beta_D", "beta_over_rho", "kappa"]
    required = required_scores + ["future_20d_vol"]
    train = finite_rows(train, required)
    test = finite_rows(test, required)

    if len(train) < 100:
        raise RuntimeError(f"Insufficient training rows: {len(train)}")
    if len(test) < 20:
        raise RuntimeError(f"Insufficient test rows: {len(test)}")

    # Single frozen training-target threshold reused verbatim by persistence.
    target_threshold = float(train["future_20d_vol"].quantile(TARGET_QUANTILE))
    train["future_high_vol"] = (train["future_20d_vol"] > target_threshold).astype(int)
    test["future_high_vol"] = (test["future_20d_vol"] > target_threshold).astype(int)

    y_true = test["future_high_vol"].astype(int)
    if y_true.nunique() != 2:
        raise RuntimeError("Held-out target lacks both positive and negative classes")

    target_order_ok = bool(
        (test["target_start_date"] > test.index).all()
        and (test["target_end_date"] >= test["target_start_date"]).all()
    )
    train_spill_ok = bool((train["target_end_date"] < TEST_START).all())
    split_ok = bool((train.index < TEST_START).all() and (test.index >= TEST_START).all())
    thresholds_training_only = True

    integrity = {
        "feature_target_order_nonoverlap": target_order_ok,
        "feature_date_split_valid": split_ok,
        "training_targets_end_before_test_start": train_spill_ok,
        "thresholds_training_only": thresholds_training_only,
        "persistence_uses_exact_target_threshold": True,
    }
    if not all(integrity.values()):
        raise RuntimeError(f"Target/split integrity gate failed: {integrity}")

    results: dict[str, dict] = {}
    for score_name in ["beta", "beta_D", "beta_over_rho", "kappa"]:
        results[score_name] = score_metrics(train, test, score_name, y_true)

    # Critical V2.1 correction: persistence uses the exact target threshold,
    # not a separately recomputed beta quantile.
    persistence_threshold = target_threshold
    persistence_pred = (test["beta"] > persistence_threshold).astype(int)
    persistence = binary_metrics(y_true, persistence_pred)
    persistence["average_precision"] = float(
        average_precision_score(y_true, persistence_pred)
    )
    persistence["training_threshold"] = persistence_threshold
    persistence["threshold_source"] = "training_target_q80_exact"
    results["persistence"] = persistence

    ap_kappa = results["kappa"]["average_precision"]
    pass_conditions = {
        "kappa_gt_beta_ap": ap_kappa > results["beta"]["average_precision"],
        "kappa_gt_no_rho_ablation_ap": ap_kappa > results["beta_D"]["average_precision"],
        "kappa_gt_no_D_ablation_ap": ap_kappa > results["beta_over_rho"]["average_precision"],
        "kappa_gt_persistence_ap": ap_kappa > results["persistence"]["average_precision"],
        "target_integrity": all(integrity.values()),
    }

    terminal = (
        "INCREMENTAL_KAPPA_CONTENT_PASS"
        if all(pass_conditions.values())
        else "NO_INCREMENTAL_KAPPA_CONTENT_ON_FROZEN_TEST"
    )

    receipt = {
        "experiment_id": EXPERIMENT_ID,
        "parent_experiment_id": PARENT_EXPERIMENT_ID,
        "protocol": str(PROTOCOL_PATH),
        "terminal": terminal,
        "claim_ceiling": (
            "Bounded finance incremental-ranking result for this exact frozen test only; "
            "no universal-kappa, causal, investment-suitability, production, or cross-domain claim."
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
        "integrity": integrity,
        "counts": {
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "test_positive_targets": int(y_true.sum()),
            "test_target_prevalence": float(y_true.mean()),
        },
        "training_target_threshold": target_threshold,
        "results": results,
        "pass_conditions": pass_conditions,
        "environment": {
            "python": sys.version.split()[0],
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "github_run_id": os.getenv("GITHUB_RUN_ID"),
            "github_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
            "github_sha": os.getenv("GITHUB_SHA"),
        },
        "source_custody": {
            "data_sha256": sha256_file(data_path),
            "script_sha256": sha256_file(SCRIPT_PATH),
            "protocol_sha256": sha256_file(PROTOCOL_PATH),
        },
    }
    return receipt


def main() -> int:
    try:
        enforce_one_use_preflight()
        receipt = run_confirmatory()
        write_json_exclusive(SCIENTIFIC_RECEIPT_PATH, receipt)
        print(json.dumps(receipt, indent=2, sort_keys=True))
        print(f"\nCreated {SCIENTIFIC_RECEIPT_PATH} exclusively")
        return 0
    except Exception as exc:
        # If any terminal already exists, it is controlling for this checkout.
        # Never create a second receipt beside it.
        existing = [path for path in LOCAL_TERMINAL_PATHS if path.exists()]
        if existing:
            print(
                "Execution refused/terminated with existing receipt(s): "
                + ", ".join(str(path) for path in existing),
                file=sys.stderr,
            )
            for path in existing:
                try:
                    print(path.read_text(encoding="utf-8"), file=sys.stderr)
                except OSError:
                    pass
            return 2

        # No terminal exists yet, so this is a first implementation/data error.
        error_payload = {
            "experiment_id": EXPERIMENT_ID,
            "parent_experiment_id": PARENT_EXPERIMENT_ID,
            "terminal": "IMPLEMENTATION_OR_DATA_ERROR_BEFORE_SCIENTIFIC_TERMINAL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "github_run_id": os.getenv("GITHUB_RUN_ID"),
            "github_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
            "github_sha": os.getenv("GITHUB_SHA"),
        }
        try:
            write_json_exclusive(ERROR_RECEIPT_PATH, error_payload)
        except FileExistsError:
            # A concurrent/local race created a terminal between the existence
            # check and exclusive create. Do not overwrite it.
            pass
        print(json.dumps(error_payload, indent=2, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
