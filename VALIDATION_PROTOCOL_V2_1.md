# κ Finance Validation Protocol v2.1
## Fresh confirmatory successor after the V2 procedural failure

**Experiment ID:** `KFIN-V2_1-20260908-002`  
**Status:** FROZEN BEFORE EXECUTION / CODE REVIEW REQUIRED BEFORE MERGE  
**Parents:** historical March adverse audit; `KFIN-V2-20260908-001` raw receipt; procedural adjudication in `adjudications/KFIN-V2-20260908-001.md`.

This is a fresh one-use successor. It does not repair or reinterpret the consumed V2 identity. The scientific target, feature map, split, metrics, and average-precision pass rule are intentionally unchanged from V2.1's V2 parent; only the two implementation defects identified by Codex are corrected: persistence uses the exact frozen target threshold, and receipt creation is structurally create-only.

---

## 1. Frozen research score

```text
κ = (β × D) / ρ
```

Finance mapping for this experiment:

- `β`: annualized standard deviation of the past 20 trading-day returns.
- `D`: absolute deviation of current price from its past 50-day moving average, normalized by that moving average.
- `ρ`: `1 - abs(lag-1 autocorrelation)` over the past 20 daily returns.
- denominator epsilon: `0.001`.

No parameter above may be changed after this protocol is merged for confirmatory execution.

---

## 2. Frozen non-overlapping target

For feature date `t`, the target uses realized volatility from returns over exactly:

```text
t+1 ... t+20
```

The target is:

```text
future_high_vol = future_20d_realized_vol > q80_train_target
```

where `q80_train_target` is computed only from admitted training target values.

The feature window ends at `t`; the target-return window begins at the next trading observation after `t`.

---

## 3. Frozen split

- Test feature dates begin `2024-01-01`.
- A training row is admitted only when its complete future target window ends before `2024-01-01`.
- A test row is admitted only when its complete future target window is observed.
- All score thresholds and the target threshold are computed from admitted training rows only.

---

## 4. Frozen comparators

Continuous scores:

1. `beta` = β-only.
2. `beta_D` = β × D, with ρ ablated.
3. `beta_over_rho` = β / ρ, with D ablated.
4. `kappa` = β × D / ρ.

Persistence baseline:

```text
persistence = 1 if current beta > q80_train_target else 0
```

**Implementation fidelity correction:** the persistence baseline must use the exact already-computed `q80_train_target`. It may not recompute a separate q80 from the β feature distribution, even if those values happen to coincide on a particular dataset.

Frozen alert operating points for the four continuous scores use each score's own training-only q95 threshold. Persistence uses `q80_train_target` exactly.

---

## 5. Frozen metrics

For each continuous score on the held-out test:

- average precision / PR-AUC;
- ROC-AUC when both classes are present;
- precision, recall, F1, alert rate, and alert count at the frozen q95 score threshold.

For persistence:

- precision, recall, F1, alert rate, alert count;
- average precision using its frozen binary score.

Also report target prevalence and admitted train/test counts.

---

## 6. Frozen scientific pass rule

The first scientifically valid run earns `INCREMENTAL_KAPPA_CONTENT_PASS` only if all are true:

1. `AP(kappa) > AP(beta)`;
2. `AP(kappa) > AP(beta_D)`;
3. `AP(kappa) > AP(beta_over_rho)`;
4. `AP(kappa) > AP(persistence)`;
5. all declared target/split/threshold integrity gates pass.

Otherwise it earns `NO_INCREMENTAL_KAPPA_CONTENT_ON_FROZEN_TEST`, unless a more specific procedural/integrity/error terminal applies.

No minimum effect size is imposed by this first clean successor. A numerical PASS remains only a bounded candidate signal.

---

## 7. Integrity and one-use gates

The implementation must fail closed if:

- target-window ordering or train/test separation is violated;
- target or score thresholds use test data;
- required rows/columns/classes are insufficient;
- a canonical V2.1 receipt already exists in the repository;
- the local scientific receipt path already exists;
- GitHub Actions reports `GITHUB_RUN_ATTEMPT > 1`;
- non-finite required values survive admissible-row filtering.

### Create-only receipt law

The scientific receipt must be created using exclusive/create-only file semantics. It may never be truncated or overwritten.

Implementation/data errors must be written to a separate create-only error receipt and may never replace a scientific terminal.

A repeat-attempt refusal must be written to a separate create-only refusal receipt and must exit nonzero.

---

## 8. Executor and review membrane

The only admitted first executor is `.github/workflows/kappa-validation-v2-1.yml` on GitHub Actions after this branch receives automated code review and any review findings are resolved **before merge**.

The workflow:

- runs only on a push to `main` changing the V2.1 protocol/script/workflow files;
- has no manual `workflow_dispatch` trigger;
- uses Python `3.11.16`;
- pins `pandas==3.0.5`, `numpy==2.4.6`, and `scikit-learn==1.9.0`;
- uploads scientific/error/refusal receipt plus console log as an immutable run artifact;
- fails CI on implementation, data, or repeat-attempt refusal;
- treats a scientifically valid PASS or FAIL as a completed execution rather than retrying to win.

---

## 9. Claim ceiling

A valid PASS establishes only bounded incremental ranking content for this exact finance mapping, dataset, split, future-volatility target, and frozen average-precision criterion.

It does **not** establish:

- universal κ;
- general financial alpha;
- investment suitability;
- causal mechanism;
- production trading readiness;
- cross-domain universality.

A valid FAIL falsifies incremental content only for this exact frozen successor.

---

## 10. Post-terminal roadmap

After either a valid PASS or FAIL:

1. preserve the first raw receipt and hashes;
2. commit an additive adjudication/currentness pointer without editing the raw receipt;
3. run block/bootstrap uncertainty only under a fresh analysis identity;
4. preregister stronger conventional volatility baselines (e.g. HAR/GARCH-family) under a fresh successor;
5. test additional independent temporal holdouts and/or prospective data;
6. require a clean-room implementation from this written protocol;
7. require external reconstruction before strong public validation language;
8. preserve mixed metrics rather than presenting one favorable metric as global dominance.

**Governing law:** frozen methodology is part of the experiment. A successor can earn a new result; it cannot erase the scar that forced its creation.
