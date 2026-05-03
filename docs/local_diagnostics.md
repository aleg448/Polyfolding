# Local Diagnostics

CrystalProbe measurements should explain where a structure looks strained, not only rank total energies.

## Why

Two crystals can contain the same molecule but place stress in different local motifs: stretched bonds, compressed contacts, strained conformers, poor hydrogen-bond geometry, or force hot spots. A total lattice or cell energy can hide those causes.

## Current Scope

The initial implementation is model-agnostic and reports:

- high-force atoms from the MLIP force prediction;
- covalent-radius bond geometry outliers;
- short nonbonded contacts;
- diagnostic flags suitable for downstream fingerprinting.

These diagnostics are not a unique decomposition of energy into per-bond energies. Most MLIPs do not expose a physically unique bond-energy partition, so CrystalProbe treats local geometry as an explanatory layer beside the energy prediction.

## Command

Local diagnostics are included by default in CPOSS structure inference:

```powershell
python scripts\run_cposs_structure_inference.py --backend mace --family IBP --output outputs\cposs_ibp_mace.jsonl
python scripts\summarize_structure_predictions.py outputs\cposs_ibp_mace.jsonl
```

Use `--no-local-geometry` only for faster raw energy scans.
