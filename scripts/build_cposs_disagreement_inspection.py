"""Build a focused CPOSS backend-disagreement inspection report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.cposs_inspection import (
    cposs_disagreement_inspection_markdown,
    cposs_disagreement_inspection_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--disagreement", type=Path, default=Path("outputs/cposs_high_priority_backend_disagreement.json"))
    parser.add_argument("--family", default="CBZ")
    parser.add_argument("--json-out", type=Path, default=Path("outputs/cposs_cbz_disagreement_inspection.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/cposs_cbz_disagreement_inspection.md"))
    args = parser.parse_args()

    report = cposs_disagreement_inspection_report(
        json.loads(args.disagreement.read_text(encoding="utf-8")),
        family=args.family,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(cposs_disagreement_inspection_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
