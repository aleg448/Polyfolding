# CrystalProbe Blockers and Approval Queue

This file tracks work that cannot be completed inside the current local sandbox without additional libraries, data, model assets, credentials, or permissions.

## Current Blockers

- `ase` is installed in `.venv`. CIF parsing can now be tested when CIF files are present.
- MACE and PyTorch are installed in `.venv`; MACE-OFF checkpoint download/configuration still needs verification.
- MACE-OFF23 small checkpoint has been downloaded to the local MACE cache and CUDA smoke-tested. License is ASL/non-commercial, so use is research-only unless licensing changes.
- AIMNet is installed in `.venv`; default AIMNet2 model was downloaded and core CUDA inference works with `needs_dispersion=False`.
- AIMNet default DFT-D3 dispersion path failed on Windows because Torch/Triton support is missing; keep `needs_dispersion=False` locally or use Linux for full dispersion.
- `fairchem-core` is installed in isolated `.venv-fairchem` because it conflicts with MACE over `e3nn` in one environment.
- FastCSP/fairchem source is not cloned; only the packaged `fairchem-core` dependency is installed.
- CPOSS209 supplemental ZIP has been downloaded and MD5-verified locally under `data/sources/cposs209`; license is CC BY-NC 4.0.
- OMC25 public lightweight dataset metadata has been downloaded locally under `data/sources/omc25`.
- OMC25/UMA model repository is manually gated on Hugging Face; checkpoint download requires account-side license/access acceptance.
- GitHub remote creation/push requires a remote URL or GitHub CLI/token setup.
- Docker CLI is not installed or not on `PATH`; Linux container build cannot run yet.
- WSL is present as a launcher, but no usable Linux distro is available in this shell. Installing Ubuntu WSL may require Windows admin approval and possibly a restart.
- `HF_TOKEN` is not visible in the Codex shell. Set it in the shell/session that runs Docker or WSL commands.

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
