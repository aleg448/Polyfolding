"""Build medication CIF ingestion and local measurement reports."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.medication_cifs import (
    extract_selected_blocks,
    medication_cif_ingestion_markdown,
    medication_cif_ingestion_report,
    medication_measurement_markdown,
    medication_measurement_summary,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", type=Path, default=Path("data/curation/medication_cif_selection_v0.1.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/medication_cif_ingestion.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/medication_cif_ingestion.md"))
    parser.add_argument("--measurement-json-out", type=Path, default=Path("outputs/medication_measurement_summary.json"))
    parser.add_argument("--measurement-md-out", type=Path, default=Path("outputs/medication_measurement_summary.md"))
    parser.add_argument("--extract-json-out", type=Path, default=Path("outputs/medication_selected_block_extraction.json"))
    parser.add_argument("--measurement-dir", type=Path, default=Path("outputs/medication_measurements"))
    parser.add_argument("--backend-blockers", type=Path, default=Path("data/curation/medication_backend_blockers_v0.1.json"))
    parser.add_argument("--extract", action="store_true")
    args = parser.parse_args()

    selection = json.loads(args.selection.read_text(encoding="utf-8"))
    report = medication_cif_ingestion_report(selection)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, medication_cif_ingestion_markdown(report))

    blockers = json.loads(args.backend_blockers.read_text(encoding="utf-8")) if args.backend_blockers.exists() else {}
    measurement = medication_measurement_summary(selection, measurement_dir=args.measurement_dir, backend_blockers=blockers)
    atomic_write_json(args.measurement_json_out, measurement)
    atomic_write_text(args.measurement_md_out, medication_measurement_markdown(measurement))

    outputs = {
        "ingestion_json": str(args.json_out),
        "ingestion_markdown": str(args.md_out),
        "measurement_json": str(args.measurement_json_out),
        "measurement_markdown": str(args.measurement_md_out),
    }
    if args.extract:
        extraction = extract_selected_blocks(selection)
        atomic_write_json(args.extract_json_out, extraction)
        outputs["extraction_json"] = str(args.extract_json_out)
    print(json.dumps(outputs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
