"""Summarize source-level structure prediction JSONL files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.structure_predictions import (
    load_structure_prediction_rows,
    summarize_relative_structure_energies,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    rows = load_structure_prediction_rows(args.predictions)
    summary = summarize_relative_structure_energies(rows)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
