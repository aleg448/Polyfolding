"""Risk-register reports for CrystalProbe claim and release readiness."""

from __future__ import annotations

from typing import Any


def risk_register_report(
    *,
    publication_readiness: dict[str, Any],
    release_boundary: dict[str, Any],
    cposs_promotion: dict[str, Any],
    cposs_block_mapping: dict[str, Any],
    fingerprint_plan: dict[str, Any],
    cposs_promotion_burndown: dict[str, Any] | None = None,
    medication_stereochemistry: dict[str, Any] | None = None,
    medication_stereochemistry_dossier: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a consolidated risk register from generated readiness reports."""

    risks = [
        _overclaiming_risk(cposs_promotion, cposs_block_mapping, fingerprint_plan, cposs_promotion_burndown or {}),
        _licensing_risk(release_boundary),
        _model_energy_risk(fingerprint_plan),
        _medication_stereochemistry_risk(
            medication_stereochemistry or {},
            fingerprint_plan,
            medication_stereochemistry_dossier or {},
        ),
        _fastcsp_positioning_risk(publication_readiness),
    ]
    return {
        "schema_version": "0.1.0",
        "status": "risk_register_recorded",
        "risk_count": len(risks),
        "open_risk_count": sum(1 for risk in risks if risk["status"] != "mitigated"),
        "critical_risk_count": sum(1 for risk in risks if risk["severity"] == "critical" and risk["status"] != "mitigated"),
        "risks": risks,
        "policy": [
            "The risk register is a release-control artifact; source reports remain canonical.",
            "A risk can be mitigated only by generated evidence, not by optimistic prose.",
            "CrystalProbe should remain an audit, curation, calibration, and claim-readiness layer around CSP outputs.",
        ],
    }


def risk_register_markdown(report: dict[str, Any]) -> str:
    """Render the risk register as Markdown."""

    lines = [
        "# CrystalProbe Risk Register",
        "",
        f"- Status: `{report['status']}`",
        f"- Risks: `{report['risk_count']}`",
        f"- Open risks: `{report['open_risk_count']}`",
        f"- Open critical risks: `{report['critical_risk_count']}`",
        "",
        "## Risks",
        "",
        "| Risk | Severity | Status | Evidence | Next Mitigation |",
        "|---|---|---|---|---|",
    ]
    for risk in report["risks"]:
        lines.append(
            f"| `{risk['risk_id']}` | `{risk['severity']}` | `{risk['status']}` | "
            f"{risk['evidence']} | {risk['next_mitigation']} |"
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _overclaiming_risk(
    cposs_promotion: dict[str, Any],
    cposs_block_mapping: dict[str, Any],
    fingerprint_plan: dict[str, Any],
    cposs_promotion_burndown: dict[str, Any],
) -> dict[str, str]:
    promoted = int(cposs_promotion.get("promoted_count", 0))
    mapped = int(cposs_promotion.get("literature_mapped_count", 0))
    mapping_ready = int(cposs_block_mapping.get("candidate_mapping_ready_count", 0))
    burndown_selected = int(cposs_promotion_burndown.get("selected_candidate_count", 0))
    burndown_blocks = int(cposs_promotion_burndown.get("selected_block_count", 0))
    burndown_remaining = int(cposs_promotion_burndown.get("remaining_to_target", 20))
    blocked_figures = [
        row.get("figure_id")
        for row in fingerprint_plan.get("figures", [])
        if row.get("status") != "ready"
    ]
    status = "mitigated" if promoted >= 20 and not blocked_figures else "open"
    return {
        "risk_id": "overclaiming_candidate_evidence",
        "severity": "critical",
        "status": status,
        "evidence": (
            f"{promoted} promoted pairs, {mapped} literature-mapped candidates, "
            f"{mapping_ready} mapping-ready candidates, {len(blocked_figures)} blocked fingerprint figures, "
            f"{burndown_selected} burn-down candidates covering {burndown_blocks} block rows for "
            f"{burndown_remaining} remaining first-milestone pairs."
        ),
        "next_mitigation": "Use the CPOSS promotion burn-down to lock selected block rows, then rerun the promotion gate until 20 verified pairs exist.",
    }


def _licensing_risk(release_boundary: dict[str, Any]) -> dict[str, str]:
    counts = release_boundary.get("counts") or {}
    review_required = int(counts.get("license_review_required", 0))
    local_only = int(counts.get("local_only", 0))
    status = "mitigated" if review_required == 0 and local_only == 0 else "open"
    return {
        "risk_id": "ccdc_csd_license_boundary",
        "severity": "critical",
        "status": status,
        "evidence": f"{review_required} license-review-required artifacts and {local_only} local-only artifacts.",
        "next_mitigation": "Keep coordinate-bearing and coordinate-derived artifacts out of public release until license review clears them.",
    }


def _model_energy_risk(fingerprint_plan: dict[str, Any]) -> dict[str, str]:
    calibration_figures = [
        row
        for row in fingerprint_plan.get("figures", [])
        if "calibration" in str(row.get("figure_id", "")) and row.get("status") == "ready"
    ]
    status = "watch" if not calibration_figures else "mitigated"
    return {
        "risk_id": "cross_backend_energy_interpretation",
        "severity": "high",
        "status": status,
        "evidence": (
            "No ready uncertainty-calibration figure is recorded."
            if not calibration_figures
            else "Uncertainty-calibration figure is marked ready."
        ),
        "next_mitigation": "Treat MACE, AIMNet2, and UMA disagreement as inspection evidence until calibrated against verified pairs.",
    }


def _medication_stereochemistry_risk(
    medication_stereochemistry: dict[str, Any],
    fingerprint_plan: dict[str, Any],
    medication_stereochemistry_dossier: dict[str, Any],
) -> dict[str, str]:
    enantiomer_targets = int(medication_stereochemistry.get("enantiomer_scope_target_count", 0))
    rankable_enantiomer_targets = int(medication_stereochemistry.get("rankable_enantiomer_scope_target_count", 0))
    dossier_count = int(medication_stereochemistry_dossier.get("dossier_count", 0))
    dossier_ready = int(medication_stereochemistry_dossier.get("ready_for_claim_scope_count", 0))
    figure_ready = any(
        row.get("figure_id") == "medication_stereochemistry" and row.get("status") == "ready"
        for row in fingerprint_plan.get("figures", [])
    )
    blockers = [
        blocker
        for target in medication_stereochemistry.get("targets", [])
        for blocker in target.get("blockers", [])
    ]
    if dossier_count:
        status = "watch" if dossier_ready == dossier_count else "open"
    else:
        status = "watch" if enantiomer_targets and figure_ready else "open"
    if not enantiomer_targets:
        status = "mitigated"
    return {
        "risk_id": "medication_stereochemistry_scope_confusion",
        "severity": "high",
        "status": status,
        "evidence": (
            f"{enantiomer_targets} enantiomer-scope targets, "
            f"{rankable_enantiomer_targets} rankable enantiomer-scope targets, "
            f"stereochemistry figure ready={figure_ready}, "
            f"{dossier_ready} of {dossier_count} stereochemistry dossiers ready, "
            f"{len(blockers)} stereochemistry blockers."
        ),
        "next_mitigation": "Resolve medication stereochemistry dossier fields before citing enantiomeric crystal comparison as curated evidence.",
    }


def _fastcsp_positioning_risk(publication_readiness: dict[str, Any]) -> dict[str, str]:
    policy_text = " ".join(str(item) for item in publication_readiness.get("policy", []))
    positioned = "FastCSP" in policy_text and "claim-readiness" in policy_text
    return {
        "risk_id": "fastcsp_positioning_drift",
        "severity": "medium",
        "status": "mitigated" if positioned else "open",
        "evidence": "Publication policy records FastCSP-complement positioning." if positioned else "FastCSP positioning is absent from publication policy.",
        "next_mitigation": "Keep CrystalProbe framed as audit/curation/calibration around CSP outputs, not as a head-on generator.",
    }
