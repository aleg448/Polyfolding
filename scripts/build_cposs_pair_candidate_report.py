"""Build a CPOSS pair-candidate curation queue from the local bridge report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.cposs_pairs import cposs_pair_candidate_markdown, cposs_pair_candidate_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cposs", type=Path, default=Path("outputs/cposs_mini_benchmark_report.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/cposs_pair_candidate_report.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/cposs_pair_candidate_report.md"))
    args = parser.parse_args()

    report = cposs_pair_candidate_report(json.loads(args.cposs.read_text(encoding="utf-8")))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(cposs_pair_candidate_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
