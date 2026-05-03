#!/usr/bin/env bash
set -euo pipefail

python -B -m pytest -q -p no:cacheprovider
python -m crystalprobe.benchmark.cli doctor
python scripts/smoke_backends.py --backend all

