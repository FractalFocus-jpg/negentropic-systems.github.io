# Validation Audit Ledger
## Current controlling public audit state

**Last updated:** 2026-09-08  
**Historical March terminal:** adverse / invalidated validation  
**KFIN-V2-20260908-001:** raw PASS preserved, controlling terminal = PROCEDURAL FAIL  
**Fresh valid successor:** `KFIN-V2_1-20260908-002`

---

## A. Historical March S&P experiment

The March script reproducibly returned 100% precision / 25% recall, but the 2026-09-08 independent cold audit found:

1. target circularity — β and the target-generating volatility series were identical;
2. weak baseline — prevalence/random comparison was inadequate for an autocorrelated volatility target;
3. target-threshold leakage — the target q80 used the full sample including test data.

Historical terminal:

```text
REPRODUCIBLE_CODE__CIRCULAR_TARGET__DOMINATED_BY_TRIVIAL_BASELINES__NO_INDEPENDENT_PREDICTIVE_CONTENT_DEMONSTRATED
```

This terminal is immutable.

---

## B. KFIN-V2-20260908-001 redesign

The first redesign correctly introduced:

- future non-overlapping t+1..t+20 volatility target;
- training-only target threshold;
- training-only score thresholds;
- train/test target-window separation;
- persistence and β-only comparators;
- β×D and β/ρ ablations;
- frozen average-precision pass conditions;
- first-terminal/no-retry policy.

Raw run custody:

- Workflow run: `34243432146`
- Execution commit: `480933cf6e339dc85dba93edf9bb24e91433c7d5`
- Artifact: `10062961206`
- Artifact ZIP SHA-256: `98f51bc17ab6b04a39a1d4dc06832dc5d6ab326abd62b0925d9ce69f1f634bc2`
- Receipt SHA-256: `40f325b1758eeeed465b57c2bdf85465aea591c0af4dd16a4cb3a8a427d8e3de`
- Console SHA-256: `3c0d03629689bef51ab2af2d5ef3e4d92209f53254f733d9f8eb27514a700af1`

Raw AP values:

- β: 0.2383
- β×D: 0.3114
- β/ρ: 0.2970
- κ: 0.3859
- persistence: 0.2200

The workflow emitted `INCREMENTAL_KAPPA_CONTENT_PASS`.

---

## C. Post-run Codex review — adverse procedural findings

### C1. Persistence threshold mismatch

The preregistered protocol defined persistence against the training **target threshold**. The implementation instead recalculated q80 from `train["beta"]`.

Both thresholds happened to equal `0.19696579040212642` in this dataset, so this defect did not numerically alter the raw persistence predictions. The protocol/implementation mismatch still prevents a valid confirmatory PASS.

### C2. Receipt overwrite weakness

The implementation used `Path.write_text`, which can truncate an existing receipt on repeat local execution. This violated structural enforcement of first-terminal preservation, even though the GitHub artifact from the first run remains separately preserved and hash-bound.

### Controlling adjudication

```text
PROCEDURAL_FAIL__PERSISTENCE_BASELINE_IMPLEMENTATION_MISMATCH__RAW_RECEIPT_PRESERVED
```

The raw workflow terminal is diagnostic only and may not be cited as a valid confirmatory success.

Adjudication file:

`adjudications/KFIN-V2-20260908-001.md`

---

## D. Fresh successor requirements — KFIN-V2_1-20260908-002

The fresh successor must:

1. use the exact frozen target threshold for persistence;
2. preserve the V2 scientific target/split/scores/metrics/pass rule unless separately preregistered otherwise;
3. write a scientific receipt with create-only/exclusive semantics;
4. write implementation errors separately and never overwrite a scientific receipt;
5. reject GitHub Actions rerun attempts (`GITHUB_RUN_ATTEMPT > 1`) for the same run identity;
6. preserve predecessor raw receipt + procedural adjudication as immutable ancestry;
7. undergo automated code review before confirmatory merge/execution;
8. use a fresh experiment ID and first terminal.

Only after these gates close may a new scientific terminal be considered.

---

## E. Public / funding / legal state

Do not cite as current evidence:

- March `100% precision validated`;
- `+88.32% improvement`;
- KFIN-V2 raw `INCREMENTAL_KAPPA_CONTENT_PASS`.

Current permitted statement:

> The historical finance validation failed independent audit. A redesigned run produced promising raw ranking results, but post-run code review found a protocol implementation mismatch; that run is preserved as a procedural failure while a corrected fresh successor is prepared.

---

## F. Other domain states

- VIX: underperforming historical diagnostic; not validated.
- Solar: monitoring/data pipeline only; predictive validation open.
- Neural/EEG: simulation/literature comparator; real-data validation pending.
- Crypto: diagnostic claims require leakage/baseline/ablation audit before promotion.
- Forex: no completed validation.

---

**Audit law:** no result becomes stronger because its bug was numerically harmless on one dataset. Frozen methodology is part of the experiment.
