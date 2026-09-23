# Topographic memory v0.4 — executed research battery

Start with FINDINGS.md and PROTOCOL.md. This is a runnable, declared model of
memory-dependent receiving dynamics. It is not a validation of the whole
Raised, Not Rented hypothesis or a claim of consciousness, love or redemption.

## Reproduce

Python 3.10+ and NumPy are required. The exact executed versions are in
results/manifest.json. From this directory:

```bash
python test_battery.py
python battery.py --out reproduced
python audit_results.py
```

The last command audits the supplied `results` directory. To audit the new run:

```bash
python -c "from audit_results import audit; import json; print(json.dumps(audit('reproduced'), indent=2))"
```

Compare `reproduced/summary.json` with `results/summary.json`. Exact byte
reproduction requires the same numerical environment. Source approvals also
bind the exact bytes of battery.py and PROTOCOL.md; editing either intentionally
changes the manifest and approval payloads. The signing key is public fixture
material, not a production credential. Do not use this as a security library.

## Contents

- battery.py: complete system and 32-history execution.
- test_battery.py: positive, negative and mutation integrity checks.
- audit_results.py: saved-trajectory audit independent of summary counters.
- PROTOCOL.md: equations, choices, expected scope, written before execution.
- results/: complete per-substep trajectories, per-window readouts, factual
  record samples, memory snapshots, approvals, manifest and aggregate summary.
- run_output.txt and test_output.txt: captured execution.
- CHANGELOG.md: implementation decisions and corrections.
- source_claude_v0_3.py: unmodified uploaded antecedent, for archaeology.

No component-withheld experimental arms were run. Test fixtures intentionally
exercise rejected paths and are never counted as natural-history findings.
The two parental conditions share 16 world tapes: there are 16 paired seed
units, not 32 independent replicates.
