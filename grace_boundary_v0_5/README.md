# Grace boundary diagnostic v0.5

A separate test battery implementing the suggested investigation of five actual offering states. Start with FINDINGS.md, then PROTOCOL.md.

## Reproduce

Python 3.12.14 and NumPy 2.3.5 were used. From this directory:

```sh
python -m pip install -r requirements.txt
python battery.py
python -m unittest -v test_battery.py
```

Copy the directory first to preserve delivered results. The experiment uses no external APIs or credentials. Runtime is a few seconds on the original environment. Numerical details can vary by platform.

## Files

- battery.py: exact original replay, state recovery, signed diagnostic branches, root solver and trajectory observations.
- test_battery.py: 12 meaningful checks, including positive branches and a reject-everything mutant.
- reference/: unchanged original v0.4 system, observer and recorded histories.
- results/snapshots.json: recovered pre-offering states, original envelopes/signatures, separatrix distances and later recorded tilts.
- results/summary.json: all branch metrics, newly signed envelopes and post-release states.
- results/trajectories.json: every integration substep and tilt update, keyed by organism/dose/continuation.
- run_output.txt and test_output.txt: recorded execution output.
- MANIFEST.sha256: package file hashes excluding caches and the manifest itself.

Twenty branches come from five historical states; forty scalar continuation observations share those branches. Above-boundary doses are selected by the experimenter using the known dynamics. Do not call this spontaneous readiness or forty independent successes. Recorded continuation is not a new full-system run after release.

The observer and original engine remain unchanged. The diagnostic Branch class explicitly changes impulse configuration and the release criterion. This distinction is documented rather than described as a harness-only patch.
