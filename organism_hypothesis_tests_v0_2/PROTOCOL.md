# Organism hypothesis tests v0.2 — prospective local protocol

Prepared by ChatGPT at Rusty's request for Claude's review. 11 September 2026. These choices are recorded before running this version. This is a local protocol, not independently registered preregistration. Previous source and results are not overwritten.

## Question and scope

Two proposed reinterpretations of organism v0.1 are now hypotheses: H2, disagreement between held commitment and accumulated evidence creates additional functional interference; H1, weighting attribution by current reliance makes it usefully situated. Neither is accepted because it explains the old output. Love, forgiveness, bilateral transition and semantic understanding are not operationalized by this narrow panel. No authorization interface is substituted for the verified junction.

## Shared world and matching

Dimension 8, linear outcome y=x[signal]+noise, observation noise SD .05, feature SD .5. The experimenter controls which of features 0/1 generates the outcome, balanced across seeds; learner code never receives that index. Every sample block is generated once and copied to all compared arms. Correlation injection consumes the same fixed draws regardless of condition. Source arrays and initial states are preserved. No independent shadow generator is used.

There are 24 independent seed blocks, 0–23. Conditions within a seed are paired, not independent replications. Report seed-cluster bootstrap intervals using 5,000 draws, RNG seed 41011. These are exploratory percentile intervals for this specified generator, not confirmatory proof. No parameter or scoring changes in response to results.

## H2: disagreement beyond the cost of holding

At each seed and initial feature correlation 0, .8 or .95, an unconstrained linear learner observes 256 examples. Its favored feature among 0/1 is determined by empirical univariate residual loss from these observations, NOT by comparing regression weights or consulting the world's true feature. The disagreement measure for a chosen commitment is (its empirical residual loss minus the better feature's residual loss), per observation.

Clone that exact state and feed every arm the same next 400 unconfounded examples. Hold factors are 1 (no constraint), .05 (partial holding) and 0 (complete holding). For constrained arms, only the selected feature's gradient is scaled; there is no suppression of a separately identified TRUE_RULE. Compare a commitment to the empirically favored feature with a commitment to the alternative. This implements holding as resistance to coefficient change, the proposed reading of the original gradient mask. It does NOT force the learner to rely exclusively on the committed feature or claim to measure inward dissonance.

Primary outcome: mean pre-update squared prediction loss over the 400 examples, minus the identical-input no-hold clone. Secondary: independent final predictive MSE on 1,024 common evaluation examples. Record full per-step losses, selected coordinate, initial weights, evidence gaps and final weights.

H2 predicts positive added cost for disagreement: excess loss for disfavored holding minus excess loss for favored holding, at the same hold factor and seed/correlation. Also report within-seed covariance of gap and holding excess across the three correlations; do not convert it into causal evidence, since changing correlation also changes learned weights and sample geometry. Alignment and disagreement affect different coordinates, so equal factors are not guaranteed equal functional constraints. The no-hold reference and both factors expose but do not eliminate that identification limit.

Failure of the contrast to favor H2 rejects this operational prediction, not all concepts of commitment or dissonance. The favored condition may itself carry substantial holding cost; that directly challenges a blanket claim of little/no interference under agreement.

## H1: situated attribution must earn predictive value

For each seed, freeze a separate record of 128 correlated observations (rho=.95), including X, y and a factual description of that sampling episode. There is no evaluator-written accusation in the record. The same byte-serialized record is used at every reader state. Reader histories consist of 0, 32 and 400 correlated observations, then the same 400 plus 400 unconfounded observations. Their positions are learned weights, not assigned personality labels. This is a record of a misleading context, not yet a naturally discovered moral or semantic error.

Compute original-style base attribution |X'y-X'Xw| * sqrt(diag(X'X)). Compare three fixed rules: multiply by (1+|w|), divide by (1+|w|), or no reliance adjustment. Normalize for reporting; choose the top feature. No rule is called correct by definition.

For each candidate feature i, the record alone specifies a coordinate correction delta_i=(X'y-X'Xw)_i/(X'X)_ii. Apply that one correction to a diagnostic copy of the reader, then evaluate actual prediction loss on 1,024 separately sampled examples from the record's generating regime. Every rule faces the same examples. The selected feature's measured loss reduction is the actionable outcome. This replaces 'names the hidden true feature' with a consequence a learner could evaluate from labeled observations. The evaluation is independent samples from a deliberately matched historical regime; it is not unseen semantic transfer.

Primary H1 contrast: loss reduction under reliance-upweighting minus reduction without adjustment, averaged over reader states within seed. Also compare discounting. Report each reader state separately, top-feature changes, actual losses, and regret relative to the best measured coordinate action (an optimistic evaluation benchmark, never provided to the rule). A changed attribution alone is not support. Normalized attribution may change even when the top feature does not. Preserve negative gains and cases where every correction worsens performance; never score novelty as warrant.

## Integrity checks and stopping

Require identical shared input hashes and initial states across H2 arms, exact favored/disfavored equality under factor1, gradient locality, unchanged record bytes, no mutation of reader state by attribution/evaluation, proper paired scoring, and no hidden true-feature access in learner methods. Include boundary examples for the attribution variants and zero evidence. A pass of these checks verifies the instrument, not H1/H2. Run all declared seeds once without outcome-based stopping or hyperparameter selection. Technical repairs must be logged separately from hypothesis changes.

Original v0.1's artifacts remain historical. This version reports successful and unsuccessful operational predictions without relabeling either as proof of the main Raised, Not Rented mechanism.
