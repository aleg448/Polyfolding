"""Summarize perturbation sensitivity prediction JSONL outputs."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.sensitivity_results import load_sensitivity_rows, sensitivity_markdown, summarize_sensitivity


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("predictions", nargs="+", type=Path)
    parser.add_argument("--json-out", type=Path, default=Path("outputs/ampetp_sensitivity_summary.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/ampetp_sensitivity_summary.md"))
    parser.add_argument("--title", default="AMPETP perturbation sensitivity summary")
    args = parser.parse_args()

    summary = summarize_sensitivity(load_sensitivity_rows(args.predictions))
    atomic_write_json(args.json_out, summary)
    atomic_write_text(args.md_out, sensitivity_markdown(summary, title=args.title))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
