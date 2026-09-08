# KappaRisk Validation Platform
## κ-Stability Research and Audit Harness

**Current public status (2026-09-08): historical S&P validation retired; first redesigned run preserved as a procedural failure; corrected one-use successor earned a bounded incremental-content PASS.**

The original March S&P 500 experiment remains reproducible as a historical computation but failed independent methodological audit. A first redesign (`KFIN-V2-20260908-001`) produced promising raw ranking metrics but was itself adjudicated `PROCEDURAL_FAIL` after post-run code review found a protocol/implementation mismatch and insufficient first-terminal enforcement.

A fresh successor, `KFIN-V2_1-20260908-002`, preserved the scientific design while fixing those execution defects. It was reviewed by Codex before merge, executed exactly once by the admitted GitHub Actions workflow, persisted its first receipt durably to live `main`, and returned:

```text
INCREMENTAL_KAPPA_CONTENT_PASS
```

That terminal is deliberately narrow. It means full κ beat the preregistered β-only, persistence, and D/ρ ablation scores on the frozen held-out **average-precision** criterion in this exact finance test. It is not universal κ, financial alpha, investment advice, a causal result, or production readiness.

---

## Current Evidence State

| Domain | Current state | Public claim ceiling |
|---|---|---|
| S&P 500 | March test invalidated; V2 procedural fail preserved; V2.1 bounded incremental-content PASS | Candidate incremental ranking content on one frozen future-volatility test; stronger baselines, uncertainty, repeated holdouts and external reconstruction remain open |
| VIX | Underperforming diagnostic | Not validated |
| Solar | Monitoring / data pipeline | Prediction accuracy not yet validated |
| Neural / EEG | Simulation + literature comparator | Real-data validation pending |
| Crypto | Diagnostic only | Requires leakage/baseline/ablation audit |
| Forex | Not started | No claim |

---

## Historical S&P adverse audit

The March script used the same 20-day rolling-volatility series for β and for construction of the `high_vol` target, with adjacent windows sharing 19/20 observations. It also compared against an inadequate prevalence/random baseline and computed the target threshold on the full sample.

Historical terminal:

```text
REPRODUCIBLE_CODE__CIRCULAR_TARGET__DOMINATED_BY_TRIVIAL_BASELINES__NO_INDEPENDENT_PREDICTIVE_CONTENT_DEMONSTRATED
```

That failure remains immutable.

---

## KFIN-v2 procedural scar

`KFIN-V2-20260908-001` introduced a genuinely future, non-overlapping target and strong comparator structure, but post-run Codex review found that persistence had been implemented with a separately recomputed β q80 instead of the exact frozen target q80 named by the protocol. The two values happened to be numerically equal in that dataset, but frozen methodology is part of the experiment. The same review also found that local receipt writing could overwrite a first result.

Controlling V2 terminal:

```text
PROCEDURAL_FAIL__PERSISTENCE_BASELINE_IMPLEMENTATION_MISMATCH__RAW_RECEIPT_PRESERVED
```

See `adjudications/KFIN-V2-20260908-001.md`.

---

## KFIN-v2.1 valid one-use successor

**Experiment:** `KFIN-V2_1-20260908-002`  
**Protocol:** `VALIDATION_PROTOCOL_V2_1.md`  
**Execution script:** `kappa_validation_v2_1.py`  
**GitHub Actions run:** `34246951669`  
**Execution merge commit:** `b9698649469a36921fc9c0f82190747467bf36cf`  
**Canonical receipt:** `receipts/KFIN-V2_1-20260908-002.json`

The successor added no post-result scientific tuning. Before execution it was hardened so that:

- persistence uses the exact training target q80 threshold;
- only the declared GitHub Actions push-to-main executor is admitted;
- every local terminal receipt is create-only;
- rejected/repeated execution cannot create a second terminal;
- live `main` is queried before analysis for prior identity consumption;
- the first scientific/error terminal is persisted automatically to live `main` before the workflow completes;
- later clean checkouts fail closed after the identity is consumed.

The workflow completed successfully and persisted the first scientific terminal.

### Frozen held-out result

Admitted rows:

- Training: 3,453
- Test: 529
- Positive future-volatility targets: 59
- Test prevalence: 11.15%

| Score | Average precision | ROC-AUC | Precision @ frozen alert | Recall @ frozen alert | F1 |
|---|---:|---:|---:|---:|---:|
| β-only | 0.2383 | **0.6835** | 0.3478 | 0.1356 | 0.1951 |
| β×D (ρ ablated) | 0.3114 | 0.6269 | 0.6429 | 0.1525 | 0.2466 |
| β/ρ (D ablated) | 0.2970 | 0.6732 | 0.3750 | 0.1525 | 0.2169 |
| **κ = βD/ρ** | **0.3859** | 0.6429 | **0.6875** | 0.1864 | 0.2933 |
| Persistence | 0.2200* | — | 0.3898 | **0.3898** | **0.3898** |

`*` Persistence AP uses its frozen binary score.

All five preregistered AP/integrity conditions passed:

- `AP(κ) > AP(β)`
- `AP(κ) > AP(β×D)`
- `AP(κ) > AP(β/ρ)`
- `AP(κ) > AP(persistence)`
- all target/split/threshold integrity checks passed

So the first valid V2.1 terminal is:

```text
INCREMENTAL_KAPPA_CONTENT_PASS
```

The mixed metrics are part of the result, not caveats to hide: β-only had higher ROC-AUC than κ, persistence had higher F1 and recall than κ, and κ recall at its frozen q95 alert threshold was only 18.64%.

---

## Custody

GitHub Actions artifact ID: `10064382539`

- Artifact ZIP SHA-256: `d5bdd3478284ec42f086824899bec1040545a132019daaa853c361499fedc675`
- Scientific receipt SHA-256: `87ef8e803cc0a4e5420b09b4d4a4965608e363429c00dcb15e731fd34f3e3468`
- Console log SHA-256: `2a88c149f92cea163b13fc990a09f4f41c44906d58883385e601418e1dd27014`

The receipt itself records source custody:

- Dataset SHA-256: `30c8b42de4a4cf47b1c67d5117740024ef3a94092df2a0eba0ee906b929d90fc`
- Protocol SHA-256: `afdd7ac526512225e648e9798b353c72099eeb05d3cc95f89a1c1e15bb09399f`
- Script SHA-256: `9df32657be214aa762fbea25a6663c2c7b3c3a3f427c52ba1b00fff184997bfb`

---

## κ Framework

The research framework studies

```text
κ = (β × D) / ρ
```

with domain-specific definitions frozen before testing. Scalar κ remains falsifiable, and richer vector/matrix/operator-valued Return geometry remains admissible when scalar compression loses directional, transient, scale or target information.

---

## Next-proof requirements

A V2.1 PASS does **not** restore broad `validated` language. Before a stronger finance claim, the branch still needs:

1. block/bootstrap uncertainty intervals;
2. multiple independent temporal holdouts and/or prospective data;
3. preregistered conventional volatility comparators such as HAR/GARCH-family models;
4. independent clean-room implementation from the written protocol;
5. external reconstruction of the frozen receipt/custody chain;
6. calibration and decision-utility analysis before any financial-action claim;
7. transaction-cost-aware evaluation if trading utility is ever claimed;
8. preservation of every first failure without retry-to-win.

---

## Public-use / Funding / Legal Guardrail

Do not cite as current evidence:

- the March `100% precision validated` headline;
- the historical `+88.32% improvement` claim;
- the noncontrolling raw V2 PASS.

The strongest currently permitted finance statement is:

> A code-reviewed, preregistered, one-use successor using a non-overlapping future-volatility target produced a bounded incremental-content PASS on its frozen held-out average-precision criterion; stronger conventional baselines, uncertainty analysis, repeated holdouts, and independent reconstruction remain open.

No investment advice, production trading claim, causal claim, universal-κ claim, or cross-domain universality claim is made.

---

**Research principle:** reproduce the number, attack the interpretation, preserve every scar, and make each successor earn its own claim.