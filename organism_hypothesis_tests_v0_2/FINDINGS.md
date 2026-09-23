# Organism hypothesis tests v0.2 — findings for Claude's review

11 September 2026. Written and executed by ChatGPT at Rusty's request. This is a new experiment, not a repair that retroactively validates v0.1.

The proposed reinterpretations received mixed and negative evidence. Holding the empirically disfavored coordinate caused more interference on average, but interference did not scale positively with the evidence gap. Reliance-weighted attribution did not show a clear overall advantage over unweighted attribution. Neither result establishes the larger restoration mechanism.

## What was fixed before running

PROTOCOL.md records the hypotheses, all 24 seeds, learning settings, comparisons, outcomes and bootstrap procedure before the first run of this version. This is local prospective specification, not independent preregistration or blinded research. No outcome-based parameter or scoring changes were made. Integrity tests were added after the run; an unclosed-file warning in test readers was subsequently removed without changing experiment code or results.

Every comparison uses shared, saved input arrays. Evidence preference comes from empirical residual loss, not coefficient magnitude or access to the world's true rule. The holding mask affects only its selected coordinate. Frozen records preserve their complete observation bytes and factual description under SHA-256; interpretation does not alter them. These changes address defects in the prior instrument, not the truth of the hypotheses.

## H2: disagreement and interference

Holding is implemented as resistance to updating one existing coefficient. It does not force exclusive reliance on that feature. For each initial state, clones hold either the empirically favored or disfavored coordinate while receiving identical subsequent data. Excess loss is measured against the identical-input unconstrained clone.

Primary paired contrast: excess prequential MSE under disfavored holding minus excess MSE under favored holding. Positive values favor this operational H2 prediction.

| Gradient multiplier | Mean contrast | Exploratory 95% seed-bootstrap interval |
|---|---:|---:|
| 0.05 | 0.005569 | [0.004736, 0.006400] |
| 0.00 | 0.007518 | [0.006276, 0.008785] |

However, the proposed gap-scaling prediction does not hold descriptively. At multiplier 0.05:

| Initial mixing parameter | Mean disfavored evidence gap | Favored holding excess MSE | Disfavored holding excess MSE |
|---|---:|---:|---:|
| 0.00 | 0.251193 | 0.000311 | 0.000016 |
| 0.80 | 0.015267 | 0.025446 | 0.036654 |
| 0.95 | 0.000621 | 0.039051 | 0.044843 |

The parameter is a mixing coefficient, not exactly Pearson correlation: the other feature is rho times the signal plus (1-rho) times independent noise. Feature variance therefore changes as well. Each setting also uses its own seeded sample stream; alignment arms within each setting share exact inputs.

The largest measured evidence gap accompanies the smallest disfavored holding cost. Mean within-seed gap/cost covariance is negative at both multipliers: -0.002224 and -0.002923. Favored commitments can also carry substantial interference. Thus the blanket claim that agreement implies little or no burden is not supported by this implementation.

A plausible explanation is coefficient trapping: holding an already-small irrelevant coefficient costs little, whereas holding a coefficient acquired in a misleading context costs more. This is an interpretation, not a separately identified causal result. The experiment changes learned weights, sample geometry and selected coordinate along with disagreement. Equal gradient multipliers do not equalize functional constraint. The positive average contrast cannot identify dissonance as its unique cause.

## H1: situated attribution and useful action

Each seed supplies one frozen record to four reader states. Upweighting, unweighted scoring and discounting choose a coordinate to correct from that record. Actual loss reduction is assessed on independent samples from the record's historical generating regime. This tests a limited actionable consequence of an interpretation; it does not score the hidden true feature as the answer.

| Contrast in loss reduction | Mean | Exploratory 95% seed-bootstrap interval |
|---|---:|---:|
| Upweight minus unweighted | -0.000002610 | [-0.000008954, 0.000002761] |
| Upweight minus discount | 0.000002750 | [-0.000004375, 0.000009926] |

Upweighting changes the selected feature in 13 of 96 reader states relative to unweighted scoring; discounting changes it in 9. Those differences alone are not useful development. No clear overall gain was observed from upweighting. Intervals spanning zero do not establish equivalence or absence of every possible effect.

The confounded reader state shows a small upweight-over-discount advantage (mean 0.000020385, interval [0.000005229, 0.000038240]); that does not extend to the overall contrast or establish superiority over unweighted scoring. All state-specific results, including negative ones, remain in summary.json and the trial tables.

This test assumes independent samples from the same historical regime are an appropriate warrant test. It does not test semantic interpretation, general transfer, truthful confession, love, forgiveness, or whether an old error becomes a parable. The record is a misleading observation context, not a naturally recognized transgression.

## Instrument checks and sample size

All 12 integrity tests pass. They cover shared inputs, exact unconstrained-arm equality, replay of all 432 H2 loss trajectories, gradient locality, evidence preference, record immutability, reader preservation, paired scoring and declared attribution behavior. These are checks of the instrument, not 12 confirmations of the research hypothesis. Static checks for named oracle access are not a security proof.

There are 24 independent seed blocks, 432 H2 trajectories and 288 H1 evaluations. Conditions within seeds are paired. The bootstrap resamples seed-level contrasts, not individual trajectory rows. Intervals are exploratory and unadjusted for multiple comparisons.

## Review targets

1. Does resistance to coefficient updates adequately instantiate the proposed holding mechanism? It is explicitly narrower than forcing a rule commitment.
2. Can the positive H2 contrast be explained entirely by coefficient geometry and adaptation cost? The current design does not separate these causes.
3. Does the coordinate-action assay test a useful part of situated interpretation, or substitute a different objective? A changed attribution is not accepted as success by itself.
4. Verify matching and replay from the saved arrays, and check the paired summaries against raw rows. Preserve the unfavorable gap-scaling and H1 outcomes when reviewing.

The larger unknowns remain held. This version supplies falsifiable consequences and an auditable mixed result; it does not convert the earlier defects into established features.
