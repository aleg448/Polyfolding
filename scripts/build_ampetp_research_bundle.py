"""Build a hashed AMPETP research-bundle manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.core.artifacts import (
    artifact_manifest_markdown,
    artifact_record,
    build_artifact_manifest,
    write_artifact_manifest,
)


ARTIFACTS = [
    ("outputs/ccdc_ampetp_extracted.cif", "extracted_cif"),
    ("outputs/ccdc_ampetp_mace.json", "mace_reference_prediction"),
    ("outputs/ccdc_ampetp_aimnet2.json", "aimnet2_reference_prediction"),
    ("outputs/ampetp_case_study_report.json", "case_study_json"),
    ("outputs/ampetp_case_study_report.md", "case_study_markdown"),
    ("outputs/ampetp_sensitivity_manifest.json", "sensitivity_manifest"),
    ("outputs/ampetp_sensitivity_mace.jsonl", "mace_sensitivity_predictions"),
    ("outputs/ampetp_sensitivity_aimnet2.jsonl", "aimnet2_sensitivity_predictions"),
    ("outputs/ampetp_sensitivity_summary.json", "sensitivity_summary_json"),
    ("outputs/ampetp_sensitivity_summary.md", "sensitivity_summary_markdown"),
    ("outputs/figures/ampetp_provenance_flow.svg", "figure_provenance"),
    ("outputs/figures/ampetp_structure_projection.svg", "figure_structure_projection"),
    ("outputs/figures/ampetp_backend_force_diagnostics.svg", "figure_backend_diagnostics"),
    ("outputs/figures/ampetp_sensitivity_energy_deltas.svg", "figure_sensitivity_deltas"),
    ("outputs/figures/ampetp_claim_guardrails.svg", "figure_claim_guardrails"),
]

OPTIONAL_ARTIFACTS = [
    ("outputs/ccdc_ampetp_uma.json", "uma_reference_prediction"),
    ("outputs/ampetp_sensitivity_uma.jsonl", "uma_sensitivity_predictions"),
]


REBUILD_COMMANDS = [
    "python scripts\\inspect_ccdc_cif.py data\\sources\\ccdc\\ccdc_amphetamine_phosphate_1036952-978407.cif --json-out outputs\\ccdc_amphetamine_bundle_index.json --extract-block AMPETP --extract-out outputs\\ccdc_ampetp_extracted.cif",
    "python scripts\\run_structure_inference.py data\\sources\\ccdc\\ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend mace --output outputs\\ccdc_ampetp_mace.json",
    "python scripts\\run_structure_inference.py data\\sources\\ccdc\\ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend aimnet2 --output outputs\\ccdc_ampetp_aimnet2.json",
    "docker compose run --rm crystalprobe-fairchem python scripts/run_structure_inference.py data/sources/ccdc/ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend uma --output outputs/ccdc_ampetp_uma.json",
    "python scripts\\build_ampetp_case_study.py",
    "python scripts\\build_ampetp_sensitivity_set.py",
    "python scripts\\run_sensitivity_inference.py outputs\\ampetp_sensitivity_manifest.json --backend mace --output outputs\\ampetp_sensitivity_mace.jsonl",
    "python scripts\\run_sensitivity_inference.py outputs\\ampetp_sensitivity_manifest.json --backend aimnet2 --output outputs\\ampetp_sensitivity_aimnet2.jsonl --continue-on-error",
    "docker compose run --rm crystalprobe-fairchem python scripts/run_sensitivity_inference.py outputs/ampetp_sensitivity_manifest.json --backend uma --output outputs/ampetp_sensitivity_uma.jsonl --continue-on-error",
    "python scripts\\summarize_sensitivity_predictions.py outputs\\ampetp_sensitivity_mace.jsonl outputs\\ampetp_sensitivity_aimnet2.jsonl outputs\\ampetp_sensitivity_uma.jsonl --json-out outputs\\ampetp_sensitivity_summary.json --md-out outputs\\ampetp_sensitivity_summary.md",
    "python scripts\\build_ampetp_figures.py",
    "python scripts\\build_ampetp_research_bundle.py",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, default=Path("outputs/ampetp_research_bundle_manifest.json"))
    parser.add_argument("--output-md", type=Path, default=Path("outputs/ampetp_research_bundle_manifest.md"))
    args = parser.parse_args()

    artifacts = ARTIFACTS + [(path, role) for path, role in OPTIONAL_ARTIFACTS if Path(path).exists()]
    records = [artifact_record(path, role=role) for path, role in artifacts]
    manifest = build_artifact_manifest(
        title="AMPETP CrystalProbe research bundle",
        artifacts=records,
        rebuild_commands=REBUILD_COMMANDS,
        notes=[
            "Raw CCDC/CSD source files remain local and are not included in this bundle.",
            "Generated perturbation CIFs are probes, not experimentally observed crystal forms.",
            "Energy deltas are interpreted within backend, relative to each backend reference prediction.",
        ],
    )
    write_artifact_manifest(args.output_json, manifest)
    args.output_md.write_text(artifact_manifest_markdown(manifest), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.output_json), "markdown": str(args.output_md)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
