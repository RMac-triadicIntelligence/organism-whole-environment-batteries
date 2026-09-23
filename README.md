# Organism / Whole-Environment Batteries

**Sealed organism / grace-boundary / whole-system / topographic-memory batteries from the Sep 2026 fork (manifest/SHA verified).**

Public shelf for organism-proxy review and hypothesis tests, grace-boundary and whole-system batteries, and topographic-memory archaeology. Seals verified after copy.

**Org / profile:** [RMac-triadicIntelligence](https://github.com/RMac-triadicIntelligence)

Licensor: [Soulshine](ABOUT_SOULSHINE.md) (501(c)(3)). License: [Apache-2.0](LICENSE). See [NOTICE](NOTICE).

## Packages

| Pack | Path | Seal | What |
|---|---|---|---|
| **organism v0.1 review** | [`organism_v0_1_review/`](organism_v0_1_review/) | `manifest.json` | Organism proxy review + evidential `*_results.json` / REPORT. |
| **organism hypothesis tests v0.2** | [`organism_hypothesis_tests_v0_2/`](organism_hypothesis_tests_v0_2/) | `MANIFEST.sha256` | Hypothesis tests with FINDINGS + results; includes reference archaeology. |
| **grace boundary v0.5** | [`grace_boundary_v0_5/`](grace_boundary_v0_5/) | `MANIFEST.sha256` | Grace-boundary battery; FINDINGS + results. |
| **whole system v0.4** | [`whole_system_v0_4/`](whole_system_v0_4/) | `MANIFEST.sha256` | Whole-system battery; FINDINGS + results. |
| **topographic memory v0.4** | [`topographic_memory_v0_4/`](topographic_memory_v0_4/) | `SHA256SUMS.json` | Topographic-memory battery; FINDINGS + results. May include `source_claude_v0_3.py` as shipped antecedent archaeology (output filenames inside that script do not imply a missing dependency tree). |

## Exclusions (not invented)

This shelf intentionally **omits**:

- `organism_v0_3` — runner recovered 2026-09-23; **byte-identical** to `topographic_memory_v0_4/source_claude_v0_3.py` (already in that pack’s seal). Named copy + fresh re-run under `organism_v0_3/` for discoverability; not a separate MANIFEST seal. Still missing: `cross_surface_battery.py`.
- `cross_surface_battery.py` / cross-surface loose scripts — unsealed or blocked (missing import); not invented here.
- `whole_cycle_observation_v0_3` — sealed but thin / non-evidential; SKIP per publish plan.

## Claim boundary

These are **simulation batteries**. Seals attest integrity of these runs — **not** consciousness, AGI, biological life, or moral truth. Read each package PROTOCOL / FINDINGS / RESULTS for scored hypotheses and verdicts.

## Sibling shelves

- [raised-not-rented](https://github.com/RMac-triadicIntelligence/raised-not-rented) — commons-kernel sealed batteries (v0.10–v0.13)
- [gospel-positional-reception](https://github.com/RMac-triadicIntelligence/gospel-positional-reception) — positional reception + junction gospel packs

## Verify seals

```bash
# MANIFEST.sha256 packs
(cd organism_hypothesis_tests_v0_2 && sha256sum -c MANIFEST.sha256)
(cd grace_boundary_v0_5 && sha256sum -c MANIFEST.sha256)
(cd whole_system_v0_4 && sha256sum -c MANIFEST.sha256)

# manifest.json (organism_v0_1_review)
python3 - <<'PY'
import json, hashlib, pathlib, sys
pack = pathlib.Path("organism_v0_1_review")
m = json.loads((pack / "manifest.json").read_text())
ok = True
for rel, expect in m["sha256"].items():
    got = hashlib.sha256((pack / rel).read_bytes()).hexdigest()
    print(("OK" if got == expect else "FAIL"), rel)
    ok &= got == expect
sys.exit(0 if ok else 1)
PY

# SHA256SUMS.json (topographic_memory_v0_4)
python3 - <<'PY'
import json, hashlib, pathlib, sys
pack = pathlib.Path("topographic_memory_v0_4")
m = json.loads((pack / "SHA256SUMS.json").read_text())
ok = True
for rel, expect in m.items():
    got = hashlib.sha256((pack / rel).read_bytes()).hexdigest()
    print(("OK" if got == expect else "FAIL"), rel)
    ok &= got == expect
sys.exit(0 if ok else 1)
PY
```
