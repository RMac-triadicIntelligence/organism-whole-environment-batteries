# Organism hypothesis tests v0.2

Start with FINDINGS.md and PROTOCOL.md, then review core.py, run.py and test_integrity.py. This version tests two prospective interpretations of the prior organism experiment; it does not modify the constitutional junction.

## Reproduce

Python 3.12.14 and NumPy 2.3.5 were used. In this directory:

```sh
python -m pip install -r requirements.txt
python run.py
python -m unittest discover -s . -p 'test_*.py' -v
```

The run rewrites results in place. Copy the directory first if preserving the delivered files for comparison. No network calls, credentials or model API are used by the experiment. NumPy numerical details can differ across platforms; compare arrays and reported values rather than requiring identical ZIP container bytes.

## Contents

- PROTOCOL.md: choices recorded before running this version.
- core.py: learner, immutable record, attribution and diagnostic actions.
- run.py: all data generation, experiment arms and paired summaries.
- test_integrity.py: 12 post-run instrument checks, including full H2 replay.
- results/: trial CSVs, seed contrasts, full input/trajectory NPZ, record roots, summaries and test log.
- run_output.txt: console summary from the experiment.
- reference/: original uploaded v0.1 source and reported outputs, unchanged, for archaeology only.
- MANIFEST.sha256: hashes of package contents, excluding this manifest and caches.

The NPZ is readable with numpy.load(..., allow_pickle=False). The h2_trials array_prefix identifies loss and initial/final weight arrays. H1 keys group each seed's fixed record, reader history, evaluation samples and reader weights. Record description and roots are saved in record_roots.json. The experiment's learner never receives the world's signal index.

This is a self-contained local experiment. Passing integrity tests is not a finding about love, restoration or long-horizon intelligence.
