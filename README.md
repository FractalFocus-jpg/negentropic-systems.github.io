# KappaRisk Validation Platform
## κ-Stability Research and Audit Harness

**Current public status (2026-09-08): historical S&P validation claim retired; clean v2 incremental-content test executed with a bounded PASS.**

The original March S&P 500 experiment remains reproducible as code, but its validation interpretation was invalidated by a 2026-09-08 independent cold audit that found target circularity, weak baselines, and target-threshold leakage. That historical claim remains retired.

A new preregistered successor, `KFIN-V2-20260908-001`, was then frozen **before execution** and run on GitHub Actions with a non-overlapping 20-day future-volatility target, training-only thresholds, persistence and β-only baselines, D/ρ ablations, and an explicit first-terminal rule. It returned:

```text
INCREMENTAL_KAPPA_CONTENT_PASS
```

This means only that full κ beat the preregistered comparison scores on the protocol's held-out **average-precision** criterion. It is not a universal-κ result, financial-alpha proof, investment recommendation, causal result, or production-readiness claim.

---

## Current Evidence State

| Domain | Current state | Public claim ceiling |
|---|---|---|
| S&P 500 | Historical test invalidated; KFIN-v2 bounded incremental-content PASS | Candidate incremental finance signal; external reconstruction and stronger baselines still required |
| VIX | Underperforming diagnostic | Not validated |
| Solar | Monitoring / data pipeline | Prediction accuracy not yet validated |
| Neural / EEG | Simulation + literature comparator | Real-data validation pending |
| Crypto | Diagnostic only | Requires leakage/baseline/ablation audit |
| Forex | Not started | No claim |

---

## Why the historical claim was retired

The March script used:

- `β` = 20-day annualized rolling volatility
- target `high_vol` = the same 20-day annualized rolling volatility thresholded at the 80th percentile
- prediction = previous-day κ signal

Adjacent feature/target windows therefore shared 19 of 20 observations. The computation reproduced, but the test did not isolate independent κ information.

Cold-audit controls on that historical test reported:

- Persistence: ~94.9% precision / ~94.9% recall
- β-only: 100% precision / 39.0% recall
- Published κ: 100% precision / ~25–27% recall

Historical terminal:

```text
REPRODUCIBLE_CODE__CIRCULAR_TARGET__DOMINATED_BY_TRIVIAL_BASELINES__NO_INDEPENDENT_PREDICTIVE_CONTENT_DEMONSTRATED
```

---

## KFIN-v2 first confirmatory receipt

**Experiment:** `KFIN-V2-20260908-001`  
**GitHub Actions run:** `34243432146`  
**Frozen execution commit:** `480933cf6e339dc85dba93edf9bb24e91433c7d5`  
**Receipt:** `receipts/KFIN-V2-20260908-001.json`

Admitted rows:

- Training: 3,453
- Held-out test: 529
- Positive future-volatility targets: 59
- Test prevalence: 11.15%

Held-out average precision:

| Score | Average precision |
|---|---:|
| β-only | 0.2383 |
| β × D (ρ ablated) | 0.3114 |
| β / ρ (D ablated) | 0.2970 |
| **κ = βD/ρ** | **0.3859** |
| Persistence | 0.2200 |

All five preregistered pass conditions were true: κ exceeded β-only, both ablations, and persistence on average precision, while target/split integrity checks passed.

At the frozen q95 alert threshold, κ produced:

- Precision: 68.75%
- Recall: 18.64%
- F1: 0.2933
- Alert rate: 3.02%

The result is **metric-specific rather than globally dominant**: β-only had higher ROC-AUC (0.6835 vs κ 0.6429), and persistence had higher F1 (0.3898 vs κ 0.2933). Those facts are preserved rather than hidden.

---

## κ Framework

The research framework studies

```text
κ = (β × D) / ρ
```

where domain-specific meanings of amplification `β`, drift/disorder `D`, and return/repair capacity `ρ` must be frozen before validation. Scalar κ remains falsifiable; richer vector/matrix/operator-valued Return geometry remains admissible where scalar compression loses directional, transient, or target information.

---

## Validation standard from here

Before stronger public validation language, the finance branch still requires:

1. block/bootstrap uncertainty intervals;
2. multiple independent temporal holdouts or prospective data;
3. stronger conventional volatility baselines such as a preregistered HAR/GARCH-family comparator;
4. independent implementation from `VALIDATION_PROTOCOL_V2.md`;
5. external reconstruction of the frozen receipt;
6. transaction-cost / decision analysis only if financial action is later claimed;
7. no retry-to-win under consumed experiment identities.

See:

- `VALIDATION_PROTOCOL_V2.md`
- `kappa_validation_v2.py`
- `VALIDATION_AUDIT.md`
- `RESULTS.md`
- `receipts/KFIN-V2-20260908-001.json`

---

## Public-use / Funding / Legal Guardrail

Do **not** cite the retired historical `100% precision`, `+88.32% improvement`, or March `validated` language as current evidence.

The strongest current public finance statement is narrower:

> A preregistered non-overlapping future-volatility test produced a bounded incremental-content PASS on its frozen average-precision criterion; stronger conventional baselines, uncertainty analysis, repeated holdouts, and independent reconstruction remain open.

No investment advice or production trading claim is made.

---

## Contact

Alexander Liantonio

---

**Research principle:** reproduce the number, attack the interpretation, preserve the scar, and let the successor earn its own claim.
