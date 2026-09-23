# Organism v0.1 — execution and bounded review

11 September 2026. Supplied source executed unchanged with Python 3.12.14 and NumPy 2.3.5. The original console output matches exactly; the generated JSON matches the supplied JSON in every value. Eight seeds were run in each of four arms. No pass/fail test suite is defined in the original file.

## Reproduced outcomes

| Arm | Later trap capture, mean | Reported final excess loss |
| --- | ---: | ---: |
| Naive | 0.00702749 | 0.00000 |
| Erred, unreleased | 0.27530105 | 0.04475 |
| Restored | 0.00765987 | 0.00031 |
| Restored, record erased | 0.00765987 | 0.00031 |

Lower trap capture is the author's declared resistance measure. It measures a weight magnitude, not held-out task loss on the second trap. The column labeled final excess loss is the last sampled rolling-loss difference, at post-window step 875 of 900. The step300 reading precedes the release call, which occurs later in that loop iteration.

C1: top attribution changes in 8/8 erred and 8/8 restored runs. None of the 48 checkpoints in either arm names the committed trap feature, so warrant is 0/48 in both under the implemented rule. Changed attribution did not meet this instrument's own warrant criterion. That is not a general refutation of developmental reinterpretation; the attribution rule itself is a chosen proxy.

C2: restored minus naive mean trap capture is +0.00063238, not an advantage. The script's printed Prodigal criterion is a sign/threshold on this difference, not a statistical test. No uncertainty-based superiority or equivalence conclusion follows.

C3: restored and erased final weights are exactly identical for every seed, not merely equal after rounding. Subsequent observe() updates never read records or interpretations. Erasing the event leaves weights and sufficient statistics intact. The result establishes that this stored record is not load-bearing in the implemented learning path, not that meaningful memory is generally unnecessary. Other learned history remains present, so this is record erasure, not total memory erasure.

C4: removal of the commitment allows later ordinary learning to improve performance. The learning constraint is explicit: while committed, gradients on the trap feature and the evaluator-known TRUE_RULE are multiplied by 0.05. The adverse condition therefore includes an imposed handicap using privileged ground truth. commit_error() is called by the experiment after 400 samples rather than triggered by the organism's decision. In seed 0, the true feature weight at this forced commitment is 0.528579 and the trap's is 0.492455. The implementation does not establish that an organism independently chose the wrong rule.

C5: all eight authorized offerings take. Seed 0 required nudge drops from approximately 0.921 to 0.104 before release. The evidence statistics now depend on actual samples, rather than a direct scalar tilt schedule. But the reception threshold is explicitly defined as gap/(1+40*max(margin,0)), and taking is nudge>=required. That is a programmed gate, not an independently measured dynamical crossing. Only a sufficient fixed nudge is exercised in the reported offering panel.

## The shadow is not matched to the same post-window stream

World.sample(confounded=True) consumes an extra random draw during the confounded window. The shadow's unconfounded call does not. Despite equal initial seeds, their generators become offset. Immediately after the 400-sample window, both x and y differ between organism and shadow in all eight inspected seeds. A comparison of averages under the same distribution is still possible, but these are not paired identical-input trajectories. The discrepancy limits the claimed matched-shadow burden interpretation.

A proper stream-matched follow-up would generate shared base samples and noise once and transform only the designated confounded feature, or use independent synchronized streams for the confound injection. This review does not alter the supplied implementation or substitute corrected results for the original run.

## What is new, and what remains untested

This is a concrete move toward the main question: accumulated experience affects model weights and sufficient statistics, and a historical evidence snapshot is queried under changing weights. It is no longer merely a particle following a specified tilt target.

However, “no schedule anywhere” is inaccurate: the world deliberately changes the correlation regime after 400 observations, commitment is imposed there, and release is attempted at post-window step300. The distinction is experience-mediated state change under an authored environment schedule, not absence of schedules.

The archive has no causal role in later action. interpret() appends diagnostic attributions but changes neither the learner's weights nor its future learning rule. The code comment says reliance is discounted, but the formula multiplies by (1+abs(w)); it upweights rather than discounts reliance. This is a source discrepancy to resolve before treating attribution as a warranted reading.

release() removes the commitment mask but does not change weights or remove past loss measurements. A seed-0 check confirms both are unchanged at release itself. The later performance recovery does not establish instantaneous elimination of emergent functional burden. The stored event is also not structurally immutable: ErrorRecord is a mutable dataclass, resolved_by changes, and root() is a partial process-dependent Python hash. Historical evidence arrays are copied and not intentionally rewritten by this run, but cryptographic invariance is not enforced.

The verified junction is not integrated: approval is a Boolean, not a bound signature; realization and confession are not checked. Love, bilateral restorative change, truthful confession, and semantic reinterpretation are not exercised. These are scope boundaries, not invitations to replace the current learning question with another security detour.

The next meaningful design decision is what permitted causal role the preserved record should have in subsequent learning, without explicitly rewarding the desired answer. A clean matched stream would make the present performance comparison interpretable. Until then, the current negatives concern this implementation; they do not test away the original developmental hypothesis.

## Reproduction

Run the unmodified source copy from this folder:

    python organism.py

This writes organism_v0_1_results.json. Run supplemental checks with:

    python review.py

That preserves all checkpoints and burden curves omitted by the original JSON, tests exact restored/erased weight equality, checks the claimed matched stream, and observes the release operation. review.py initially needed explicit serialization of NumPy Boolean scalars; that reporting issue was corrected and the supplemental run repeated. No organism code or experimental parameter was changed.

The attached outputs and manifest identify the executed source and runtime. Original source hash: deee4dec1c824152377d1e8c829d2a8aecd8ca9a1354f00f3f7d1e460ba14dc3.
