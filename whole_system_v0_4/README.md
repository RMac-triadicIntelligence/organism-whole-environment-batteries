# Whole-system exploratory run v0.4

An executed integrated operational proxy for Rusty's complete-environment research direction. Start with FINDINGS.md, then RUN_PROTOCOL.md. FOUNDATION.md preserves the Gospel anchors and six-study observational design from v0.3; RUN_PROTOCOL.md declares this implementation's narrower scope.

## Reproduce

Python 3.12.14 and NumPy 2.3.5 were used. From this directory:

```sh
python -m pip install -r requirements.txt
python run.py
python -m unittest -v test_system.py
```

The run overwrites results. Copy the delivered folder first to preserve reference outputs. No model API, credentials or network access is used by the experiment itself. Installation may need network access if NumPy is absent.

## Contents

- system.py: task generator, learner, retained records, conductor, authorizer and full encounter loop.
- run.py: 12-history execution and output capture.
- observer.py: v0.3 read-only history observer, unchanged.
- test_system.py: 12 instrument checks; constructed tests are not study histories.
- results/histories.json: all experience, disclosures, approvals, offerings, dynamics checkpoints, probes and rereadings.
- results/observations.json: trace observer output, retaining the original histories.
- results/inputs.npz: all generated world/probe input arrays; load with allow_pickle=False.
- results/summary.json: exact numerical summaries and protocol hash.
- run_output.txt and test_output.txt: captured outputs.
- MANIFEST.sha256: file hashes excluding caches and the manifest itself.

The state trajectory is captured at observation-window and assay endpoints, not every RK4 substep. Source and inputs permit deterministic reconstruction of the substeps. Observation t is an event index, not psychological time or a claim that logging itself constitutes dwelling. The actual learning and flow updates are in system.py.

The run has five signed offerings and zero releases. The positive release unit test does not change that count. Complete-system code means all declared proxy roles execute in one system; it does not mean every path was observed or every Gospel relationship is fully represented.
