"""Summarize source-level structure prediction JSONL files."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json
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
        atomic_write_json(args.json_out, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
