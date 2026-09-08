# KappaRisk Validation Platform
## κ-Stability Research and Audit Harness

**Current public status (2026-09-08): validation claims under correction after independent cold audit.**

The repository remains reproducible as code, but the original S&P 500 validation claim has been retired. An independent cold audit (Claude/Rhythm, 2026-09-08) reproduced the published 100% precision / 25% recall numbers and then identified target circularity, an inappropriate prevalence/random baseline, and test-label leakage. The published S&P experiment therefore does **not** demonstrate independent predictive value for κ.

---

## Current Evidence State

| Domain | Current state | Public claim ceiling |
|---|---|---|
| S&P 500 | Reproducible code; original validation invalidated | No independent κ predictive content demonstrated yet |
| VIX | Underperforming diagnostic | Not validated |
| Solar | Monitoring / data pipeline | Prediction accuracy not yet validated |
| Neural / EEG | Simulation + literature comparator | Real-data validation pending |
| Crypto | Diagnostic only | Requires independent baseline and leakage audit |
| Forex | Not started | No claim |

### S&P 500 adverse audit

The original script defined:

- `β` = 20-day annualized rolling volatility
- target `high_vol` = the same 20-day annualized rolling volatility thresholded at the 80th percentile
- prediction = previous-day κ signal

Because adjacent 20-day windows share 19 of 20 observations, this created a circular / overlapping target structure. The original computation is reproducible, but the interpretation was not valid.

Independent controls reported in the 2026-09-08 audit:

- Persistence baseline: ~94.9% precision / ~94.9% recall
- β-only baseline: 100% precision / 39.0% recall
- Published κ: 100% precision / ~25–27% recall

So β-only strictly dominated the published κ signal on this test, and persistence dominated both on combined precision/recall.

**Correct public state:**

`REPRODUCIBLE_CODE__CIRCULAR_TARGET__DOMINATED_BY_TRIVIAL_BASELINES__NO_INDEPENDENT_PREDICTIVE_CONTENT_DEMONSTRATED`

---

## κ Framework

The research framework studies a normalized instability quantity

```text
κ = (β × D) / ρ
```

where the domain-specific meanings of amplification `β`, drift/disorder `D`, and return/repair capacity `ρ` must be frozen before validation. A scalar κ is a research hypothesis, not a universal law established by this repository.

The mature research standard requires directional/transient/target-aware breakers and permits vector/matrix/operator-valued successors if scalar compression loses necessary information.

---

## Validation v2 Requirements

Any future finance validation must be preregistered and satisfy all of the following before execution:

1. **Non-overlapping future target** — target data must be disjoint from feature windows (for example realized volatility over `t+1..t+20`).
2. **Training-only thresholds** — all thresholds, normalizers, and hyperparameters are estimated from training data only.
3. **Strong baselines** — κ must be compared with persistence, β-only, and at least one established volatility baseline under the same split and metrics.
4. **Ablation** — `D` and `ρ` must each show positive held-out marginal value before κ receives incremental-content credit.
5. **Frozen protocol** — target, split, metrics, thresholds, tuning rules, and failure terminals are written down before the confirmatory run.
6. **No retry-to-win** — failures are preserved; a changed design receives a fresh experiment identity.
7. **Calibration and uncertainty** — report precision, recall, PR-AUC / ROC-AUC where appropriate, calibration, coverage, and confidence intervals rather than a single headline metric.
8. **Independent reconstruction** — external or independently implemented replay is required before any strong validation claim.

See `VALIDATION_PROTOCOL_V2.md` and `kappa_validation_v2.py`.

---

## Repository Structure

```text
kappa_analysis.py          # historical S&P experiment; retained for reproducibility
kappa_validation_v2.py    # clean v2 preregistered test harness
VALIDATION_PROTOCOL_V2.md # passing conditions and experiment contract
VALIDATION_AUDIT.md       # audit ledger / historical adverse findings
RESULTS.md                # current evidence summary
api_server.py             # experimental API surface
```

Historical artifacts remain available for reproducibility. They must not be cited as current validation after the 2026-09-08 adverse audit.

---

## Public-use / Funding / Legal Guardrail

Do **not** cite the retired S&P 500 `100% precision`, `+88.32% improvement`, or `validated` language in funding, outreach, legal, patent, licensing, investor, or customer materials.

Any future claim must cite the exact experiment identity, code revision, data split, baselines, metrics, and current claim ceiling.

---

## License

Repository licensing and third-party dependency compliance should be reviewed before external commercialization or proposal use.

---

## Contact

Alexander Liantonio

---

**Research principle:** maximize the claim target; credit only what the receipts earn.
