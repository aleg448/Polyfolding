"""Build promoted CPOSS benchmark records from completed evidence workpacks."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.cposs_promotion import cposs_promotion_markdown, cposs_promotion_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workpack", type=Path, default=Path("outputs/cposs_evidence_workpack.json"))
    parser.add_argument("--family-annotations", type=Path, default=Path("data/curation/cposs_family_annotations_v0.1.json"))
    parser.add_argument("--block-mapping", type=Path, default=Path("outputs/cposs_block_form_mapping.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/cposs_promotion_gate.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/cposs_promotion_gate.md"))
    parser.add_argument("--records-out", type=Path, default=Path("outputs/cposs_promoted_pairs.jsonl"))
    args = parser.parse_args()

    annotations = json.loads(args.family_annotations.read_text(encoding="utf-8")) if args.family_annotations.exists() else {}
    report = cposs_promotion_report(
        json.loads(args.workpack.read_text(encoding="utf-8")),
        family_annotations=annotations.get("families", annotations),
        block_mapping_report=json.loads(args.block_mapping.read_text(encoding="utf-8")) if args.block_mapping.exists() else None,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, cposs_promotion_markdown(report))
    atomic_write_text(
        args.records_out,
        "\n".join(json.dumps(record, sort_keys=True) for record in report["promoted_records"]) + ("\n" if report["promoted_records"] else ""),
    )
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out), "records": str(args.records_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
