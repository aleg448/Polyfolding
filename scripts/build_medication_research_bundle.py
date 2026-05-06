"""Build a hashed local-only medication research-bundle manifest."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.artifacts import (
    artifact_manifest_markdown,
    artifact_record,
    build_artifact_manifest,
    write_artifact_manifest,
)
from crystalprobe.core.io import atomic_write_text


ARTIFACTS = [
    ("outputs/medication_cif_ingestion.json", "medication_cif_ingestion_json"),
    ("outputs/medication_cif_ingestion.md", "medication_cif_ingestion_markdown"),
    ("outputs/medication_selected_block_extraction.json", "selected_block_extraction_json"),
    ("outputs/medication_measurement_summary.json", "medication_measurement_summary_json"),
    ("outputs/medication_measurement_summary.md", "medication_measurement_summary_markdown"),
    ("outputs/crystalprobe_source_acquisition.json", "source_acquisition_json"),
    ("outputs/crystalprobe_source_acquisition.md", "source_acquisition_markdown"),
    ("outputs/crystalprobe_fingerprint_artifact_plan.json", "fingerprint_artifact_plan_json"),
    ("outputs/crystalprobe_fingerprint_artifact_plan.md", "fingerprint_artifact_plan_markdown"),
    ("outputs/figures/medication_case_study_coverage.svg", "medication_case_study_figure"),
]

OPTIONAL_ARTIFACTS = [
    ("outputs/medication_measurements/modafinil_s_plus_241713_mace.json", "modafinil_mace_prediction"),
    ("outputs/medication_measurements/modafinil_s_plus_241713_aimnet2.json", "modafinil_aimnet2_prediction"),
    ("outputs/medication_measurements/modafinil_s_plus_241713_uma.json", "modafinil_uma_prediction"),
    ("outputs/medication_measurements/atomoxetine_hcl_1519130_mace.json", "atomoxetine_mace_prediction"),
    ("outputs/medication_measurements/atomoxetine_hcl_1519130_aimnet2.json", "atomoxetine_aimnet2_prediction"),
    ("outputs/medication_measurements/atomoxetine_hcl_1519130_uma.json", "atomoxetine_uma_prediction"),
    ("outputs/medication_measurements/methylphenidate_hcl_1453371_mace.json", "methylphenidate_mace_prediction"),
    ("outputs/medication_measurements/methylphenidate_hcl_1453371_aimnet2.json", "methylphenidate_aimnet2_prediction"),
    ("outputs/medication_measurements/methylphenidate_hcl_1453371_uma.json", "methylphenidate_uma_prediction"),
]

REBUILD_COMMANDS = [
    "python scripts\\build_source_acquisition_report.py",
    "python scripts\\build_medication_cif_ingestion_report.py --extract",
    "python scripts\\build_medication_figures.py",
    "python scripts\\build_fingerprint_artifact_plan.py",
    "python scripts\\build_medication_research_bundle.py",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=Path("outputs/medication_research_bundle_manifest.json"))
    parser.add_argument("--output-md", type=Path, default=Path("outputs/medication_research_bundle_manifest.md"))
    args = parser.parse_args()

    artifacts = [(path, role) for path, role in ARTIFACTS if Path(path).exists()]
    artifacts.extend((path, role) for path, role in OPTIONAL_ARTIFACTS if Path(path).exists())
    records = [artifact_record(path, role=role) for path, role in artifacts]
    manifest = build_artifact_manifest(
        title="CrystalProbe medication local-only research bundle",
        artifacts=records,
        rebuild_commands=REBUILD_COMMANDS,
        notes=[
            "Raw medication CIF bundles are local-only CCDC/CSD-derived source files and are not included in this manifest.",
            "Single-structure medication measurements are backend-behaviour evidence, not polymorph stability claims.",
            "MACE, AIMNet2, and UMA local-only measurements are now present for the selected medication proof blocks.",
        ],
    )
    write_artifact_manifest(args.output_json, manifest)
    atomic_write_text(args.output_md, artifact_manifest_markdown(manifest))
    print(json.dumps({"json": str(args.output_json), "markdown": str(args.output_md)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
