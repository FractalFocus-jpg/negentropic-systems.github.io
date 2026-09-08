# Validation Audit Ledger
## Current controlling public audit state

**Last updated:** 2026-09-08  
**Status:** ADVERSE AUDIT INCORPORATED — PUBLIC CLAIM REPAIR IN PROGRESS  
**Governance:** preserve historical outputs; do not preserve invalid interpretations.

---

## 2026-09-08 independent cold audit — S&P 500

**Evidence class:** friendly independent cold run / adverse / non-adjudicative  
**Audited artifacts:** `kappa_analysis.py` + `sp500.csv`

### Positive reproduction

The historical script runs and reproduces the published output:

- Precision: 100.0% (16/16)
- Recall: 25.0% (16/64)

This establishes **computational reproducibility only**.

### Finding A — target circularity

The script defines:

```text
β = returns.rolling(20).std() * sqrt(252)
volatility = returns.rolling(20).std() * sqrt(252)
high_vol = volatility > full-sample 80th percentile
prediction = prior-day κ signal
```

`β` and the target-generating volatility series are identical. With a one-day shift, adjacent feature and label windows share 19/20 daily returns. The test therefore cannot establish independent κ predictive content.

### Finding B — baseline failure

The historical comparison to a prevalence/random baseline is inadequate for an autocorrelated target.

Cold-audit controls:

- Persistence: ~94.9% precision / ~94.9% recall
- β-only: 100% precision / 39.0% recall
- Published κ: 100% precision / ~25–27% recall

β-only strictly dominates the published κ signal at equal precision, and persistence is a much stronger practical baseline than prevalence/random guessing.

### Finding C — target-threshold leakage

The original target threshold used the entire sample, including test data. Future confirmatory tests must estimate all thresholds and normalizers from training data only.

### Correct terminal

```text
REPRODUCIBLE_CODE__CIRCULAR_TARGET__DOMINATED_BY_TRIVIAL_BASELINES__NO_INDEPENDENT_PREDICTIVE_CONTENT_DEMONSTRATED
```

### Scope ceiling

This result applies only to the audited S&P artifact. It does not automatically falsify or validate other domains, physics branches, PDE work, UOS, or a future redesigned κ finance test.

---

## Required passing conditions for finance validation v2

A confirmatory v2 experiment must be frozen before execution and satisfy:

1. **Disjoint future target**: the target window must not overlap the feature window.
2. **Training-only preprocessing**: thresholds, normalizers, hyperparameters, and calibration are learned only from training data.
3. **Strong baselines**: at minimum persistence and β-only; preferably an established volatility-model baseline as well.
4. **Ablation**: dropping D and dropping ρ are measured separately; full κ earns incremental-content credit only if the held-out metric improves over both ablations and β-only.
5. **Frozen split and metrics**: no result-contingent tuning.
6. **First-terminal preservation**: a failed v2 confirmatory run is retained and not retried under the same identity.
7. **Independent reconstruction** before strong public validation language.

The repository now carries `VALIDATION_PROTOCOL_V2.md` and `kappa_validation_v2.py` for this purpose.

---

## Other domains — current conservative states

### VIX

Historical diagnostic underperformed its simple baseline. **NOT VALIDATED.** A redesigned mean-reversion-aware test would require a fresh preregistered identity.

### Solar / NOAA

Live data ingestion/monitoring is useful engineering evidence. Prediction accuracy remains **UNVALIDATED** until a sufficiently long frozen prospective interval closes.

### Neural / EEG

Simulation and literature comparison are not real-data validation. **REAL-DATA VALIDATION PENDING.**

### Crypto

Historical code/data-format repairs do not by themselves establish predictive validity. Any BTC/ETH performance headline must pass the same leakage/baseline/ablation audit before promotion.

### Forex

No completed validation. **NOT STARTED / NO CLAIM.**

---

## Deployment / marketing correction

The earlier recommendation to deploy v1.0 on the strength of the S&P result is retired.

Current public posture:

```text
RESEARCH / AUDIT HARNESS
NOT VALIDATED FINANCIAL ADVICE
NO PRODUCTION PREDICTIVE CLAIM
```

Do not use the retired S&P performance language in proposals, customer materials, investor materials, legal filings, patent prosecution evidence, or licensing discussions.

---

## Historical note

The March 12 audit and deployment recommendation remain recoverable in Git history. Their continued existence is a provenance scar, not current endorsement.

---

**Audit law:** reproducibility is necessary; non-circular targets, strong baselines, ablations, frozen protocols, and independent reconstruction decide whether the interpretation survives.
