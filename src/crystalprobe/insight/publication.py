"""Publication-readiness gates for CrystalProbe artifacts."""

from __future__ import annotations

from typing import Any


def publication_readiness_report(
    *,
    cposs_promotion: dict[str, Any],
    cposs_block_mapping: dict[str, Any] | None = None,
    fingerprint_plan: dict[str, Any],
    release_boundary: dict[str, Any],
    execution_unblock: dict[str, Any],
    handoff: dict[str, Any],
    medication_stereochemistry_dossier: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Summarize whether current artifacts are ready for public scientific claims."""

    gates = [
        _gate(
            "verified_pair_milestone_20",
            cposs_promotion.get("promoted_count", 0) >= 20,
            f"{cposs_promotion.get('promoted_count', 0)} promoted pairs; 20 required for first benchmark-paper milestone.",
        ),
        *_block_mapping_gates(cposs_block_mapping),
        _gate(
            "fingerprint_figures",
            all(row.get("status") == "ready" for row in fingerprint_plan.get("figures", [])),
            _fingerprint_detail(fingerprint_plan),
        ),
        *_medication_stereochemistry_gates(medication_stereochemistry_dossier),
        _gate(
            "release_boundary",
            int((release_boundary.get("counts") or {}).get("license_review_required", 0)) == 0
            and int((release_boundary.get("counts") or {}).get("local_only", 0)) == 0,
            _release_detail(release_boundary),
        ),
        _gate(
            "execution_unblocked",
            execution_unblock.get("blocker_count", 0) == 0,
            f"{execution_unblock.get('blocker_count', 0)} execution blockers recorded.",
        ),
        _gate(
            "human_input",
            not handoff.get("human_input_needed"),
            f"{len(handoff.get('human_input_needed', []))} human-input items recorded.",
        ),
    ]
    ready = all(gate["status"] == "passed" for gate in gates)
    return {
        "schema_version": "0.1.0",
        "status": "publication_ready" if ready else "publication_blocked",
        "ready": ready,
        "gates": gates,
        "blocked_gate_count": sum(1 for gate in gates if gate["status"] != "passed"),
        "approval_batch": list(execution_unblock.get("approval_batch", [])),
        "next_publication_steps": _next_steps(gates, cposs_promotion, cposs_block_mapping or {}, handoff),
        "policy": [
            "CrystalProbe is positioned as an audit, curation, calibration, and claim-readiness layer that complements FastCSP-style crystal-landscape generation.",
            "Publication readiness requires verified benchmark evidence, not just backend disagreement.",
            "CCDC/CSD-derived generated reports and figures require source-license review before public sharing.",
            "MACE, AIMNet2, and UMA absolute energies are not a shared thermodynamic scale; cross-backend disagreement is an inspection signal unless calibrated.",
            "Medication single-structure measurements are backend-behaviour evidence, not polymorph stability claims.",
            "Medication stereochemistry panels are claim-scope artifacts and must not be interpreted as polymorph benchmark validation.",
            "Medication stereochemistry dossiers must be claim-scope ready before enantiomeric panels are cited as curated evidence.",
        ],
    }


def publication_readiness_markdown(report: dict[str, Any]) -> str:
    """Render publication readiness as Markdown."""

    lines = [
        "# CrystalProbe Publication Readiness",
        "",
        f"- Status: `{report['status']}`",
        f"- Ready: `{report['ready']}`",
        f"- Blocked gates: `{report['blocked_gate_count']}`",
        "",
        "## Gates",
        "",
        "| Gate | Status | Detail |",
        "|---|---|---|",
    ]
    for gate in report["gates"]:
        lines.append(f"| `{gate['gate']}` | `{gate['status']}` | {gate['detail']} |")
    lines.extend(["", "## Next Publication Steps", ""])
    lines.extend(f"- {item}" for item in report["next_publication_steps"])
    lines.extend(["", "## Approval Batch", ""])
    if report["approval_batch"]:
        lines.extend(f"- {item}" for item in report["approval_batch"])
    else:
        lines.append("- None currently recorded.")
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _gate(name: str, passed: bool, detail: str) -> dict[str, str]:
    return {"gate": name, "status": "passed" if passed else "blocked", "detail": detail}


def _fingerprint_detail(fingerprint_plan: dict[str, Any]) -> str:
    blocked = [row.get("figure_id") for row in fingerprint_plan.get("figures", []) if row.get("status") != "ready"]
    ready_claim_scope = [
        row.get("figure_id")
        for row in fingerprint_plan.get("figures", [])
        if row.get("status") == "ready" and str(row.get("figure_id", "")).startswith("medication_")
    ]
    ready_text = (
        f" Ready medication claim-scope panels: {', '.join(str(item) for item in ready_claim_scope)}."
        if ready_claim_scope
        else ""
    )
    if not blocked:
        return f"All planned fingerprint figures are ready.{ready_text}"
    return f"Blocked figures: {', '.join(str(item) for item in blocked)}.{ready_text}"


def _release_detail(release_boundary: dict[str, Any]) -> str:
    counts = release_boundary.get("counts") or {}
    return (
        f"{counts.get('candidate_public', 0)} candidate-public, "
        f"{counts.get('license_review_required', 0)} license-review-required, "
        f"{counts.get('local_only', 0)} local-only artifacts."
    )


def _block_mapping_gates(cposs_block_mapping: dict[str, Any] | None) -> list[dict[str, str]]:
    if cposs_block_mapping is None:
        return []
    return [
        _gate(
            "block_form_mapping",
            cposs_block_mapping.get("candidate_count", 0) > 0
            and cposs_block_mapping.get("candidate_mapping_ready_count", 0)
            == cposs_block_mapping.get("candidate_count", 0),
            (
                f"{cposs_block_mapping.get('candidate_mapping_ready_count', 0)} of "
                f"{cposs_block_mapping.get('candidate_count', 0)} candidate pairs have locked block-to-form mappings."
            ),
        )
    ]


def _medication_stereochemistry_gates(dossier: dict[str, Any] | None) -> list[dict[str, str]]:
    if not dossier or int(dossier.get("dossier_count", 0)) == 0:
        return []
    ready = int(dossier.get("ready_for_claim_scope_count", 0))
    count = int(dossier.get("dossier_count", 0))
    return [
        _gate(
            "medication_stereochemistry_dossier",
            ready == count,
            f"{ready} of {count} medication stereochemistry dossiers are claim-scope ready.",
        )
    ]


def _next_steps(
    gates: list[dict[str, str]],
    cposs_promotion: dict[str, Any],
    cposs_block_mapping: dict[str, Any],
    handoff: dict[str, Any],
) -> list[str]:
    steps: list[str] = []
    blocked = {gate["gate"] for gate in gates if gate["status"] != "passed"}
    if "verified_pair_milestone_20" in blocked:
        remaining = 20 - int(cposs_promotion.get("promoted_count", 0))
        steps.append(f"Curate and promote {remaining} verified CPOSS pairs for the first benchmark milestone.")
    if "block_form_mapping" in blocked:
        remaining = int(cposs_block_mapping.get("candidate_count", 0)) - int(
            cposs_block_mapping.get("candidate_mapping_ready_count", 0)
        )
        steps.append(f"Lock block-to-experimental-form mappings for {remaining} CPOSS candidate pairs before promotion.")
    if "fingerprint_figures" in blocked:
        steps.append("Keep fingerprint figures blocked until verified-pair counts support ranking and calibration claims.")
    if "medication_stereochemistry_dossier" in blocked:
        steps.append("Resolve medication stereochemistry dossier fields before citing enantiomeric crystal comparisons as curated evidence.")
    if "release_boundary" in blocked:
        steps.append("Human-review license-review-required and local-only artifacts before any public release.")
    if "execution_unblocked" in blocked:
        steps.append("Resolve the execution unblock report before rerunning dependency-heavy measurements.")
    if "human_input" in blocked:
        steps.extend(list(handoff.get("human_input_needed", []))[:3])
    return steps or ["All publication gates passed; prepare final release review."]
