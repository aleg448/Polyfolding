"""Build a conservative release-boundary report for CrystalProbe artifacts."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.release import release_boundary_markdown, release_boundary_report


DEFAULT_REPO_PATHS = [
    "README.md",
    "BLOCKERS.md",
    "data/curation/cposs_family_annotations_v0.1.json",
    "data/curation/facebook_model_access_v0.1.json",
    "data/curation/medication_backend_blockers_v0.1.json",
    "data/curation/medication_cif_selection_v0.1.json",
    "data/curation/source_acquisition_attempts_v0.1.json",
    "data/curation/source_discovery_targets_v0.1.json",
    "docs/report_workflows.md",
    "docs/facebook_model_access.md",
    "docs/full_suite_plan.md",
    "docs/sources.md",
    "scripts/_path_bootstrap.py",
    "scripts/build_backend_disagreement_report.py",
    "scripts/build_measurement_queue.py",
    "scripts/build_cposs_backend_disagreement_report.py",
    "scripts/build_cposs_disagreement_inspection.py",
    "scripts/build_cposs_promoted_pairs.py",
    "scripts/build_cposs_candidate_cards.py",
    "scripts/build_evidence_tier_report.py",
    "scripts/build_environment_blockers_report.py",
    "scripts/build_execution_unblock_report.py",
    "scripts/build_fingerprint_artifact_plan.py",
    "scripts/build_handoff_report.py",
    "scripts/build_medication_figures.py",
    "scripts/build_medication_cif_ingestion_report.py",
    "scripts/build_medication_research_bundle.py",
    "scripts/build_model_guardrails_report.py",
    "scripts/build_project_status_dashboard.py",
    "scripts/build_publication_readiness_report.py",
    "scripts/build_release_boundary_report.py",
    "scripts/build_roadmap_status_report.py",
    "scripts/build_source_acquisition_report.py",
    "scripts/build_source_discovery_report.py",
    "scripts/build_substance_profiles.py",
    "scripts/build_uncertainty_proxy_report.py",
    "papers/ampetp_case_study.md",
    "papers/joss_paper.md",
    "src/crystalprobe/insight/backend_disagreement.py",
    "src/crystalprobe/core/io.py",
    "src/crystalprobe/insight/claims.py",
    "src/crystalprobe/insight/cposs_disagreement.py",
    "src/crystalprobe/insight/cposs_inspection.py",
    "src/crystalprobe/insight/cposs_pairs.py",
    "src/crystalprobe/insight/cposs_promotion.py",
    "src/crystalprobe/insight/evidence_tiers.py",
    "src/crystalprobe/insight/environment.py",
    "src/crystalprobe/insight/fingerprint_artifacts.py",
    "src/crystalprobe/insight/handoff.py",
    "src/crystalprobe/insight/medication_cifs.py",
    "src/crystalprobe/insight/measurement_queue.py",
    "src/crystalprobe/insight/model_guardrails.py",
    "src/crystalprobe/insight/publication.py",
    "src/crystalprobe/insight/release.py",
    "src/crystalprobe/insight/roadmap.py",
    "src/crystalprobe/insight/status.py",
    "src/crystalprobe/insight/source_acquisition.py",
    "src/crystalprobe/insight/source_discovery.py",
    "src/crystalprobe/insight/substance_profiles.py",
    "src/crystalprobe/insight/unblock.py",
    "src/crystalprobe/uncertainty/proxy.py",
    "tests/test_backend_disagreement.py",
    "tests/test_claims.py",
    "tests/test_cposs_disagreement.py",
    "tests/test_cposs_inspection.py",
    "tests/test_cposs_pairs.py",
    "tests/test_cposs_promotion.py",
    "tests/test_cposs_runner.py",
    "tests/test_evidence_tiers.py",
    "tests/test_environment.py",
    "tests/test_fingerprint_artifacts.py",
    "tests/test_handoff.py",
    "tests/test_io.py",
    "tests/test_measurement_queue.py",
    "tests/test_medication_cifs.py",
    "tests/test_model_guardrails.py",
    "tests/test_publication.py",
    "tests/test_release.py",
    "tests/test_report_workflows.py",
    "tests/test_roadmap.py",
    "tests/test_status.py",
    "tests/test_source_acquisition.py",
    "tests/test_source_discovery.py",
    "tests/test_substance_profiles.py",
    "tests/test_unblock.py",
    "tests/test_uncertainty_proxy.py",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, default=Path("outputs/ampetp_research_bundle_manifest.json"))
    parser.add_argument("--workflow-manifest", type=Path, default=Path("data/curation/report_workflows_v0.1.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_release_boundary.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_release_boundary.md"))
    args = parser.parse_args()

    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    workflow_manifest = json.loads(args.workflow_manifest.read_text(encoding="utf-8"))
    artifact_paths = DEFAULT_REPO_PATHS + [artifact["path"] for artifact in bundle.get("artifacts", [])]
    report = release_boundary_report(artifact_paths=artifact_paths, workflow_manifest=workflow_manifest)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, release_boundary_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
