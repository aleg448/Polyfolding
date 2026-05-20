"""Build the reviewer-facing public CrystalProbe artifact."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.insight.public_artifact import (
    DEFAULT_ASSET_DIR,
    DEFAULT_GALLERY_PATH,
    build_public_artifact,
)
from crystalprobe.insight.public_cases import (
    DEFAULT_CASE_ASSET_DIR,
    DEFAULT_CASE_DOC_PATH,
    DEFAULT_CHECKLIST_PATH,
    DEFAULT_PUBLIC_CASE_PATH,
)
from crystalprobe.insight.public_demo import DEFAULT_MANIFEST, DEFAULT_OUTPUT_DIR, DEFAULT_PREDICTIONS


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the public CrystalProbe demo artifact and gallery.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--gallery", type=Path, default=DEFAULT_GALLERY_PATH)
    parser.add_argument("--asset-dir", type=Path, default=DEFAULT_ASSET_DIR)
    parser.add_argument("--checklist", type=Path, default=DEFAULT_CHECKLIST_PATH)
    parser.add_argument("--public-case", type=Path, default=DEFAULT_PUBLIC_CASE_PATH)
    parser.add_argument("--case-output", type=Path, default=DEFAULT_CASE_DOC_PATH)
    parser.add_argument("--case-asset-dir", type=Path, default=DEFAULT_CASE_ASSET_DIR)
    parser.add_argument("--backend-smoke", choices=["auto", "always", "never"], default="auto")
    parser.add_argument("--backend-timeout-seconds", type=int, default=90)
    args = parser.parse_args()

    result = build_public_artifact(
        manifest=args.manifest,
        predictions=args.predictions,
        output_dir=args.output_dir,
        gallery_path=args.gallery,
        asset_dir=args.asset_dir,
        checklist_path=args.checklist,
        public_case_path=args.public_case,
        case_output_path=args.case_output,
        case_asset_dir=args.case_asset_dir,
        backend_smoke=args.backend_smoke,
        backend_timeout_seconds=args.backend_timeout_seconds,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
