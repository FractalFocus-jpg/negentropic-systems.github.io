# κ-Framework Validation Results
## Current Evidence State — 2026-09-08

**Historical experiment:** 2026-03-12 — invalidated as validation  
**Independent adverse audit:** 2026-09-08  
**First redesigned run:** `KFIN-V2-20260908-001` — raw PASS, adjudicated PROCEDURAL FAIL  
**Fresh corrected successor:** `KFIN-V2_1-20260908-002` — valid bounded `INCREMENTAL_KAPPA_CONTENT_PASS`

---

## 1. Historical S&P experiment

The March computation reproduced its 100% precision / 25% recall numbers, but the 2026-09-08 audit found target circularity, an inadequate baseline, and full-sample target-threshold leakage.

Historical terminal:

```text
REPRODUCIBLE_CODE__CIRCULAR_TARGET__DOMINATED_BY_TRIVIAL_BASELINES__NO_INDEPENDENT_PREDICTIVE_CONTENT_DEMONSTRATED
```

That historical failure remains intact.

---

## 2. KFIN-V2-20260908-001 — redesigned raw execution, procedural failure

The first redesign introduced a genuinely future, non-overlapping 20-day volatility target, training-only thresholds, β-only / persistence comparators, and D/ρ ablations.

Raw execution custody:

- GitHub Actions run: `34243432146`
- Execution commit: `480933cf6e339dc85dba93edf9bb24e91433c7d5`
- Artifact ID: `10062961206`
- Artifact ZIP SHA-256: `98f51bc17ab6b04a39a1d4dc06832dc5d6ab326abd62b0925d9ce69f1f634bc2`
- Receipt SHA-256: `40f325b1758eeeed465b57c2bdf85465aea591c0af4dd16a4cb3a8a427d8e3de`

The workflow emitted a raw `INCREMENTAL_KAPPA_CONTENT_PASS`, but post-run Codex review found a frozen-protocol implementation mismatch in the persistence baseline and a first-receipt overwrite weakness. Its controlling terminal therefore remains:

```text
PROCEDURAL_FAIL__PERSISTENCE_BASELINE_IMPLEMENTATION_MISMATCH__RAW_RECEIPT_PRESERVED
```

The raw V2 metrics are diagnostic ancestry only.

---

## 3. KFIN-V2_1-20260908-002 — fresh valid one-use successor

V2.1 preserved the V2 scientific design and corrected execution fidelity before seeing its confirmatory result:

- persistence uses the exact training target q80 threshold;
- local scientific/error/refusal receipts are create-only;
- any pre-existing local terminal consumes the identity;
- only the declared push-to-main GitHub Actions executor is admitted;
- live `main` is queried before analysis for prior consumption;
- run attempt must equal exactly 1;
- the first scientific/error terminal is persisted durably to live `main` before job completion;
- the canonical receipt path is excluded from trigger paths, preventing a persistence loop;
- Codex code review completed before merge and all material review threads were resolved.

### Execution custody

- PR: `#3`
- Merge commit: `b9698649469a36921fc9c0f82190747467bf36cf`
- GitHub Actions run: `34246951669`
- Run attempt: `1`
- Artifact ID: `10064382539`
- Canonical receipt: `receipts/KFIN-V2_1-20260908-002.json`

Artifact/file hashes:

- Artifact ZIP SHA-256: `d5bdd3478284ec42f086824899bec1040545a132019daaa853c361499fedc675`
- Scientific receipt SHA-256: `87ef8e803cc0a4e5420b09b4d4a4965608e363429c00dcb15e731fd34f3e3468`
- Console log SHA-256: `2a88c149f92cea163b13fc990a09f4f41c44906d58883385e601418e1dd27014`

Source custody recorded inside the receipt:

- Dataset SHA-256: `30c8b42de4a4cf47b1c67d5117740024ef3a94092df2a0eba0ee906b929d90fc`
- Protocol SHA-256: `afdd7ac526512225e648e9798b353c72099eeb05d3cc95f89a1c1e15bb09399f`
- Script SHA-256: `9df32657be214aa762fbea25a6663c2c7b3c3a3f427c52ba1b00fff184997bfb`

### Integrity gates

All passed:

- feature/target ordering and non-overlap;
- valid feature-date split;
- training target windows end before test start;
- thresholds training-only;
- persistence uses the exact frozen target threshold.

Admitted rows:

- Train: 3,453
- Test: 529
- Positive future-volatility targets: 59
- Test prevalence: 11.153%

### Held-out metrics

| Score | Average precision | ROC-AUC | Precision @ frozen alert | Recall @ frozen alert | F1 |
|---|---:|---:|---:|---:|---:|
| β | 0.2383 | **0.6835** | 0.3478 | 0.1356 | 0.1951 |
| β×D | 0.3114 | 0.6269 | 0.6429 | 0.1525 | 0.2466 |
| β/ρ | 0.2970 | 0.6732 | 0.3750 | 0.1525 | 0.2169 |
| **κ = βD/ρ** | **0.3859** | 0.6429 | **0.6875** | 0.1864 | 0.2933 |
| Persistence | 0.2200* | — | 0.3898 | **0.3898** | **0.3898** |

`*` Persistence average precision uses the frozen binary persistence score.

### Preregistered first terminal

All five frozen average-precision/integrity conditions passed:

```text
INCREMENTAL_KAPPA_CONTENT_PASS
```

This is the first valid scientific terminal for the redesigned finance branch.

---

## 4. Interpretation and mixed-metric boundary

The PASS establishes that, on this exact frozen held-out test, full κ ranked future high-volatility outcomes better by average precision than β-only, persistence, and either D/ρ single ablation.

It does **not** establish global dominance:

- β ROC-AUC was higher than κ: 0.6835 > 0.6429.
- Persistence F1 was higher than κ: 0.3898 > 0.2933.
- Persistence recall was higher than κ: 0.3898 > 0.1864.
- κ emitted only 16 frozen-threshold alerts and had 18.64% recall.

Those counterweights are part of the result.

---

## 5. Current claim ceiling

Permitted:

> A code-reviewed, preregistered, one-use successor using a non-overlapping future-volatility target produced a bounded incremental-content PASS on its frozen held-out average-precision criterion.

Not established:

- universal κ;
- general financial alpha;
- investment suitability;
- causal mechanism;
- production readiness;
- cross-domain universality.

---

## 6. Next-proof roadmap

1. block/bootstrap uncertainty intervals;
2. independent temporal holdouts and/or prospective data;
3. preregistered HAR/GARCH-family or equivalently strong conventional volatility comparator;
4. independent clean-room implementation from the written protocol;
5. external reconstruction of source hashes, workflow, artifact and canonical receipt;
6. calibration and decision-utility analysis before any financial-action claim;
7. transaction-cost-aware study only if trading utility is later claimed;
8. preserve all first failures and mixed metrics without retry-to-win or selective reporting.

---

**Governing rule:** the valid V2.1 PASS does not repair the broken March experiment or the procedurally failed V2 run. It is a new result earned by a new successor.