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
    has_cposs_candidate_cards: bool = False,
    has_cposs_evidence_workpack: bool = False,
    has_backend_disagreement: bool = False,
    has_cposs_backend_disagreement: bool = False,
    has_model_guardrails: bool = False,
    has_uncertainty_proxy: bool = False,
) -> dict[str, Any]:
    """Map current local artifacts to the four CrystalProbe roadmap deliverables."""

    docker_status = str(project_status.get("verification", {}).get("docker_status") or "")
    docker_verified = "verified" in docker_status or "ok" in docker_status
    uma_ampetp_verified = "uma_ampetp" in docker_status
    uma_ampetp_sensitivity_verified = "uma_ampetp_sensitivity" in docker_status
    uma_therapeutic_contrast_verified = "uma_therapeutic_contrast" in docker_status
    aimnet2_therapeutic_contrast_verified = "aimnet2_therapeutic_contrast" in docker_status
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
                "CPOSS candidate cards include claim boundaries and follow-up backend commands."
                if has_cposs_candidate_cards
                else "CPOSS AGI-assisted candidate cards are missing.",
                "CPOSS triage queue has curator-fillable evidence workpacks."
                if has_cposs_evidence_workpack
                else "CPOSS evidence workpack is missing.",
                "Prioritized CPOSS pairs have multi-backend disagreement evidence."
                if has_cposs_backend_disagreement
                else "Prioritized CPOSS pairs still need multi-backend disagreement evidence.",
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
                "Scale candidate-card measurements to additional CPOSS pairs after inspecting the first disagreement."
                if has_cposs_backend_disagreement
                else (
                    "Use candidate-card commands to run AIMNet2 and UMA on prioritized CPOSS pairs."
                    if has_cposs_candidate_cards
                    else "Create claim-safe candidate cards for prioritized CPOSS pairs."
                ),
                "Complete evidence workpack fields before promoting candidate pairs."
                if has_cposs_evidence_workpack
                else "Create curator-fillable evidence forms for candidate pairs.",
                "Inspect CPOSS backend-disagreement families before selecting paper-facing examples."
                if has_cposs_backend_disagreement
                else "Run candidate-card commands with AIMNet2 and UMA for top CPOSS pairs.",
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
                "AMPETP-vs-ibuprofen AIMNet2 contrast is available."
                if aimnet2_therapeutic_contrast_verified
                else "AMPETP-vs-ibuprofen AIMNet2 contrast is not yet recorded in project status.",
                "AMPETP-vs-ibuprofen UMA contrast is available."
                if uma_therapeutic_contrast_verified
                else "AMPETP-vs-ibuprofen UMA contrast is not yet recorded in project status.",
                "ChemRxiv-style preprint scaffold exists." if has_preprint_draft else "ChemRxiv-style preprint scaffold is missing.",
                "AMPETP backend-disagreement metrics are available."
                if has_backend_disagreement
                else "AMPETP backend-disagreement metrics are missing.",
                "High-priority CPOSS backend-disagreement metrics are available."
                if has_cposs_backend_disagreement
                else "High-priority CPOSS backend-disagreement metrics are missing.",
                "AMPETP has Docker/fairchem UMA reference and sensitivity measurements."
                if uma_ampetp_sensitivity_verified
                else (
                    "AMPETP has a Docker/fairchem UMA reference measurement."
                    if uma_ampetp_verified
                    else "UMA reference measurement for AMPETP is not yet recorded in project status."
                ),
            ],
            "remaining": [
                "Run AIMNet2 ibuprofen sensitivity in Linux/Docker."
                if not aimnet2_therapeutic_contrast_verified
                else "Scale AIMNet2 contrast to curated pairwise benchmark slices.",
                (
                    "Scale UMA contrast to curated pairwise benchmark slices."
                    if uma_therapeutic_contrast_verified
                    else (
                        "Extend UMA from AMPETP sensitivity into therapeutic contrast workflows."
                        if uma_ampetp_sensitivity_verified
                        else (
                            "Extend UMA from AMPETP reference measurement to sensitivity and therapeutic contrast workflows."
                            if uma_ampetp_verified
                            else "Add UMA measurements now that Hugging Face access is approved and Docker/fairchem initializes UMA."
                        )
                    )
                ),
                "Scale from pilot/bridge results to curated pairwise benchmark slices.",
                "Extend backend-disagreement metrics from AMPETP sensitivity to CPOSS candidate pairs."
                if has_backend_disagreement and not has_cposs_backend_disagreement
                else "Use the CPOSS disagreement report to choose bounded case-study examples."
                if has_cposs_backend_disagreement
                else "Build backend-disagreement metrics from the AMPETP sensitivity summary.",
            ],
        },
        {
            "deliverable": "Uncertainty-aware MLIP wrapper",
            "status": "core_primitives_ready",
            "evidence": [
                "Model-agnostic ensemble wrapper primitives exist.",
                "Sensitivity and contrast reports now provide empirical inputs for later calibration work.",
                "Backend-disagreement metrics provide the first uncalibrated uncertainty proxy."
                if has_backend_disagreement
                else "Backend-disagreement metrics are not yet available.",
                "Uncertainty proxy v0 aggregates AMPETP sensitivity and high-priority CPOSS disagreement evidence."
                if has_uncertainty_proxy
                else "Uncertainty proxy v0 report is missing.",
            ],
            "remaining": [
                "Calibrate uncertainty against verified benchmark pairs.",
                "Add OOD features grounded in model embeddings or chemistry descriptors.",
                "Define release API and documentation examples."
                if has_uncertainty_proxy
                else "Generate the uncertainty proxy v0 report from available backend-disagreement evidence.",
            ],
        },
        {
            "deliverable": "FastCSP usability layer",
            "status": "planned_not_integrated" if has_fastcsp_plan else "not_started",
            "evidence": [
                "FastCSP integration plan exists." if has_fastcsp_plan else "No FastCSP integration plan found.",
                "Docker/fairchem environment is documented and UMA access now verifies through fairchem.",
                "OMAT24/OMol25 model guardrails are documented before scientific use."
                if has_model_guardrails
                else "OMAT24/OMol25 model guardrail report is missing.",
            ],
            "remaining": [
                "Wire CrystalProbe uncertainty/reporting outputs into a fairchem/UMA-compatible workflow.",
                "Read FastCSP code and identify small upstream PR targets.",
                "Run a FastCSP-specific integration smoke test."
                if docker_verified
                else "Wire CrystalProbe uncertainty/reporting outputs into a FastCSP-compatible workflow.",
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
                "Keep Docker/fairchem verification current before release." if docker_verified else "Run Docker verification.",
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
