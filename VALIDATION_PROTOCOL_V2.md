# κ Finance Validation Protocol v2
## Frozen redesign after the 2026-09-08 adverse audit

**Experiment ID:** `KFIN-V2-20260908-001`  
**Status before first run:** PREREGISTERED / NOT YET EXECUTED  
**Purpose:** test whether the complete κ score contains held-out predictive information beyond volatility persistence and β-only information on a genuinely future, non-overlapping target.

---

## 1. Hypothesis

The research score is

```text
κ = (β × D) / ρ
```

with the existing finance mappings retained for this frozen test:

- `β`: past 20-trading-day annualized return volatility
- `D`: absolute deviation of price from its past 50-day moving average, normalized by that moving average
- `ρ`: `1 - abs(lag-1 autocorrelation)` of past 20 daily returns, with a fixed epsilon in the denominator

This experiment does **not** assume that these definitions are universal or optimal. It asks only whether this exact frozen mapping adds predictive information on the declared target.

---

## 2. Non-overlapping target

For feature date `t`, the target is annualized realized volatility computed only from returns over:

```text
t+1 ... t+20
```

No return used in the feature-window volatility `β_t` may appear in the target window.

The binary event is:

```text
future_high_vol = future_20d_realized_vol > q80_train
```

where `q80_train` is estimated from training-target values only.

---

## 3. Train/test boundary

- Test feature dates start at `2024-01-01`.
- A training row is admitted only when its entire 20-day future target window ends before the test start.
- Test rows are admitted only when their full 20-day future target is observed.

This removes target-window spillover across the split.

---

## 4. Frozen scores and baselines

Continuous scores:

1. `beta` — β-only baseline
2. `beta_D` — β × D (ρ ablated)
3. `beta_over_rho` — β / ρ (D ablated)
4. `kappa` — β × D / ρ

Binary persistence baseline:

- Predict future high volatility when current/past 20-day β exceeds the training target high-vol threshold.

Fixed alert operating points:

- β and κ-family alerts use their own **training-only 95th-percentile score threshold**.

No threshold is tuned on test results.

---

## 5. Metrics

For each continuous score on the held-out test:

- Average precision / PR-AUC
- ROC-AUC where both target classes are present
- Precision at frozen alert threshold
- Recall at frozen alert threshold
- F1 at frozen alert threshold
- Alert rate

For persistence:

- Precision
- Recall
- F1
- Alert rate
- Average precision using its binary score

The receipt also reports target prevalence and admitted row counts.

---

## 6. Incremental-content passing rule

The first confirmatory run receives `INCREMENTAL_KAPPA_CONTENT_PASS` only if all conditions hold on the frozen held-out test:

1. `AP(kappa) > AP(beta)`
2. `AP(kappa) > AP(beta_D)` — evidence that ρ contributes beyond the no-ρ ablation
3. `AP(kappa) > AP(beta_over_rho)` — evidence that D contributes beyond the no-D ablation
4. `AP(kappa) > AP(persistence)`
5. target, feature, split, and threshold integrity checks pass

Otherwise the terminal is `NO_INCREMENTAL_KAPPA_CONTENT_ON_FROZEN_TEST` or a more specific integrity/error terminal.

No minimum effect size is claimed by this first v2 experiment. A tiny numerical win is only a candidate signal and would still require uncertainty analysis, repeated independent periods, stronger model baselines, and external reconstruction before a strong public validation claim.

---

## 7. Integrity gates

The script must fail closed if:

- the target window overlaps feature inputs;
- train target windows cross into the test period;
- any score threshold uses test data;
- the test set has no positive or no negative targets;
- required inputs are missing;
- scores/targets contain unusable non-finite values after admissible-row filtering.

---

## 8. First-terminal / no-retry rule

`KFIN-V2-20260908-001` is a one-use confirmatory identity.

- If it fails scientifically, the result is preserved.
- If code fails before a scientifically meaningful terminal because of an implementation defect, the defect and exact receipt are preserved; any repaired implementation receives a new successor ID.
- Hyperparameters, definitions, target, thresholds, and pass criteria may not be changed after seeing the confirmatory output under this identity.

---

## 9. Claim ceiling

A PASS would establish only bounded incremental predictive content for this exact finance mapping, dataset, target, split, and metrics. It would **not** establish universal κ, general financial alpha, investment suitability, causal mechanism, or cross-domain universality.

A FAIL would falsify incremental content for this exact frozen experiment only; it would not automatically falsify every other κ formulation or domain.

---

## 10. Next-stage requirements after any candidate PASS

Before restoring public `validated` language:

1. bootstrap/block-bootstrap uncertainty intervals;
2. multiple non-overlapping historical periods or prospective data;
3. stronger conventional volatility baselines (for example HAR/GARCH-family or another preregistered benchmark appropriate to the data);
4. transaction-cost-aware decision study if financial action is claimed;
5. independent implementation from the written protocol;
6. frozen external reconstruction receipt.

**Governing sentence:** the redesigned test must make κ earn information that β, persistence, and its own ablations do not already contain.
