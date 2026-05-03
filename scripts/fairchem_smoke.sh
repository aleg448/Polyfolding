#!/usr/bin/env bash
set -euo pipefail

python -m crystalprobe.benchmark.cli doctor
python - <<'PY'
import torch
import fairchem

print("torch", torch.__version__, "cuda", torch.cuda.is_available(), torch.version.cuda)
print("fairchem import ok")
PY

