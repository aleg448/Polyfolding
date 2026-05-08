"""Seed CPOSS block-to-form mapping manifest rows from the evidence workpack."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json
from crystalprobe.insight.cposs_block_mapping import seed_cposs_block_form_mapping_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workpack", type=Path, default=Path("outputs/cposs_evidence_workpack.json"))
    parser.add_argument("--manifest", type=Path, default=Path("data/curation/cposs_block_form_mapping_v0.1.json"))
    parser.add_argument("--out", type=Path, default=Path("data/curation/cposs_block_form_mapping_v0.1.json"))
    args = parser.parse_args()

    existing = json.loads(args.manifest.read_text(encoding="utf-8")) if args.manifest.exists() else {}
    before_count = _block_count(existing)
    seeded = seed_cposs_block_form_mapping_manifest(
        json.loads(args.workpack.read_text(encoding="utf-8")),
        mapping_manifest=existing,
    )
    atomic_write_json(args.out, seeded)
    print(
        json.dumps(
            {
                "manifest": str(args.out),
                "seeded": seeded["total_block_count"] - before_count,
                "total": seeded["total_block_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _block_count(manifest: dict) -> int:
    return sum(len(record.get("blocks", {})) for record in manifest.get("families", {}).values())


if __name__ == "__main__":
    raise SystemExit(main())
