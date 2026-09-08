# Validation Audit Ledger
## Current controlling public audit state

**Last updated:** 2026-09-08  
**Historical March terminal:** adverse / invalidated validation  
**KFIN-V2-20260908-001:** raw PASS preserved; controlling terminal = PROCEDURAL FAIL  
**KFIN-V2_1-20260908-002:** valid first terminal = `INCREMENTAL_KAPPA_CONTENT_PASS` with bounded claim ceiling

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

## B. KFIN-V2-20260908-001 — redesigned but procedurally invalid

The first redesign correctly introduced a non-overlapping future-volatility target, training-only thresholds, persistence and β-only comparators, D/ρ ablations, and frozen AP pass conditions.

Its raw workflow emitted `INCREMENTAL_KAPPA_CONTENT_PASS`, but post-run Codex review found:

- persistence used a separately recomputed β q80 rather than the exact frozen training target q80 named by the protocol;
- local `Path.write_text` could overwrite a first receipt.

The two q80 values happened to be numerically equal, but frozen methodology is part of the experiment. Controlling terminal:

```text
PROCEDURAL_FAIL__PERSISTENCE_BASELINE_IMPLEMENTATION_MISMATCH__RAW_RECEIPT_PRESERVED
```

Raw V2 custody remains preserved in `receipts/KFIN-V2-20260908-001.json` and `adjudications/KFIN-V2-20260908-001.md`.

---

## C. KFIN-V2_1-20260908-002 — fresh one-use successor

### C1. Pre-execution corrections

V2.1 preserved the V2 scientific target/split/score/metric/pass semantics and corrected execution fidelity before confirmatory execution:

- persistence uses the exact already-computed training target q80;
- scientific/error/refusal receipts are create-only and mutually exclusive;
- any pre-existing local terminal consumes the checkout identity;
- only `GITHUB_ACTIONS=true`, the exact repository, `push`, `refs/heads/main`, run attempt exactly `1`, and nonempty run ID/SHA/token are admitted;
- live `main` is queried before analysis for durable prior consumption;
- matching executions are serialized by a fixed concurrency group;
- the workflow automatically persists the exact first scientific/error terminal to the canonical live-main receipt path before completion;
- the canonical receipt path is excluded from workflow triggers;
- all material Codex code-review findings were resolved before merge.

PR #3 merged at commit:

`b9698649469a36921fc9c0f82190747467bf36cf`

### C2. Execution

GitHub Actions run `34246951669`, attempt `1`, completed successfully. Every workflow step passed, including:

- frozen environment setup;
- one-use confirmatory execution;
- artifact upload;
- durable canonical receipt persistence;
- terminal-class adjudication.

Canonical receipt:

`receipts/KFIN-V2_1-20260908-002.json`

### C3. Custody

Artifact ID: `10064382539`

- Artifact ZIP SHA-256: `d5bdd3478284ec42f086824899bec1040545a132019daaa853c361499fedc675`
- Scientific receipt SHA-256: `87ef8e803cc0a4e5420b09b4d4a4965608e363429c00dcb15e731fd34f3e3468`
- Console SHA-256: `2a88c149f92cea163b13fc990a09f4f41c44906d58883385e601418e1dd27014`

Receipt source-custody hashes:

- dataset: `30c8b42de4a4cf47b1c67d5117740024ef3a94092df2a0eba0ee906b929d90fc`
- protocol: `afdd7ac526512225e648e9798b353c72099eeb05d3cc95f89a1c1e15bb09399f`
- script: `9df32657be214aa762fbea25a6663c2c7b3c3a3f427c52ba1b00fff184997bfb`

### C4. Integrity

All receipt integrity gates are `true`:

- feature-date split valid;
- feature/target order non-overlap;
- persistence uses exact target threshold;
- thresholds training-only;
- training targets end before test start.

Counts:

- train rows: 3,453
- test rows: 529
- positive test targets: 59
- prevalence: 11.153%

### C5. Results

| Score | AP | ROC-AUC | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|
| β | 0.2383 | **0.6835** | 0.3478 | 0.1356 | 0.1951 |
| β×D | 0.3114 | 0.6269 | 0.6429 | 0.1525 | 0.2466 |
| β/ρ | 0.2970 | 0.6732 | 0.3750 | 0.1525 | 0.2169 |
| **κ** | **0.3859** | 0.6429 | **0.6875** | 0.1864 | 0.2933 |
| Persistence | 0.2200* | — | 0.3898 | **0.3898** | **0.3898** |

`*` persistence AP uses its frozen binary score.

All five preregistered AP/integrity conditions passed.

### C6. Valid first terminal

```text
INCREMENTAL_KAPPA_CONTENT_PASS
```

This is the first scientifically admissible terminal for the redesigned finance experiment lineage.

---

## D. Claim ceiling and mixed-metric firewall

The PASS establishes only bounded incremental ranking content on the exact frozen V2.1 held-out average-precision criterion.

It does not establish global metric dominance:

- β ROC-AUC exceeded κ ROC-AUC;
- persistence F1 and recall exceeded κ F1 and recall;
- κ recall at its frozen q95 alert threshold was 18.64%.

It does not establish universal κ, causal finance mechanism, general alpha, investment suitability, production trading readiness, or cross-domain universality.

---

## E. Public / funding / legal currentness

Retired permanently from the March experiment:

- `100% precision validated`;
- `+88.32% improvement vs baseline`;
- `Validation: SUCCESS` as evidence of independent κ prediction;
- claims that the old hold-out construction itself prevented leakage/circularity.

The raw V2 PASS also remains noncontrolling because its procedural failure is immutable.

Permitted current sentence:

> A code-reviewed, preregistered, one-use successor using a non-overlapping future-volatility target produced a bounded incremental-content PASS on its frozen held-out average-precision criterion; stronger conventional baselines, uncertainty analysis, repeated holdouts, and independent reconstruction remain open.

---

## F. Next-proof requirements

1. block/bootstrap uncertainty intervals;
2. independent temporal holdouts and/or prospective data;
3. preregistered HAR/GARCH-family or equivalently strong conventional volatility baselines;
4. clean-room independent implementation from the protocol;
5. external reconstruction of source hashes, workflow, artifact and canonical receipt;
6. calibration and decision-utility analysis before any financial-action claim;
7. transaction-cost-aware evaluation only if trading utility is later claimed;
8. preserve every first adverse terminal and mixed metric without selective reporting.

---

## G. Other domain states

- VIX: underperforming historical diagnostic; not validated.
- Solar: monitoring/data pipeline only; predictive validation open.
- Neural/EEG: simulation/literature comparator; real-data validation pending.
- Crypto: diagnostic claims require leakage/baseline/ablation audit before promotion.
- Forex: no completed validation.

---

**Audit law:** reproducibility is not validity; a successor may earn a new result, but it never repairs the scar that forced its creation.