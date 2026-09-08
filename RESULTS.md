# κ-Framework Validation Results
## Current Evidence State — corrected and re-tested 2026-09-08

**Historical experiment date:** 2026-03-12  
**Independent adverse audit:** 2026-09-08  
**Clean successor experiment:** `KFIN-V2-20260908-001`  
**Current finance terminal:** `INCREMENTAL_KAPPA_CONTENT_PASS` — bounded, metric-specific

---

## 1. Historical S&P computation — preserved but invalidated as validation

The original `kappa_analysis.py` run reproducibly returned:

- Precision: 100% (16/16 alerts correct)
- Recall: 25% (16/64 labeled events caught)

The 2026-09-08 cold audit found target circularity, an inadequate prevalence/random baseline, and full-sample target-threshold leakage. Historical terminal:

```text
REPRODUCIBLE_CODE__CIRCULAR_TARGET__DOMINATED_BY_TRIVIAL_BASELINES__NO_INDEPENDENT_PREDICTIVE_CONTENT_DEMONSTRATED
```

This historical failure remains immutable.

---

## 2. Clean KFIN-v2 successor — executed once

The successor protocol was frozen before execution in `VALIDATION_PROTOCOL_V2.md` and used:

- feature β: past 20-day annualized volatility;
- D: price deviation from past 50-day moving average;
- ρ: one minus absolute lag-1 autocorrelation over past 20 returns;
- target: realized volatility over **future, non-overlapping days t+1..t+20**;
- target threshold: training-only q80;
- score alert thresholds: training-only q95;
- held-out feature dates beginning 2024-01-01;
- persistence, β-only, β×D, β/ρ and full κ comparators;
- first-terminal / no-retry rule.

GitHub Actions run `34243432146` executed against commit `480933cf6e339dc85dba93edf9bb24e91433c7d5` and completed successfully.

### Integrity gates

All were true:

- declared feature/target non-overlap;
- target end after feature date;
- train target windows end before test start;
- feature-date split valid;
- thresholds training-only.

Counts:

- Training rows: 3,453
- Test rows: 529
- Positive test targets: 59
- Test prevalence: 0.1115

---

## 3. Held-out results

| Score | Average precision | ROC-AUC | Precision @ frozen alert | Recall @ frozen alert | F1 |
|---|---:|---:|---:|---:|---:|
| β | 0.2383 | 0.6835 | 0.3478 | 0.1356 | 0.1951 |
| β×D (ρ ablated) | 0.3114 | 0.6269 | 0.6429 | 0.1525 | 0.2466 |
| β/ρ (D ablated) | 0.2970 | 0.6732 | 0.3750 | 0.1525 | 0.2169 |
| **κ = βD/ρ** | **0.3859** | 0.6429 | **0.6875** | 0.1864 | 0.2933 |
| Persistence | 0.2200* | — | 0.3898 | 0.3898 | **0.3898** |

`*` Persistence average precision uses its frozen binary score.

### Preregistered pass conditions

All five passed:

- `AP(kappa) > AP(beta)`
- `AP(kappa) > AP(beta_D)`
- `AP(kappa) > AP(beta_over_rho)`
- `AP(kappa) > AP(persistence)`
- target/split integrity PASS

Therefore the first terminal is:

```text
INCREMENTAL_KAPPA_CONTENT_PASS
```

---

## 4. What the PASS means — and does not mean

It means the full κ score carried more held-out ranking information than β-only, persistence and either single-component ablation **on the frozen average-precision criterion in this exact experiment**.

It does **not** mean κ dominated every metric. Important counterweights are preserved:

- β had higher ROC-AUC than κ: 0.6835 vs 0.6429.
- Persistence had higher F1 than κ: 0.3898 vs 0.2933.
- κ recall at the frozen q95 alert threshold was only 18.64%.

So the result is a bounded incremental-content candidate, not a production or universal-finance result.

---

## 5. Custody

Frozen receipt: `receipts/KFIN-V2-20260908-001.json`

- Workflow run ID: `34243432146`
- Frozen execution commit: `480933cf6e339dc85dba93edf9bb24e91433c7d5`
- GitHub artifact ID: `10062961206`
- Artifact ZIP SHA-256: `98f51bc17ab6b04a39a1d4dc06832dc5d6ab326abd62b0925d9ce69f1f634bc2`
- Receipt SHA-256: `40f325b1758eeeed465b57c2bdf85465aea591c0af4dd16a4cb3a8a427d8e3de`
- Console SHA-256: `3c0d03629689bef51ab2af2d5ef3e4d92209f53254f733d9f8eb27514a700af1`

---

## 6. Next-proof roadmap

No strong `validated` headline returns yet. Required next steps:

1. block/bootstrap uncertainty intervals;
2. independent temporal holdouts and/or prospective data;
3. preregistered conventional HAR/GARCH-family comparator;
4. independent clean-room implementation from the written protocol;
5. external reconstruction of this receipt;
6. calibration / decision-utility study before any operational financial claim;
7. preserve every first failure without retry-to-win.

---

## 7. Public claim ceiling

Permitted:

> A preregistered non-overlapping future-volatility successor produced a bounded incremental-content PASS on its frozen average-precision criterion.

Not permitted from this result alone:

- universal κ;
- general financial alpha;
- investment suitability;
- causal mechanism;
- production readiness;
- cross-domain universality.

---

**Governing rule:** the adverse audit was not erased by the successor PASS. The broken experiment remains broken; the successor earned a new, narrower result under a new design.
