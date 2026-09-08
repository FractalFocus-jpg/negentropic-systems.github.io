# KappaRisk Validation Platform
## κ-Stability Research and Audit Harness

**Current public status (2026-09-08): historical S&P validation retired; first clean-successor run preserved but adjudicated PROCEDURAL FAIL; corrected successor pending.**

The original March S&P experiment is reproducible as code but invalid as a validation claim because of target circularity, weak baselines, and target-threshold leakage.

A first redesigned successor, `KFIN-V2-20260908-001`, was preregistered and executed once. Its raw workflow output satisfied the declared average-precision comparisons, but post-run Codex review found that the implementation did not literally use the frozen persistence threshold specified in the protocol and that local receipt writing was not overwrite-safe. Under the project's first-terminal law, the raw PASS is therefore **noncontrolling**.

Controlling terminal:

```text
PROCEDURAL_FAIL__PERSISTENCE_BASELINE_IMPLEMENTATION_MISMATCH__RAW_RECEIPT_PRESERVED
```

The fresh corrected successor is `KFIN-V2_1-20260908-002`. It must be code-reviewed before execution and may not rewrite or rerun the consumed V2 identity.

---

## Current Evidence State

| Domain | Current state | Public claim ceiling |
|---|---|---|
| S&P 500 | Historical test invalidated; KFIN-v2 raw result procedurally invalid; V2.1 pending | No current validated κ finance claim |
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

## KFIN-v2 raw run — preserved, not promoted

**Experiment:** `KFIN-V2-20260908-001`  
**Workflow run:** `34243432146`  
**Execution commit:** `480933cf6e339dc85dba93edf9bb24e91433c7d5`  
**Raw receipt:** `receipts/KFIN-V2-20260908-001.json`  
**Adjudication:** `adjudications/KFIN-V2-20260908-001.md`

The raw run used a non-overlapping future-volatility target and training-only thresholds. Its raw average-precision values were:

| Score | Average precision |
|---|---:|
| β-only | 0.2383 |
| β×D | 0.3114 |
| β/ρ | 0.2970 |
| κ = βD/ρ | 0.3859 |
| Persistence | 0.2200 |

However, post-run code review found that persistence was implemented using `train["beta"].quantile(0.8)` rather than the exact frozen `target_threshold` named by the protocol. In this dataset the two thresholds happened to be numerically equal (`0.19696579040212642`), so the raw metrics do not change numerically; the procedural mismatch still invalidates the claimed confirmatory terminal.

Codex also found that `Path.write_text` could overwrite a first receipt on local repeated execution. The GitHub artifact itself remains preserved, but the successor must use exclusive receipt creation and rerun refusal.

---

## κ Framework

The research framework studies

```text
κ = (β × D) / ρ
```

with domain-specific definitions frozen before testing. Scalar κ remains falsifiable. No repository result currently establishes universal κ, general financial alpha, investment suitability, causal mechanism, or cross-domain universality.

---

## Corrected successor requirements

`KFIN-V2_1-20260908-002` must:

1. keep the same non-overlapping future target and split logic;
2. use the exact frozen target threshold for persistence;
3. preserve β, β×D, β/ρ and κ comparisons;
4. keep training-only preprocessing and the frozen AP pass rule;
5. create receipts exclusively and preserve errors separately;
6. refuse GitHub Actions rerun attempts for the same execution identity;
7. undergo code review before confirmatory execution;
8. preserve any first adverse result without retry-to-win.

Even after a valid successor PASS, stronger conventional volatility baselines, uncertainty intervals, repeated holdouts/prospective data, and independent reconstruction remain required before strong public validation language.

---

## Public-use / Funding / Legal Guardrail

Do not cite:

- the March `100% precision validated` headline;
- the historical `+88.32% improvement` claim;
- the noncontrolling KFIN-v2 raw PASS as a valid confirmatory result.

Current permitted statement:

> The original finance validation failed independent audit. A redesigned run produced promising raw incremental-ranking results, but code review found a protocol-implementation mismatch; those results are preserved as a procedural scar while a corrected fresh successor is prepared.

No investment advice or production trading claim is made.

---

**Research principle:** reproduce the number, attack the interpretation, preserve the scar, and make every successor earn its own claim.
