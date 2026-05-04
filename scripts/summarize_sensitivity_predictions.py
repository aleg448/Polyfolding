"""Summarize perturbation sensitivity prediction JSONL outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.sensitivity_results import load_sensitivity_rows, sensitivity_markdown, summarize_sensitivity


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("predictions", nargs="+", type=Path)
    parser.add_argument("--json-out", type=Path, default=Path("outputs/ampetp_sensitivity_summary.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/ampetp_sensitivity_summary.md"))
    parser.add_argument("--title", default="AMPETP perturbation sensitivity summary")
    args = parser.parse_args()

    summary = summarize_sensitivity(load_sensitivity_rows(args.predictions))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(sensitivity_markdown(summary, title=args.title), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
