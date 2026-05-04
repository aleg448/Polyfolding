# CrystalProbe Blockers and Approval Queue

This file tracks work that cannot be completed inside the current local sandbox without additional libraries, data, model assets, credentials, or permissions.

## Current Blockers

- `ase` is installed in `.venv`. CIF parsing can now be tested when CIF files are present.
- MACE and PyTorch are installed in `.venv`.
- MACE-OFF23 small checkpoint has been downloaded to the local MACE cache and CUDA smoke-tested. License is ASL/non-commercial, so use is research-only unless licensing changes.
- AIMNet is installed in `.venv`; default AIMNet2 model was downloaded and core CUDA inference works with `needs_dispersion=False`.
- AIMNet default DFT-D3 dispersion path failed on Windows because Torch/Triton support is missing; keep `needs_dispersion=False` locally or use Linux for full dispersion.
- `fairchem-core` is installed in isolated `.venv-fairchem` because it conflicts with MACE over `e3nn` in one environment.
- FastCSP/fairchem source is not cloned; only the packaged `fairchem-core` dependency is installed.
- CPOSS209 supplemental ZIP has been downloaded and MD5-verified locally under `data/sources/cposs209`; license is CC BY-NC 4.0.
- OMC25 public lightweight dataset metadata has been downloaded locally under `data/sources/omc25`.
- OMC25 ESEN checkpoint download from `facebook/OMC25` works with Docker `.env` token handoff and has been CUDA smoke-tested through fairchem.
- UMA access to `facebook/UMA` is accepted and Docker/fairchem initializes `uma-s-1p2` successfully.
- OMAT24 access to `facebook/OMAT24` is accepted and the model repository file inventory is verified.
- OMol25 access to `facebook/OMol25` is accepted and the model repository file inventory is verified.
- GitHub remote and identity are configured for `https://github.com/aleg448/Polyfolding.git`.
- Docker Desktop is installed and GPU passthrough works.
- Linux core and fairchem Docker images build and run.
- AIMNet full DFT-D3/Triton path works in Linux.
- `HF_TOKEN` is visible inside Docker Compose containers through `.env`.
- CPOSS209 source indexing and MACE structure-level inference both run locally and in the Linux core container.
- Lisdexamfetamine parent conformer is measured with MACE-OFF23 small and AIMNet2; crystalline dimesylate measurement still needs license-clean atom coordinates or CIF.
- Local CCDC/CSD multi-block CIF exports for amphetamine-family salts and ibuprofen are present under ignored `data/sources/ccdc/`.
- CCDC block extraction and measurement now work for amphetamine dihydrogen phosphate (`AMPETP`, CCDC 1102740) and ibuprofen (`ibuprofen`, CCDC 774097).

## Remaining User Input

- Locate or obtain license-compatible crystalline lisdexamfetamine dimesylate atom coordinates/CIF. Patent evidence exists, but the accessible patent text does not provide a reusable coordinate file.
- For CCDC/CSD: complete human validation in CCDC Access Structures or install/configure licensed CSD Python API access, then search the lisdexamfetamine terms and lattice window recorded in `docs/crystallographic_database_search.md`.
- Keep raw CCDC CIFs local and ignored unless the applicable CCDC/CSD license explicitly permits redistribution.

## Linux Environment Files Added

- `docker/core.Dockerfile`: CrystalProbe + ASE + MACE + AIMNet.
- `docker/fairchem.Dockerfile`: CrystalProbe + ASE + fairchem-core.
- `docker-compose.yml`: GPU-capable compose services for both stacks.
- `docs/linux_environment.md`: setup and run instructions.

## Approval Batch To Request

When ready for dependency installation and data acquisition, request approval for:

- Installing scientific Python dependencies into a project environment.
- Downloading or cloning open-source backend repositories.
- Downloading redistributable benchmark/source data.
- Downloading model checkpoints where licenses permit local use.
- Creating/pushing to a GitHub remote if publication is desired from this machine.
