"""Resolve evidence-packet blockers with candidate literature/source records."""

from __future__ import annotations

from typing import Any


def evidence_resolution_report(packet: dict[str, Any], candidate_document: dict[str, Any]) -> dict[str, Any]:
    """Compare an evidence packet with candidate evidence overlays."""

    pair_id = str(packet["pair_id"])
    candidate = _candidate_for_pair(candidate_document, pair_id)
    if candidate is None:
        return {
            "schema_version": "0.1.0",
            "status": "evidence_resolution_candidate_missing",
            "pair_id": pair_id,
            "resolved_blocker_count": 0,
            "remaining_blocker_count": packet["promotion_gate"]["blocker_count"],
            "resolved_blockers": [],
            "remaining_blockers": packet["promotion_gate"]["blockers"],
            "promotion_decision": "do_not_promote_no_candidate_evidence",
            "next_actions": ["Add a candidate evidence record before attempting blocker resolution."],
            "policy": list(candidate_document.get("policy", [])),
        }

    resolved = _resolved_blockers(packet, candidate)
    resolved_fields = {row["field"] for row in resolved}
    remaining = [
        blocker
        for blocker in packet["promotion_gate"]["blockers"]
        if blocker["field"] not in resolved_fields
    ]
    manual_checks = list(candidate.get("remaining_manual_checks", []))
    if manual_checks:
        remaining.append(
            {
                "pair_id": pair_id,
                "severity": "blocker",
                "field": "human_review",
                "message": "candidate evidence requires human source/form/license review before manifest promotion",
            }
        )
    status = "evidence_resolution_candidate_recorded"
    if not remaining:
        status = "evidence_resolution_ready_for_manifest_patch"
    return {
        "schema_version": "0.1.0",
        "status": status,
        "pair_id": pair_id,
        "molecule": packet.get("molecule"),
        "candidate_status": candidate.get("candidate_status"),
        "promotion_decision": candidate.get("promotion_decision", "do_not_promote_candidate_only"),
        "proposed_stability_ordering": candidate.get("proposed_stability_ordering"),
        "stability_summary": candidate.get("stability_summary"),
        "stability_sources": list(candidate.get("stability_sources", [])),
        "structure_candidates": dict(candidate.get("structure_candidates", {})),
        "resolved_blocker_count": len(resolved),
        "remaining_blocker_count": len(remaining),
        "resolved_blockers": resolved,
        "remaining_blockers": remaining,
        "remaining_manual_checks": manual_checks,
        "suggested_manifest_values": _suggested_manifest_values(candidate),
        "next_actions": _next_actions(remaining, manual_checks),
        "policy": list(candidate_document.get("policy", [])),
    }


def evidence_resolution_markdown(report: dict[str, Any]) -> str:
    """Render an evidence-resolution report as Markdown."""

    lines = [
        f"# CrystalProbe Evidence Resolution: {report['pair_id']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Candidate status: `{report.get('candidate_status', 'not_recorded')}`",
        f"- Promotion decision: `{report['promotion_decision']}`",
        f"- Proposed stability ordering: `{report.get('proposed_stability_ordering', 'not_recorded')}`",
        f"- Resolved blockers: `{report['resolved_blocker_count']}`",
        f"- Remaining blockers: `{report['remaining_blocker_count']}`",
        "",
        "## Stability Evidence Candidates",
        "",
        "| Source | DOI | Role | Note |",
        "|---|---|---|---|",
    ]
    for source in report.get("stability_sources", []):
        lines.append(
            f"| {source['title']} | `{source.get('doi', '')}` | "
            f"`{source.get('evidence_role', '')}` | {source.get('evidence_note', '')} |"
        )
    lines.extend(
        [
            "",
            "## Structure Candidates",
            "",
            "| Side | Proposed Form | Source ID | Space Group | License | Disorder |",
            "|---|---|---|---|---|---|",
        ]
    )
    for side, candidate in report.get("structure_candidates", {}).items():
        lines.append(
            f"| {side} | {candidate['proposed_form_label']} | `{candidate['source_id']}` | "
            f"`{candidate['space_group']}` | `{candidate['license']}` | `{candidate['has_disorder']}` |"
        )
    lines.extend(
        [
            "",
            "## Resolved Blockers",
            "",
            "| Field | Candidate Replacement | Evidence |",
            "|---|---|---|",
        ]
    )
    if report["resolved_blockers"]:
        for blocker in report["resolved_blockers"]:
            lines.append(f"| `{blocker['field']}` | `{blocker['candidate_value']}` | {blocker['evidence']} |")
    else:
        lines.append("| `none` | `not_recorded` | No candidate evidence resolved a packet blocker. |")
    lines.extend(
        [
            "",
            "## Remaining Blockers",
            "",
            "| Field | Message |",
            "|---|---|",
        ]
    )
    for blocker in report["remaining_blockers"]:
        lines.append(f"| `{blocker['field']}` | {blocker['message']} |")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in report["next_actions"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report.get("policy", []))
    return "\n".join(lines).rstrip() + "\n"


def _candidate_for_pair(candidate_document: dict[str, Any], pair_id: str) -> dict[str, Any] | None:
    for candidate in candidate_document.get("candidates", []):
        if candidate.get("pair_id") == pair_id:
            return candidate
    return None


def _resolved_blockers(packet: dict[str, Any], candidate: dict[str, Any]) -> list[dict[str, str]]:
    blockers = {blocker["field"] for blocker in packet["promotion_gate"]["blockers"]}
    resolved: list[dict[str, str]] = []
    if "evidence.stability_ordering" in blockers and candidate.get("proposed_stability_ordering"):
        resolved.append(
            {
                "field": "evidence.stability_ordering",
                "candidate_value": str(candidate["proposed_stability_ordering"]),
                "evidence": "candidate stability sources record Form I/Form II stability context",
            }
        )
    if "evidence.citation" in blockers and candidate.get("stability_sources"):
        source = candidate["stability_sources"][0]
        resolved.append(
            {
                "field": "evidence.citation",
                "candidate_value": str(source.get("doi") or source.get("url")),
                "evidence": "candidate stability source supplies a durable DOI or URL",
            }
        )
    for side in ("A", "B"):
        structure = candidate.get("structure_candidates", {}).get(side, {})
        if f"structure_{side}.license" in blockers and structure.get("license"):
            resolved.append(
                {
                    "field": f"structure_{side}.license",
                    "candidate_value": str(structure["license"]),
                    "evidence": f"{structure.get('source_id', side)} reports candidate release terms",
                }
            )
        if f"structure_{side}.source_id" in blockers and structure.get("source_id"):
            resolved.append(
                {
                    "field": f"structure_{side}.source_id",
                    "candidate_value": str(structure["source_id"]),
                    "evidence": "candidate public structure source is recorded",
                }
            )
    if "has_disorder" in blockers:
        structures = candidate.get("structure_candidates", {})
        if all(side in structures and "has_disorder" in structures[side] for side in ("A", "B")):
            resolved.append(
                {
                    "field": "has_disorder",
                    "candidate_value": "A=false; B=false",
                    "evidence": "candidate structure pages report no disorder for both structures",
                }
            )
    return resolved


def _suggested_manifest_values(candidate: dict[str, Any]) -> dict[str, Any]:
    structures = candidate.get("structure_candidates", {})
    return {
        "curation_status": "reviewed_candidate_after_human_review",
        "evidence.stability_ordering": candidate.get("proposed_stability_ordering"),
        "evidence.citation_doi": (candidate.get("stability_sources") or [{}])[0].get("doi"),
        "structure_a.source_id": structures.get("A", {}).get("source_id"),
        "structure_a.license": structures.get("A", {}).get("license"),
        "structure_b.source_id": structures.get("B", {}).get("source_id"),
        "structure_b.license": structures.get("B", {}).get("license"),
        "has_disorder": False if structures else None,
    }


def _next_actions(remaining: list[dict[str, Any]], manual_checks: list[str]) -> list[str]:
    actions = []
    if any(blocker["field"] == "record" for blocker in remaining):
        actions.append("Prepare a manifest patch that replaces TODO placeholders and points to reviewed CIF paths.")
    if any(blocker["field"] == "human_review" for blocker in remaining):
        actions.extend(manual_checks)
    if not actions:
        actions.append("Human reviewer can prepare a manifest patch; do not auto-promote from candidate evidence alone.")
    return actions
