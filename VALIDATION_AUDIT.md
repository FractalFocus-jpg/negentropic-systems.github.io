# Validation Audit Ledger
## Current controlling public audit state

**Last updated:** 2026-09-08  
**Status:** HISTORICAL ADVERSE AUDIT PRESERVED + CLEAN SUCCESSOR EXECUTED  
**Current finance successor terminal:** `INCREMENTAL_KAPPA_CONTENT_PASS` — bounded / metric-specific  
**Governance:** preserve historical outputs; never repair a failed interpretation in place.

---

## A. 2026-09-08 independent cold audit — historical S&P experiment

**Evidence class:** friendly independent cold run / adverse / non-adjudicative  
**Audited artifacts:** historical `kappa_analysis.py` + `sp500.csv`

### Positive reproduction

The historical script reproduced:

- Precision: 100.0% (16/16)
- Recall: 25.0% (16/64)

This established computational reproducibility only.

### Finding A1 — target circularity

Historical definitions:

```text
β = returns.rolling(20).std() * sqrt(252)
volatility = returns.rolling(20).std() * sqrt(252)
high_vol = volatility > full-sample 80th percentile
prediction = prior-day κ signal
```

β and the target-generating volatility series were identical, and the one-day shift left 19/20 observations shared across adjacent windows.

### Finding A2 — baseline failure

Cold-audit controls:

- Persistence: ~94.9% precision / ~94.9% recall
- β-only: 100% precision / 39.0% recall
- Published κ: 100% precision / ~25–27% recall

The historical prevalence/random comparison was inadequate, β-only strictly dominated the published κ signal at equal precision, and persistence was a much stronger practical baseline.

### Finding A3 — target-threshold leakage

The historical target threshold used the full sample including the test period.

### Historical terminal — immutable

```text
REPRODUCIBLE_CODE__CIRCULAR_TARGET__DOMINATED_BY_TRIVIAL_BASELINES__NO_INDEPENDENT_PREDICTIVE_CONTENT_DEMONSTRATED
```

This terminal remains true even though a later successor test passed. The successor does not retroactively validate the March design.

---

## B. Clean successor — KFIN-V2-20260908-001

The replacement protocol was frozen before execution in `VALIDATION_PROTOCOL_V2.md`.

### B1. Design corrections

- Non-overlapping future realized-volatility target: t+1..t+20
- Training-only target threshold
- Training-only score thresholds
- Explicit train/test target-window separation
- β-only comparator
- Persistence comparator
- no-ρ ablation: β×D
- no-D ablation: β/ρ
- Full κ: βD/ρ
- Frozen held-out average-precision pass rule
- First-terminal / no-retry rule

### B2. Execution custody

- GitHub Actions run: `34243432146`
- Frozen execution commit: `480933cf6e339dc85dba93edf9bb24e91433c7d5`
- Artifact ID: `10062961206`
- Artifact ZIP SHA-256: `98f51bc17ab6b04a39a1d4dc06832dc5d6ab326abd62b0925d9ce69f1f634bc2`
- Receipt SHA-256: `40f325b1758eeeed465b57c2bdf85465aea591c0af4dd16a4cb3a8a427d8e3de`
- Console SHA-256: `3c0d03629689bef51ab2af2d5ef3e4d92209f53254f733d9f8eb27514a700af1`
- Repository receipt: `receipts/KFIN-V2-20260908-001.json`

### B3. Integrity results

All passed:

- declared feature/target non-overlap;
- feature-date split validity;
- target-end after feature date;
- train targets ending before test start;
- thresholds training-only.

Admitted rows:

- Train: 3,453
- Test: 529
- Positive targets: 59
- Prevalence: 11.15%

### B4. Held-out results

| Score | Average precision | ROC-AUC | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| β | 0.2383 | 0.6835 | 0.3478 | 0.1356 | 0.1951 |
| β×D | 0.3114 | 0.6269 | 0.6429 | 0.1525 | 0.2466 |
| β/ρ | 0.2970 | 0.6732 | 0.3750 | 0.1525 | 0.2169 |
| **κ = βD/ρ** | **0.3859** | 0.6429 | **0.6875** | 0.1864 | 0.2933 |
| Persistence | 0.2200* | — | 0.3898 | 0.3898 | **0.3898** |

`*` Persistence AP uses the frozen binary score.

### B5. First terminal

All preregistered average-precision comparisons and integrity gates passed:

```text
INCREMENTAL_KAPPA_CONTENT_PASS
```

### B6. Claim ceiling

The pass demonstrates bounded incremental ranking content for this exact frozen finance mapping and held-out AP criterion. It does not demonstrate universal κ, causal finance mechanism, general alpha, investment suitability, production readiness, or cross-domain universality.

The metrics are deliberately not summarized as universal dominance:

- β ROC-AUC exceeded κ ROC-AUC: 0.6835 > 0.6429.
- Persistence F1 exceeded κ F1: 0.3898 > 0.2933.
- κ recall at the frozen q95 alert threshold was 18.64%.

---

## C. Public / funding / legal correction state

Retired permanently from the March experiment:

- `100% precision validated`
- `+88.32% improvement vs baseline`
- `Validation: SUCCESS` as evidence of independent κ prediction
- claims that the old hold-out construction by itself prevented leakage/circularity

Permitted current statement:

> A preregistered non-overlapping future-volatility successor produced a bounded incremental-content PASS on its frozen average-precision criterion; stronger conventional baselines, uncertainty analysis, repeated holdouts, and independent reconstruction remain open.

Do not promote the successor beyond that sentence in funding, outreach, legal, investor, licensing or customer materials.

---

## D. Next-proof requirements

1. block/bootstrap uncertainty intervals;
2. multiple independent temporal holdouts and/or prospective data;
3. preregistered HAR/GARCH-family or equivalently strong conventional volatility comparator;
4. independent clean-room implementation from the written protocol;
5. external receipt reconstruction;
6. calibration and decision-utility analysis before any financial-action claim;
7. preserve every first adverse terminal and do not retry-to-win.

---

## E. Other domains

- VIX: underperforming historical diagnostic; not validated.
- Solar: monitoring evidence only; predictive accuracy open.
- Neural/EEG: simulation/literature comparator; real-data validation pending.
- Crypto: diagnostic results require the same leakage/baseline/ablation audit before promotion.
- Forex: no completed validation.

---

**Audit law:** the project improved because the adverse receipt was allowed to break the old claim. The successor earned a new claim under a different design; it did not erase the scar.
