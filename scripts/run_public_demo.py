"""Run the CrystalProbe public demo."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.insight.public_demo import (
    DEFAULT_MANIFEST,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PREDICTIONS,
    run_public_demo,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the public CrystalProbe demo report.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--backend-smoke", choices=["auto", "always", "never"], default="auto")
    parser.add_argument("--backend-timeout-seconds", type=int, default=90)
    args = parser.parse_args()

    report = run_public_demo(
        manifest=args.manifest,
        predictions=args.predictions,
        output_dir=args.output_dir,
        backend_smoke=args.backend_smoke,
        backend_timeout_seconds=args.backend_timeout_seconds,
    )
    print(json.dumps(report["outputs"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
