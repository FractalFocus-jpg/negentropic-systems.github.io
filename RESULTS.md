# κ-Framework Validation Results
## Current Evidence State — corrected 2026-09-08

**Historical experiment date:** 2026-03-12  
**Independent audit date:** 2026-09-08  
**Current status:** ❌ ORIGINAL S&P VALIDATION CLAIM RETIRED

---

## Historical computation that reproduced

The original `kappa_analysis.py` run is reproducible and returns the previously published S&P 500 numbers:

- Precision: 100% (16/16 alerts correct)
- Recall: 25% (16/64 labeled events caught)

Those numbers are preserved as a **reproducible historical computation**, not as evidence of independent predictive value.

---

## Independent adverse audit

A cold audit on 2026-09-08 identified three methodological defects.

### 1. Target circularity

`β` was the 20-day annualized rolling volatility. The target `high_vol` was created from the same 20-day annualized rolling volatility series. A one-day shift meant adjacent feature/target windows shared 19 of 20 observations.

This primarily tests persistence / volatility clustering rather than incremental κ information.

### 2. Weak baseline

The historical report compared precision with the prevalence/random rate (~11.7%). For an autocorrelated volatility target, that is not an adequate benchmark.

Independent controls on the same holdout reported:

| Method | Precision | Recall | Audit interpretation |
|---|---:|---:|---|
| Persistence | ~94.9% | ~94.9% | Strong trivial/autocorrelation baseline |
| β-only | 100% | 39.0% | Strictly better recall than published κ at equal precision |
| Published κ | 100% | ~25–27% | No incremental content established |

The published D and ρ terms did not add value on this experiment.

### 3. Label leakage

The target's 80th-percentile volatility threshold was calculated on the full sample, including the test period. The numerical effect was small in the audit, but the construction is methodologically invalid and is prohibited in future confirmatory runs.

---

## Correct terminal for the March S&P experiment

```text
REPRODUCIBLE_CODE__CIRCULAR_TARGET__DOMINATED_BY_TRIVIAL_BASELINES__NO_INDEPENDENT_PREDICTIVE_CONTENT_DEMONSTRATED
```

This terminal is limited to this experiment. It does not adjudicate other κ domains, physics work, PDE work, Holonomy Renormalization, or UOS as a whole.

---

## Validation v2

A clean replacement experiment is now specified in:

- `VALIDATION_PROTOCOL_V2.md`
- `kappa_validation_v2.py`

The confirmatory test uses a non-overlapping future volatility window, training-only thresholds, persistence and β-only baselines, D/ρ ablations, frozen metrics, and a first-terminal receipt.

No v2 success is claimed until that script is run under the frozen protocol and the resulting receipt is independently reconstructed.

---

## Public claim retirement

The following historical language is retired and must not be cited as current evidence:

- `Status: VALIDATED`
- `100% precision validated`
- `+88.32% improvement vs baseline`
- `The framework works`
- any implication that the original hold-out design by itself prevented leakage/circularity

---

## Governing rule

**Reproduce the number. Attack the interpretation. Preserve the failure. Design the next test before seeing its result.**
