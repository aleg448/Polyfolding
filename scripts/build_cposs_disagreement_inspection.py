"""Build a focused CPOSS backend-disagreement inspection report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.cposs_inspection import (
    cposs_disagreement_inspection_markdown,
    cposs_disagreement_inspection_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--disagreement", type=Path, default=Path("outputs/cposs_high_priority_backend_disagreement.json"))
    parser.add_argument("--mace-summary", type=Path, default=Path("outputs/cposs_cbz_mace_summary.json"))
    parser.add_argument("--family", default="CBZ")
    parser.add_argument("--json-out", type=Path, default=Path("outputs/cposs_cbz_disagreement_inspection.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/cposs_cbz_disagreement_inspection.md"))
    args = parser.parse_args()

    report = cposs_disagreement_inspection_report(
        json.loads(args.disagreement.read_text(encoding="utf-8")),
        family=args.family,
        mace_summary=json.loads(args.mace_summary.read_text(encoding="utf-8")) if args.mace_summary.exists() else None,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, cposs_disagreement_inspection_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
