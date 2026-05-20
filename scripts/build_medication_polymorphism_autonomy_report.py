"""Build autonomous medication polymorphism triage reports."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.medication_polymorphism import (
    medication_polymorphism_autonomy_markdown,
    medication_polymorphism_autonomy_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingestion", type=Path, default=Path("outputs/medication_cif_ingestion.json"))
    parser.add_argument("--measurements", type=Path, default=Path("outputs/medication_measurement_summary.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/medication_polymorphism_autonomy.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/medication_polymorphism_autonomy.md"))
    args = parser.parse_args()

    report = medication_polymorphism_autonomy_report(
        json.loads(args.ingestion.read_text(encoding="utf-8")),
        json.loads(args.measurements.read_text(encoding="utf-8")),
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, medication_polymorphism_autonomy_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
