"""Build CPOSS block-to-experimental-form mapping readiness reports."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.cposs_block_mapping import cposs_block_mapping_markdown, cposs_block_mapping_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workpack", type=Path, default=Path("outputs/cposs_evidence_workpack.json"))
    parser.add_argument("--mapping-manifest", type=Path, default=Path("data/curation/cposs_block_form_mapping_v0.1.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/cposs_block_form_mapping.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/cposs_block_form_mapping.md"))
    args = parser.parse_args()

    manifest = json.loads(args.mapping_manifest.read_text(encoding="utf-8")) if args.mapping_manifest.exists() else {}
    report = cposs_block_mapping_report(
        json.loads(args.workpack.read_text(encoding="utf-8")),
        mapping_manifest=manifest,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, cposs_block_mapping_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
