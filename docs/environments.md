# Local Environments

CrystalProbe currently uses two local Python environments because the upstream ML stacks have incompatible `e3nn` requirements.

## `.venv`

Purpose: core CrystalProbe development, ASE CIF parsing, MACE-OFF, AIMNet.

Installed highlights:

- PyTorch 2.11.0+cu126
- ASE 3.28.0
- MACE 0.3.15 (`mace-torch`)
- AIMNet 0.2.0
- CrystalProbe editable install with tests

## `.venv-fairchem`

Purpose: fairchem, UMA, and FastCSP-facing experiments.

Installed highlights:

- PyTorch 2.8.0+cu126
- ASE 3.28.0
- fairchem-core 2.19.0

## Why Separate Environments

`mace-torch` currently requires `e3nn==0.4.4`, while `fairchem-core` requires `e3nn>=0.5`. Installing both into one environment causes pip resolution failure. Keep them isolated and exchange predictions through CrystalProbe JSON Lines prediction files.

