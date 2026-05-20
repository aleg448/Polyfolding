# CrystalProbe Public Demo Checklist

Use this checklist to evaluate the public artifact without granting it stronger scientific claims than it currently earns.

## Run

```powershell
python scripts\build_public_artifact.py
python scripts\check_public_artifact.py
```

Expected runtime: under five minutes on the dependency-light path.

## Required Dependencies

- Python 3.11+
- Core package dependencies from `pyproject.toml`
- No MACE, AIMNet2, UMA, fairchem, ASE, Docker, CCDC, or CSD dependency is required for the public demo path.

## Optional Scientific Backends

| Backend | Importable | Smoke status | Public-demo role |
|---|---:|---|---|
| `aimnet2` | `False` | `skipped` | optional MLIP inference smoke |
| `ase_cif` | `False` | `not_applicable` | CIF parsing support |
| `fastcsp` | `False` | `not_applicable` | future CSP complement |
| `mace_off` | `False` | `skipped` | optional MLIP inference smoke |
| `uma` | `False` | `not_implemented` | optional fairchem/UMA path |

## Expected Outputs

- `docs/public_demo.md` embeds reviewer-visible SVGs.
- `docs/assets/public_demo/*.svg` contains stable copied demo figures.
- `docs/public_demo_checklist.md` records this checklist.
- `docs/cases/cposs_ibp_candidate.md` records one stronger unverified example.
- `outputs/public_demo/*` contains regenerated local reports and ledgers, but remains ignored.
- `outputs/public_artifact_integrity.*` records the public artifact integrity check, but remains ignored.

## Claim Checks

- Claim gate decision: `blocked_headline_benchmark_claims_until_verified_records_exist`
- Seed pairs: `5`
- Evaluated ranking pairs: `0`
- Skipped ranking pairs: `5`
- Headline benchmark claims are blocked unless records are verified.
- Candidate figures must show `draft/unverified`, `candidate/unverified`, or equivalent labels.
- Optional backend availability is execution evidence only, not scientific validity evidence.

## Manual Review Before Public Sharing

- Confirm no raw CCDC/CSD-derived coordinate files are copied into `docs/`.
- Confirm every public case declares source-license, stability-evidence, disorder, curator, and reviewer blockers.
- Confirm no cross-backend absolute energy comparison is presented as calibrated thermodynamics.
- Confirm the public story remains reliability infrastructure, not a finished drug-discovery engine.

## Automated Integrity Gate

`python scripts\check_public_artifact.py` verifies required public paths, visible unverified labels, public release-boundary classification, and absence of coordinate-style files under the public asset directories. The command exits nonzero if any check is blocked.
