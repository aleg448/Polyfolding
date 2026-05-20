"""Build the historical opportunity matrix report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.historical_opportunities import (
    historical_opportunity_markdown,
    historical_opportunity_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("data/curation/historical_opportunity_matrix_v0.1.json"),
    )
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_historical_opportunities.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_historical_opportunities.md"))
    args = parser.parse_args()

    report = historical_opportunity_report(json.loads(args.matrix.read_text(encoding="utf-8")))
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, historical_opportunity_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
