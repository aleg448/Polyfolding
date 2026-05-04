"""Roadmap-level status reports for CrystalProbe deliverables."""

from __future__ import annotations

from typing import Any


def roadmap_status_report(
    *,
    project_status: dict[str, Any],
    readiness: dict[str, Any],
    cposs_bridge: dict[str, Any],
    has_preprint_draft: bool,
    has_joss_draft: bool,
    has_fastcsp_plan: bool,
    has_release_boundary: bool = False,
    has_cposs_pair_candidates: bool = False,
    has_cposs_pair_triage: bool = False,
    has_cposs_evidence_workpack: bool = False,
) -> dict[str, Any]:
    """Map current local artifacts to the four CrystalProbe roadmap deliverables."""

    deliverables = [
        {
            "deliverable": "Polymorph-pair benchmark",
            "status": "partial_bridge_ready",
            "evidence": [
                f"CPOSS bridge report covers {cposs_bridge.get('structure_count')} structures across {cposs_bridge.get('family_count')} families.",
                "Benchmark schema and curation readiness checks exist.",
                "CPOSS bridge summaries are converted into adjacent pair-candidate records."
                if has_cposs_pair_candidates
                else "CPOSS pair-candidate report is missing.",
                "CPOSS pair candidates have a local evidence-review triage report."
                if has_cposs_pair_triage
                else "CPOSS pair-candidate triage report is missing.",
                "CPOSS triage queue has curator-fillable evidence workpacks."
                if has_cposs_evidence_workpack
                else "CPOSS evidence workpack is missing.",
                "Release-boundary report separates candidate public, review-required, and local-only artifacts."
                if has_release_boundary
                else "Release-boundary report is missing.",
            ],
            "remaining": [
                "Promote pair candidates into curated records after experimental stability evidence is attached."
                if has_cposs_pair_candidates
                else "Promote local structure summaries into curated pair records.",
                "Work through the triage queue to add experimental stability labels and citations."
                if has_cposs_pair_triage
                else "Add experimental stability labels and citations.",
                "Complete evidence workpack fields before promoting candidate pairs."
                if has_cposs_evidence_workpack
                else "Create curator-fillable evidence forms for candidate pairs.",
                "Human-review the release-boundary report before publishing CCDC-derived artifacts."
                if has_release_boundary
                else "Separate redistributable source records from restricted local CCDC evidence.",
            ],
        },
        {
            "deliverable": "Behavioural fingerprint paper",
            "status": "pilot_draft_ready" if has_preprint_draft and readiness.get("status") == "paper_pilot_ready" else "drafting",
            "evidence": [
                f"AMPETP readiness status is {readiness.get('status')}.",
                "AMPETP-vs-ibuprofen MACE contrast is available.",
                "ChemRxiv-style preprint scaffold exists." if has_preprint_draft else "ChemRxiv-style preprint scaffold is missing.",
            ],
            "remaining": [
                "Run AIMNet2 ibuprofen sensitivity in Linux/Docker.",
                "Add UMA once access is approved.",
                "Scale from pilot/bridge results to curated pairwise benchmark slices.",
            ],
        },
        {
            "deliverable": "Uncertainty-aware MLIP wrapper",
            "status": "core_primitives_ready",
            "evidence": [
                "Model-agnostic ensemble wrapper primitives exist.",
                "Sensitivity and contrast reports now provide empirical inputs for later calibration work.",
            ],
            "remaining": [
                "Calibrate uncertainty against verified benchmark pairs.",
                "Add OOD features grounded in model embeddings or chemistry descriptors.",
                "Define release API and documentation examples.",
            ],
        },
        {
            "deliverable": "FastCSP usability layer",
            "status": "planned_not_integrated" if has_fastcsp_plan else "not_started",
            "evidence": [
                "FastCSP integration plan exists." if has_fastcsp_plan else "No FastCSP integration plan found.",
                "Docker/fairchem environment is documented, but heartbeat work avoided Docker.",
            ],
            "remaining": [
                "Verify fairchem/UMA access.",
                "Read FastCSP code and identify small upstream PR targets.",
                "Wire CrystalProbe uncertainty/reporting outputs into a FastCSP-compatible workflow.",
            ],
        },
        {
            "deliverable": "Software paper",
            "status": "drafting" if has_joss_draft else "not_started",
            "evidence": [
                "JOSS draft exists." if has_joss_draft else "JOSS draft is missing.",
                "Local tests and generated reports demonstrate software artifact growth.",
            ],
            "remaining": [
                "Commit and push accumulated changes.",
                "Run Docker verification.",
                "Add installation and user documentation for the new report generators.",
            ],
        },
    ]
    return {
        "schema_version": "0.1.0",
        "status": "roadmap_active",
        "ampetp_status": project_status.get("ampetp", {}).get("readiness_status"),
        "local_verification": project_status.get("verification", {}).get("latest_local_test_summary"),
        "deliverables": deliverables,
    }


def roadmap_status_markdown(report: dict[str, Any]) -> str:
    """Render a roadmap status report as Markdown."""

    lines = [
        "# CrystalProbe Roadmap Status",
        "",
        f"- Status: `{report['status']}`",
        f"- AMPETP: `{report['ampetp_status']}`",
        f"- Latest local verification: `{report['local_verification']}`",
        "",
        "## Deliverables",
        "",
    ]
    for item in report["deliverables"]:
        lines.extend(
            [
                f"### {item['deliverable']}",
                "",
                f"- Status: `{item['status']}`",
                "- Evidence:",
            ]
        )
        lines.extend(f"  - {evidence}" for evidence in item["evidence"])
        lines.append("- Remaining:")
        lines.extend(f"  - {remaining}" for remaining in item["remaining"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
