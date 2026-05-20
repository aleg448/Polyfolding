"""Build a roadmap-level CrystalProbe status report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.roadmap import roadmap_status_markdown, roadmap_status_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-status", type=Path, default=Path("outputs/crystalprobe_project_status.json"))
    parser.add_argument("--readiness", type=Path, default=Path("outputs/ampetp_readiness_report.json"))
    parser.add_argument("--cposs", type=Path, default=Path("outputs/cposs_mini_benchmark_report.json"))
    parser.add_argument("--preprint", type=Path, default=Path("outputs/crystalprobe_chemrxiv_preprint_draft.md"))
    parser.add_argument("--joss", type=Path, default=Path("papers/joss_paper.md"))
    parser.add_argument("--fastcsp-plan", type=Path, default=Path("docs/fastcsp_integration_plan.md"))
    parser.add_argument("--release-boundary", type=Path, default=Path("outputs/crystalprobe_release_boundary.json"))
    parser.add_argument("--cposs-pair-candidates", type=Path, default=Path("outputs/cposs_pair_candidate_report.json"))
    parser.add_argument("--cposs-pair-triage", type=Path, default=Path("outputs/cposs_pair_triage_report.json"))
    parser.add_argument("--cposs-candidate-cards", type=Path, default=Path("outputs/cposs_candidate_cards.json"))
    parser.add_argument("--cposs-evidence-workpack", type=Path, default=Path("outputs/cposs_evidence_workpack.json"))
    parser.add_argument("--cposs-block-mapping", type=Path, default=Path("outputs/cposs_block_form_mapping.json"))
    parser.add_argument("--backend-disagreement", type=Path, default=Path("outputs/ampetp_backend_disagreement.json"))
    parser.add_argument("--cposs-backend-disagreement", type=Path, default=Path("outputs/cposs_high_priority_backend_disagreement.json"))
    parser.add_argument("--cposs-disagreement-inspection", type=Path, default=Path("outputs/cposs_cbz_disagreement_inspection.json"))
    parser.add_argument("--source-discovery", type=Path, default=Path("outputs/crystalprobe_source_discovery.json"))
    parser.add_argument("--model-guardrails", type=Path, default=Path("outputs/fairchem_model_guardrails.json"))
    parser.add_argument("--uncertainty-proxy", type=Path, default=Path("outputs/crystalprobe_uncertainty_proxy_v0.json"))
    parser.add_argument("--substance-profiles", type=Path, default=Path("outputs/crystalprobe_substance_profiles.json"))
    parser.add_argument("--measurement-queue", type=Path, default=Path("outputs/crystalprobe_measurement_queue.json"))
    parser.add_argument("--medication-cif-ingestion", type=Path, default=Path("outputs/medication_cif_ingestion.json"))
    parser.add_argument("--medication-measurements", type=Path, default=Path("outputs/medication_measurement_summary.json"))
    parser.add_argument("--cposs-promotion-gate", type=Path, default=Path("outputs/cposs_promotion_gate.json"))
    parser.add_argument("--fingerprint-artifact-plan", type=Path, default=Path("outputs/crystalprobe_fingerprint_artifact_plan.json"))
    parser.add_argument("--environment-blockers", type=Path, default=Path("outputs/crystalprobe_environment_blockers.json"))
    parser.add_argument(
        "--medication-stereochemistry-dossier",
        type=Path,
        default=Path("outputs/medication_stereochemistry_dossier.json"),
    )
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_roadmap_status.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_roadmap_status.md"))
    args = parser.parse_args()
    cposs_promotion_gate = (
        json.loads(args.cposs_promotion_gate.read_text(encoding="utf-8")) if args.cposs_promotion_gate.exists() else None
    )
    fingerprint_artifact_plan = (
        json.loads(args.fingerprint_artifact_plan.read_text(encoding="utf-8")) if args.fingerprint_artifact_plan.exists() else None
    )
    environment_blockers = (
        json.loads(args.environment_blockers.read_text(encoding="utf-8")) if args.environment_blockers.exists() else None
    )
    cposs_block_mapping = (
        json.loads(args.cposs_block_mapping.read_text(encoding="utf-8")) if args.cposs_block_mapping.exists() else None
    )
    medication_stereochemistry_dossier = (
        json.loads(args.medication_stereochemistry_dossier.read_text(encoding="utf-8"))
        if args.medication_stereochemistry_dossier.exists()
        else None
    )

    report = roadmap_status_report(
        project_status=json.loads(args.project_status.read_text(encoding="utf-8")),
        readiness=json.loads(args.readiness.read_text(encoding="utf-8")),
        cposs_bridge=json.loads(args.cposs.read_text(encoding="utf-8")),
        cposs_promotion_gate=cposs_promotion_gate,
        cposs_block_mapping=cposs_block_mapping,
        fingerprint_artifact_plan=fingerprint_artifact_plan,
        environment_blockers=environment_blockers,
        medication_stereochemistry_dossier=medication_stereochemistry_dossier,
        has_preprint_draft=args.preprint.exists(),
        has_joss_draft=args.joss.exists(),
        has_fastcsp_plan=args.fastcsp_plan.exists(),
        has_release_boundary=args.release_boundary.exists(),
        has_cposs_pair_candidates=args.cposs_pair_candidates.exists(),
        has_cposs_pair_triage=args.cposs_pair_triage.exists(),
        has_cposs_candidate_cards=args.cposs_candidate_cards.exists(),
        has_cposs_evidence_workpack=args.cposs_evidence_workpack.exists(),
        has_cposs_block_mapping=args.cposs_block_mapping.exists(),
        has_backend_disagreement=args.backend_disagreement.exists(),
        has_cposs_backend_disagreement=args.cposs_backend_disagreement.exists(),
        has_cposs_disagreement_inspection=args.cposs_disagreement_inspection.exists(),
        has_source_discovery=args.source_discovery.exists(),
        has_model_guardrails=args.model_guardrails.exists(),
        has_uncertainty_proxy=args.uncertainty_proxy.exists(),
        has_substance_profiles=args.substance_profiles.exists(),
        has_measurement_queue=args.measurement_queue.exists(),
        has_medication_cif_ingestion=args.medication_cif_ingestion.exists(),
        has_medication_measurements=args.medication_measurements.exists(),
        has_cposs_promotion_gate=args.cposs_promotion_gate.exists(),
        has_fingerprint_artifact_plan=args.fingerprint_artifact_plan.exists(),
        has_environment_blockers=args.environment_blockers.exists(),
        has_medication_stereochemistry_dossier=args.medication_stereochemistry_dossier.exists(),
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, roadmap_status_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
