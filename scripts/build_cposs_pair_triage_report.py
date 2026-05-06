"""Build a curation triage report for CPOSS pair candidates."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.cposs_pairs import cposs_pair_triage_markdown, cposs_pair_triage_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=Path("outputs/cposs_pair_candidate_report.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/cposs_pair_triage_report.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/cposs_pair_triage_report.md"))
    args = parser.parse_args()

    report = cposs_pair_triage_report(json.loads(args.candidates.read_text(encoding="utf-8")))
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, cposs_pair_triage_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
