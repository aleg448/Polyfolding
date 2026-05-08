"""Build a small CPOSS bridge report from local structure summaries."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
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
        Path("outputs/cposs_acr_mace_summary.json"),
        Path("outputs/cposs_ibp_mace_summary.json"),
        Path("outputs/cposs_cbz_mace_summary.json"),
        Path("outputs/cposs_flu_mace_summary.json"),
    ]
    report = build_cposs_mini_benchmark_report(
        [load_summary(path) for path in summaries],
        title="CPOSS local mini-benchmark bridge report",
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, mini_benchmark_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
