# Linux Environment

Docker/WSL is the clean path for publication-grade CrystalProbe runs. The Windows environment is good for core smoke tests, but Linux should resolve the AIMNet/Triton issue and is the realistic target for fairchem/UMA.

## Current Local Status

- Docker CLI is not installed or not on `PATH`.
- WSL command is present, but no usable distro is currently available in this Codex shell.
- `HF_TOKEN` is not visible in this Codex shell, even though it may be set in another PowerShell session.

## Recommended Setup

Install Docker Desktop with WSL2 backend and NVIDIA GPU support. After Docker is available, run from the repo root:

```powershell
docker compose build crystalprobe-core
docker compose run --rm crystalprobe-core
docker compose run --rm crystalprobe-core bash scripts/linux_smoke.sh

docker compose build crystalprobe-fairchem
docker compose run --rm crystalprobe-fairchem bash scripts/fairchem_smoke.sh
```

GPU passthrough is validated through the Compose device reservation in `docker-compose.yml`; this Docker Compose version rejected `--gpus all` on `compose run`.

## Services

- `crystalprobe-core`: CrystalProbe, ASE, MACE, AIMNet, tests, backend smoke checks.
- `crystalprobe-fairchem`: CrystalProbe, ASE, fairchem-core, UMA/FastCSP-facing checks.

The split remains intentional because MACE and fairchem currently require incompatible `e3nn` versions.

## Hugging Face Token

Use an environment variable rather than writing tokens to files:

```powershell
$env:HF_TOKEN="hf_your_token_here"
```

The compose file passes `HF_TOKEN` through to the containers. Validate without printing the token:

```powershell
docker compose run --rm crystalprobe-fairchem python -c "import os; print(bool(os.environ.get('HF_TOKEN')))"
```

Alternatively, copy `.env.example` to `.env` and put the token there. Do not commit `.env`.

This was not visible in the Codex-run container during validation, so gated UMA checkpoint download is still waiting on this handoff.

## Validated Results

- Docker Desktop is available.
- NVIDIA GPU passthrough works in Linux containers.
- `crystalprobe-core` builds and passes tests.
- `crystalprobe-core` runs MACE-OFF and AIMNet on CUDA.
- AIMNet full DFT-D3/Triton path works in Linux.
- `crystalprobe-fairchem` builds and imports fairchem on CUDA.
- OMC25/UMA model metadata is visible but remains manually gated.

## WSL Alternative

If Docker Desktop is not desired, install Ubuntu for WSL:

```powershell
wsl --install -d Ubuntu
```

Then inside Ubuntu:

```bash
sudo apt update
sudo apt install -y git python3-venv python3-pip build-essential
cd /mnt/c/Users/PC1/Desktop/AGI_repo/Polyfolding
python3 -m venv .venv-linux
source .venv-linux/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
python -m pip install ase mace-torch "aimnet[ase]" huggingface_hub requests
python -B -m pytest -q -p no:cacheprovider
```
