# CrystalProbe Blockers and Approval Queue

This file tracks work that cannot be completed inside the current local sandbox without additional libraries, data, model assets, credentials, or permissions.

## Current Execution State

- `ase` is installed in `.venv`. CIF parsing can now be tested when CIF files are present.
- The project runner `.venv\Scripts\python.exe` imports `ase`, `torch`, `mace`, and `aimnet`.
- The isolated FAIR Chemistry runner `.venv-fairchem\Scripts\python.exe` imports `ase`, `torch`, and `fairchem`.
- The execution-unblock report is currently clear: Python dependency visibility, medication backend blockers, and measurement-queue runner blockers have no active blocking items.
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
- Lisdexamfetamine parent conformer is measured with MACE-OFF23 small and AIMNet2; crystalline dimesylate measurement is treated as unavailable for this project phase because no license-clean atom coordinates or CIF have been found.
- Local CCDC/CSD multi-block CIF exports for amphetamine-family salts and ibuprofen are present under ignored `data/sources/ccdc/`.
- CCDC block extraction and measurement now work for amphetamine dihydrogen phosphate (`AMPETP`, CCDC 1102740) and ibuprofen (`ibuprofen`, CCDC 774097).
- Local CCDC/CSD-derived medication CIF bundles are present for modafinil, atomoxetine hydrochloride, and methylphenidate hydrochloride. They are local-only until source redistribution terms are reviewed.
- Medication MACE, AIMNet2, and UMA measurements are complete for the selected local-only proof blocks: modafinil `(S)-(+)modafinil`, atomoxetine HCl `ATOMOXETINE_publ`, and methylphenidate HCl block `498`.
- Medication backend blockers have been cleared in `data/curation/medication_backend_blockers_v0.1.json`; the measurement summary now records three measured targets and zero blocked backend runs.

## Current Publication Blockers

- CPOSS candidates have not been promoted into verified benchmark pairs. The promotion gate still reports 0 promoted pairs, so the first publication milestone remains 20 verified pairs with stability evidence.
- Fingerprint ranking-accuracy and calibration figures remain blocked until verified pairs exist. Current medication and CPOSS outputs are case-study and inspection evidence, not benchmark headline metrics.
- Raw CCDC/CSD-derived CIFs and extracted coordinate-bearing blocks remain local-only unless license review explicitly permits redistribution.
- Human input is still needed for medication CIF public-reference policy and any future CCDC/CSD validation decision.

## Remaining User Input

- Treat crystalline lisdexamfetamine dimesylate as blocked for measurement unless a new license-compatible coordinate source appears. Patent evidence exists, but the accessible patent text does not provide a reusable coordinate file.
- Human CCDC/CSD validation is unlikely for this phase. Use `scripts/build_evidence_tier_report.py` to keep AGI-assisted, non-human-validated evidence explicitly downgraded from benchmark-grade claims.
- Keep raw CCDC CIFs local and ignored unless the applicable CCDC/CSD license explicitly permits redistribution.
- Confirm whether the downloaded medication CIF bundles can be referenced publicly or must remain strictly local-only.

## Linux Environment Files Added

- `docker/core.Dockerfile`: CrystalProbe + ASE + MACE + AIMNet.
- `docker/fairchem.Dockerfile`: CrystalProbe + ASE + fairchem-core.
- `docker-compose.yml`: GPU-capable compose services for both stacks.
- `docs/linux_environment.md`: setup and run instructions.

## Approval or Input Batch To Request

The dependency and local runner queue is clear. The next approval/input batch is scientific and release-oriented:

- Confirm whether local medication CIF bundles can be referenced publicly by source metadata only, or must remain strictly private/local.
- Attach experimental stability ordering, DOI or durable source URL, license decision, and disorder annotations for the first 20 CPOSS benchmark candidates.
- Decide whether to open a public release/PR that includes only source code, manifests, and generated non-coordinate reports while keeping raw CIFs ignored.
