# κ-Framework Validation Results
## Current Evidence State — 2026-09-08

**Historical experiment:** 2026-03-12 — invalidated as validation  
**Independent adverse audit:** 2026-09-08  
**First redesigned run:** `KFIN-V2-20260908-001` — raw PASS, adjudicated PROCEDURAL FAIL  
**Fresh successor:** `KFIN-V2_1-20260908-002` — pending confirmatory execution

---

## 1. Historical S&P experiment

The March computation reproduced its 100% precision / 25% recall numbers, but the 2026-09-08 audit found target circularity, an inadequate baseline, and full-sample target-threshold leakage.

Historical terminal:

```text
REPRODUCIBLE_CODE__CIRCULAR_TARGET__DOMINATED_BY_TRIVIAL_BASELINES__NO_INDEPENDENT_PREDICTIVE_CONTENT_DEMONSTRATED
```

---

## 2. KFIN-V2-20260908-001 — raw execution

The successor introduced a genuinely future, non-overlapping 20-day volatility target, training-only thresholds, β-only / persistence comparators, and D/ρ ablations.

Raw execution custody:

- GitHub Actions run: `34243432146`
- Execution commit: `480933cf6e339dc85dba93edf9bb24e91433c7d5`
- Artifact ID: `10062961206`
- Artifact ZIP SHA-256: `98f51bc17ab6b04a39a1d4dc06832dc5d6ab326abd62b0925d9ce69f1f634bc2`
- Receipt SHA-256: `40f325b1758eeeed465b57c2bdf85465aea591c0af4dd16a4cb3a8a427d8e3de`

Raw average precision:

| Score | AP |
|---|---:|
| β | 0.2383 |
| β×D | 0.3114 |
| β/ρ | 0.2970 |
| κ | 0.3859 |
| Persistence | 0.2200 |

The raw workflow emitted `INCREMENTAL_KAPPA_CONTENT_PASS`.

---

## 3. Post-run code review — controlling adjudication

Codex review found two P1 issues.

### 3.1 Persistence baseline implementation mismatch

The protocol required persistence to compare current β with the **training target threshold**. The code instead recomputed q80 from `train["beta"]`.

In this run both values happened to be exactly:

```text
0.19696579040212642
```

so the numerical persistence predictions were unchanged. Nevertheless, the implementation did not literally execute the preregistered experiment and the run cannot receive a confirmatory scientific PASS.

### 3.2 First-receipt overwrite vulnerability

The script used `Path.write_text`, allowing a repeated local invocation to truncate/replace the first receipt. The GitHub artifact remains preserved, but the implementation did not structurally enforce the no-retry / first-terminal rule.

### Controlling terminal

```text
PROCEDURAL_FAIL__PERSISTENCE_BASELINE_IMPLEMENTATION_MISMATCH__RAW_RECEIPT_PRESERVED
```

The raw metrics are retained as diagnostic evidence only.

---

## 4. Fresh successor

`KFIN-V2_1-20260908-002` is the only valid next confirmatory identity.

It must preserve the scientific semantics of the V2 design while correcting implementation fidelity:

1. exact frozen target threshold used for persistence;
2. exclusive receipt creation (`x` / create-only semantics);
3. separate error receipt that cannot overwrite a scientific terminal;
4. explicit refusal of GitHub Actions rerun attempts for the same run identity;
5. code review before execution;
6. same target, split, score definitions, metrics, and AP pass rule unless a separately preregistered future experiment changes them.

---

## 5. Current claim ceiling

Permitted:

> The original finance test failed independent audit. A redesigned test produced promising raw incremental-ranking results, but post-run code review found a protocol implementation mismatch; the raw result is preserved as a procedural scar and a corrected fresh successor is required.

Not permitted:

- finance validation success;
- universal κ;
- general alpha;
- investment suitability;
- production readiness;
- causal or cross-domain conclusions.

---

**Governing rule:** a numerically unchanged implementation mismatch is still a procedural failure when the protocol was frozen in advance.
