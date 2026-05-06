"""Build backend-disagreement report for CPOSS candidate measurements."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.cposs_disagreement import cposs_backend_disagreement_markdown, cposs_backend_disagreement_report
from crystalprobe.insight.structure_predictions import load_structure_prediction_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mace", type=Path, default=Path("outputs/cposs_candidates_high_priority_mace.jsonl"))
    parser.add_argument("--aimnet2", type=Path, default=Path("outputs/cposs_candidates_high_priority_aimnet2.jsonl"))
    parser.add_argument("--uma", type=Path, default=Path("outputs/cposs_candidates_high_priority_uma.jsonl"))
    parser.add_argument("--title", default="CPOSS high-priority backend disagreement report")
    parser.add_argument("--json-out", type=Path, default=Path("outputs/cposs_high_priority_backend_disagreement.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/cposs_high_priority_backend_disagreement.md"))
    args = parser.parse_args()

    rows_by_backend = {
        "mace": load_structure_prediction_rows(args.mace),
        "aimnet2": load_structure_prediction_rows(args.aimnet2),
        "uma": load_structure_prediction_rows(args.uma),
    }
    report = cposs_backend_disagreement_report(rows_by_backend, title=args.title)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, cposs_backend_disagreement_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
