"""Build a small CPOSS bridge report from local structure summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.mini_benchmark import build_cposs_mini_benchmark_report, load_summary, mini_benchmark_markdown


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summary",
        action="append",
        type=Path,
        default=[],
        help="CPOSS summary JSON path; repeat for multiple families.",
    )
    parser.add_argument("--json-out", type=Path, default=Path("outputs/cposs_mini_benchmark_report.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/cposs_mini_benchmark_report.md"))
    args = parser.parse_args()

    summaries = args.summary or [
        Path("outputs/cposs_ibp_mace_summary.json"),
        Path("outputs/cposs_cbz_mace_summary.json"),
    ]
    report = build_cposs_mini_benchmark_report(
        [load_summary(path) for path in summaries],
        title="CPOSS local mini-benchmark bridge report",
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(mini_benchmark_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
