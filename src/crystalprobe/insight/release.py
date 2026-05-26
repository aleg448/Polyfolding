"""Release-boundary reports for CrystalProbe research artifacts."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class ReleaseRecord:
    """One artifact classified by release boundary."""

    path: str
    category: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def release_boundary_report(
    *,
    artifact_paths: Iterable[str],
    workflow_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify local artifacts by conservative publication boundary."""

    paths = {_normalize_path(path) for path in artifact_paths}
    if workflow_manifest:
        for workflow in workflow_manifest.get("workflows", []):
            paths.update(_normalize_path(path) for path in workflow.get("primary_outputs", []))
    records = [_classify(path) for path in sorted(paths)]
    counts = Counter(record.category for record in records)
    return {
        "schema_version": "0.1.0",
        "status": "release_boundary_recorded",
        "counts": dict(sorted(counts.items())),
        "records": [record.as_dict() for record in records],
        "policy": [
            "candidate_public artifacts are source, documentation, tests, and manuscript scaffolds that do not embed gated coordinates.",
            "license_review_required artifacts are CCDC-derived reports, figures, manifests, or model measurements that need human license review before sharing.",
            "local_only artifacts include raw, extracted, or generated coordinate files from gated CCDC/CSD sources.",
        ],
    }


def release_boundary_markdown(report: dict[str, Any]) -> str:
    """Render a release-boundary report as Markdown."""

    lines = [
        "# CrystalProbe Release Boundary Report",
        "",
        f"- Status: `{report['status']}`",
        "",
        "## Counts",
        "",
    ]
    for category, count in sorted(report["counts"].items()):
        lines.append(f"- `{category}`: `{count}`")
    lines.extend(
        [
            "",
            "## Policy",
            "",
        ]
    )
    lines.extend(f"- {line}" for line in report["policy"])
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "| Category | Path | Reason |",
            "|---|---|---|",
        ]
    )
    for record in report["records"]:
        lines.append(f"| `{record['category']}` | `{record['path']}` | {record['reason']} |")
    return "\n".join(lines).rstrip() + "\n"


def _classify(path: str) -> ReleaseRecord:
    normalized = _normalize_path(path)
    suffix = Path(normalized).suffix.lower()
    name = Path(normalized).name.lower()
    if _is_local_only_coordinate(normalized, suffix):
        return ReleaseRecord(
            path=path,
            category="local_only",
            reason="Coordinate-bearing gated CCDC/CSD source or extracted/generated CIF; keep local unless the license explicitly permits redistribution.",
        )
    if normalized in {"outputs/crystalprobe_evidence_tiers.json", "outputs/crystalprobe_evidence_tiers.md"}:
        return ReleaseRecord(
            path=path,
            category="candidate_public",
            reason="Evidence-tier policy output contains claim-boundary metadata, not raw gated coordinates.",
        )
    if normalized in {
        "outputs/crystalprobe_backend_ready_inputs.json",
        "outputs/crystalprobe_backend_ready_inputs.md",
        "outputs/crystalprobe_backend_ready_inputs.sqlite",
        "outputs/crystalprobe_backend_smoke.json",
        "outputs/crystalprobe_backend_smoke.md",
        "outputs/crystalprobe_backend_smoke.sqlite",
        "outputs/crystalprobe_conformer_generation.json",
        "outputs/crystalprobe_conformer_generation.md",
        "outputs/crystalprobe_conformer_generation.sqlite",
        "outputs/crystalprobe_energy_verification.json",
        "outputs/crystalprobe_energy_verification.md",
        "outputs/crystalprobe_evidence_atlas.json",
        "outputs/crystalprobe_evidence_atlas.md",
        "outputs/crystalprobe_evidence_atlas.sqlite",
        "outputs/crystalprobe_molecule_bug_hunt.json",
        "outputs/crystalprobe_molecule_bug_hunt.md",
        "outputs/crystalprobe_molecule_bug_hunt.sqlite",
        "outputs/crystalprobe_tentative_molecule_benchmark.json",
        "outputs/crystalprobe_tentative_molecule_benchmark.md",
        "outputs/crystalprobe_tentative_molecule_benchmark.sqlite",
    }:
        return ReleaseRecord(
            path=path,
            category="candidate_public",
            reason="Backend-ready input, backend-smoke, conformer-generation, energy, evidence-atlas, molecule bug-hunt, or tentative molecule-benchmark database contains normalized metadata, QA fixtures, hashes, claim gates, links, and release categories without raw gated-coordinate payloads.",
        )
    if normalized in {
        "outputs/crystalprobe_environment_blockers.json",
        "outputs/crystalprobe_environment_blockers.md",
        "outputs/crystalprobe_execution_unblock_report.json",
        "outputs/crystalprobe_execution_unblock_report.md",
        "outputs/crystalprobe_handoff_summary.json",
        "outputs/crystalprobe_handoff_summary.md",
        "outputs/crystalprobe_active_evidence_triage.json",
        "outputs/crystalprobe_active_evidence_triage.md",
        "outputs/crystalprobe_evidence_packet.json",
        "outputs/crystalprobe_evidence_packet.md",
        "outputs/crystalprobe_evidence_resolution.json",
        "outputs/crystalprobe_evidence_resolution.md",
        "outputs/crystalprobe_historical_opportunities.json",
        "outputs/crystalprobe_historical_opportunities.md",
        "outputs/crystalprobe_historical_research_modules.json",
        "outputs/crystalprobe_historical_research_modules.md",
        "outputs/crystalprobe_molecule_viewers.json",
        "outputs/crystalprobe_molecule_viewers.md",
        "outputs/crystalprobe_project_status.json",
        "outputs/crystalprobe_project_status.md",
        "outputs/crystalprobe_publication_readiness.json",
        "outputs/crystalprobe_publication_readiness.md",
        "outputs/crystalprobe_release_boundary.json",
        "outputs/crystalprobe_release_boundary.md",
        "outputs/crystalprobe_report_consistency.json",
        "outputs/crystalprobe_report_consistency.md",
        "outputs/crystalprobe_research_cycle.json",
        "outputs/crystalprobe_research_cycle.md",
        "outputs/crystalprobe_risk_register.json",
        "outputs/crystalprobe_risk_register.md",
        "outputs/crystalprobe_roadmap_status.json",
        "outputs/crystalprobe_roadmap_status.md",
        "outputs/crystalprobe_status_chain.json",
    }:
        return ReleaseRecord(
            path=path,
            category="candidate_public",
            reason="Execution, roadmap, publication-readiness, risk, handoff, status-chain, or active-environment report contains status metadata, not gated coordinates.",
        )
    if normalized in {
        "outputs/medication_research_bundle_manifest.json",
        "outputs/medication_research_bundle_manifest.md",
    }:
        return ReleaseRecord(
            path=path,
            category="license_review_required",
            reason="Medication bundle manifest hashes local CCDC/CSD-derived measurements; useful for internal review but requires source-license review before public sharing.",
        )
    if normalized.startswith("outputs/figures/medication_") and suffix == ".svg":
        return ReleaseRecord(
            path=path,
            category="license_review_required",
            reason="Medication figure summarizes CCDC/CSD-derived local measurements or claim scopes and requires source-license review before public sharing.",
        )
    if normalized.startswith(("src/", "scripts/", "tests/", "docs/", "data/curation/", "data/public_cases/")) or normalized in {
        "README.md",
        "BLOCKERS.md",
        "CASE_STUDY.md",
        "pyproject.toml",
    }:
        return ReleaseRecord(
            path=path,
            category="candidate_public",
            reason="Repository source, documentation, test, or curation metadata path intended for publication review.",
        )
    if normalized.startswith("papers/"):
        return ReleaseRecord(
            path=path,
            category="candidate_public",
            reason="Manuscript scaffold with claim guardrails and no raw CCDC coordinate file.",
        )
    if normalized.startswith("outputs/"):
        if name.endswith((".svg", ".md")):
            return ReleaseRecord(
                path=path,
                category="license_review_required",
                reason="Generated CCDC-derived report or figure; review source-license implications before public sharing.",
            )
        return ReleaseRecord(
            path=path,
            category="license_review_required",
            reason="Generated CCDC-derived machine-readable artifact; review source-license implications before public sharing.",
        )
    return ReleaseRecord(
        path=path,
        category="review_required",
        reason="Unrecognized artifact path; classify manually before sharing.",
    )


def _is_local_only_coordinate(path: str, suffix: str) -> bool:
    if path.startswith("data/sources/ccdc/"):
        return True
    if suffix == ".cif" and path.startswith("outputs/"):
        return True
    if "/ampetp_sensitivity/" in path and suffix == ".cif":
        return True
    if "/ibuprofen_sensitivity/" in path and suffix == ".cif":
        return True
    return False


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/")
