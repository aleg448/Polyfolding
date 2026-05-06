"""Build the AMPETP case-study report from measured backend outputs."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.case_study import build_single_structure_case_study, case_study_markdown, load_prediction


DEFAULT_PREDICTIONS = [
    Path("outputs/ccdc_ampetp_mace.json"),
    Path("outputs/ccdc_ampetp_aimnet2.json"),
]

OPTIONAL_PREDICTIONS = [
    Path("outputs/ccdc_ampetp_uma.json"),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction", action="append", type=Path, default=[])
    parser.add_argument("--curation", type=Path, default=Path("data/curation/ccdc_therapeutic_sources_v0.1.json"))
    parser.add_argument("--output-json", type=Path, default=Path("outputs/ampetp_case_study_report.json"))
    parser.add_argument("--output-md", type=Path, default=Path("outputs/ampetp_case_study_report.md"))
    args = parser.parse_args()

    prediction_paths = args.prediction or DEFAULT_PREDICTIONS + [path for path in OPTIONAL_PREDICTIONS if path.exists()]
    predictions = [load_prediction(path) for path in prediction_paths]
    source_record = _ampetp_source_record(args.curation)
    report = build_single_structure_case_study(
        predictions,
        title="AMPETP CCDC 1102740 CrystalProbe Case Study",
        source_record=source_record,
    )

    atomic_write_json(args.output_json, report)
    atomic_write_text(args.output_md, case_study_markdown(report))
    print(json.dumps({"json": str(args.output_json), "markdown": str(args.output_md)}, indent=2))
    return 0


def _ampetp_source_record(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    for record in data["records"]:
        if record.get("selected_block_id") == "AMPETP":
            return record
    raise ValueError(f"AMPETP source record not found in {path}")


if __name__ == "__main__":
    raise SystemExit(main())
