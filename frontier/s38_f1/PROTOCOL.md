# S38-F1 — Critique-to-upgrade continuation

Analysis identity: `KFIN-S38-F1-20260908-001`
Date: 2026-09-08
Parent: `KFIN-V2_1-20260908-002`
Class: POST-TERMINAL DIAGNOSTIC / SAME PREVIOUSLY OBSERVED HOLDOUT / NON-INDEPENDENT.
This method is fixed before this analysis executes, but it is NOT a fresh blind confirmation. V2 and V2.1 outcomes were already observed. No new prospective evidence is manufactured by changing the analysis ID.

## Founder continuity

Alexander's observation, “We literally upgraded from it,” is preserved as the engineering lineage: criticism -> adverse receipt -> claim retirement -> explicit constraint -> successor -> measured result. This is consistent with the intended Living Morphology discipline. Calling this “Holonomy Renormalization” records conceptual continuity, not a measured holonomy theorem or proof of universal physics. A future holonomy claim still needs a defined connection, loop, admissible equivalence class, measured defect and falsifier.

Successor may repair predecessor; successor may not rewrite predecessor. A scar must be capable of permanently lowering its predecessor's epistemic status. Better governance is not automatically stronger predictive evidence.

## Correction to the prior completion summary

The final PR #3 review was completed but was NOT free of findings. Comment `3959707387`, dated 2026-09-08 15:45:39Z, requires reserving the identity BEFORE analysis: a crash or failed post-analysis Contents API write could otherwise reopen an identity. The earlier statement that all P1 findings were resolved before merge was too strong. The historical V2.1 raw receipt stays unchanged; its raw point estimates remain available. The stronger fully-cleared pre-merge review/crash-safe custody claim is withdrawn. This correction is not evidence that the displayed numbers were altered.

Source: https://github.com/FractalFocus-jpg/negentropic-systems.github.io/pull/3#discussion_r3959707387

## Source and reconstruction gate

Read the existing sp500.csv only. Required SHA-256:
`30c8b42de4a4cf47b1c67d5117740024ef3a94092df2a0eba0ee906b929d90fc`.
Parent receipt is `receipts/KFIN-V2_1-20260908-002.json`.
Do NOT execute the consumed parent entrypoint. Reconstruct its declared score table in a new diagnostic module and require all five AP values, 529 test rows, 59 positive rows and the training target threshold to match within absolute 1e-12. This is an internal numerical reconstruction, not a clean-room or unaffiliated replication.

Retain the parent's 20-return beta, 50-price trend deviation, rho = 1 - absolute lag-1 autocorrelation, denominator epsilon 0.001, future t+1..t+20 sample-standard-deviation target, training target q80 and 2024-01-01 split. Training target windows must end before the test split. The return windows are feature-target disjoint, but adjacent target windows share 19 returns; the 59 labels are NOT 59 independent market events.

## E13: paired circular-block uncertainty

Freeze 5,000 attempted bootstrap samples per block length 20, 40 and 60 rows. Primary length: 40. RNG: NumPy default_rng seed 20260908 + block length. Each sample draws uniform circular-block starts and uses the same row indices for labels and all comparator scores. No model refitting, threshold selection or new labels in the bootstrap.

Metric: noninterpolated average precision (AP), with tied scores grouped. AP is not interchangeable with trapezoidal PR-AUC. Verify the implementation against scikit-learn.

Report kappa minus each of beta, beta_D, beta_over_rho and binary persistence. For each report paired percentile 95% intervals and Bonferroni original-four-family intervals using quantiles 0.00625 and 0.99375 (98.75% each, nominal family alpha 0.05). Also report the fraction of bootstrap deltas above zero; this is NOT a p-value or posterior probability.

Count and disclose bootstrap samples lacking either class; do not silently redraw. More than 250 invalid samples at primary block length yields DATA_INSUFFICIENT_FOR_STABLE_BOOTSTRAP. Otherwise the descriptive robustness criterion requires all four simultaneous lower bounds > 0 and all four point gains >= 0.02 AP. The 0.02 threshold is a chosen diagnostic materiality threshold, not a discovered physical constant or retrospective amendment to V2.1. If not met, output UNCERTAINTY_NOT_RESOLVED__POINT_ESTIMATE_ONLY. Even a pass remains descriptive, conditional on this observed table, and not selection-adjusted, a training-parameter uncertainty analysis, or prospective validation. Circular resampling's local-stationarity approximation is a limitation.

Count contiguous positive-label runs with dates and sizes. These runs are a dependence diagnostic, NOT an independent-event estimator.

## E14: conventional baseline diagnostic

Add a zero-mean Gaussian-QMLE GARCH(1,1) and fixed-decay EWMA (lambda=0.94). Fit GARCH on percentage daily returns strictly before 2024-01-01 only. Initialize variance to that training sample variance. SLSQP optimizer uses three fixed starts (alpha,beta)=(0.05,0.90),(0.10,0.80),(0.15,0.80), omega=(1-alpha-beta)*training variance; bounds omega >= 1e-10, alpha,beta >= 0, alpha+beta <= 0.999999; maxiter=1000, ftol=1e-9. Select minimum TRAINING likelihood among successful optimizations. If none converge, record error, not a replacement comparator chosen after test results.

Freeze parameters throughout test; filtering may use returns observed through feature date t, not future returns. GARCH score is square root of 252 times mean t+1..t+20 forecast conditional variance, divided by 100. EWMA starts from the first 20 training squared returns and updates causally using fixed decay. Its future-variance persistence forecast supplies the ranking score. These are volatility-ranking comparators, not calibrated forecasts of exactly the same centered sample-standard-deviation functional. Report AP/ROC-AUC, paired 95% AP-difference intervals and fit metadata. No claim of superiority over the entire GARCH family. No trading decisions, financial advice, profit or production claim.

## E19: reserve before execution

Use dedicated evidence branch `audit/s38-f1-evidence`. Create `ledger/reservations/KFIN-S38-F1-20260908-001.json` through Contents PUT without a SHA BEFORE the analysis callback. A conflict, timeout, unknown outcome or failed HTTP response refuses analysis. A successful reservation consumes the identity even if analysis, runner or terminal persistence subsequently fails. Do not delete/reuse reservations to retry. Recovery gets a separate incident record.

Create a separate terminal at `ledger/terminals/KFIN-S38-F1-20260908-001.json`, also create-only. Rejected later attempts cannot alter either original record. Keep raw local output and Actions artifact for recovery, but a 90-day Actions artifact alone is not permanent custody.

Admitted diagnostic executor: push to `audit/s38-f1-next-frontier`, exact repository/workflow_ref, first run attempt. No local execution admitted for the scientific-data callback; offline tests use synthetic data and an injected in-memory store. GitHub contents:write permission is repository-wide, not technically path-limited. The adapter restricts its two intended record paths; this is not protection against a malicious administrator, compromised token, deleted ledger branch or provider failure. No claim of full autonomous complete mediation.

## Roadmap and exit gates

F1-00: preserve lineage and correct review-clearance overstatement.
F1-01: bind source and parent receipt hashes.
F1-02: internally reconstruct the parent score table without executing its entrypoint.
F1-03: execute paired dependence-aware uncertainty.
F1-04: execute the frozen GARCH diagnostic.
F1-05: execute EWMA diagnostic.
F1-06: disclose label clustering and mixed metrics.
F1-07: test reservation, concurrency, crash, timeout and overwrite failures on synthetic fixtures.
F1-08: obtain new code review; completion is not clearance and unresolved findings remain open.
F1-09: design a truly untouched/prospective holdout before looking at outcomes; current data remains development/diagnostic material.
F1-10: freeze a second non-market domain's observables and independence criterion before data reveal; do not invent biological or plasma evidence.
F1-11: independent implementation and unaffiliated reconstruction before stronger promotion.
F1-12: derive and test an actual holonomy observable separately; engineering repair is not itself physical holonomy evidence.

## Primary methodological references

https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html
https://bashtage.github.io/arch/devel/bootstrap/timeseries-bootstraps.html
https://arch.readthedocs.io/en/latest/univariate/forecasting.html

Claim ceiling: method-specific, retrospective diagnostics and bounded engineering tests only. Historical March and V2 scars remain permanent. No universal-kappa, life/personhood, physics, Clay, production-autonomy, causal or commercial promotion.
