"""Compact handoff summaries for CrystalProbe work sessions."""

from __future__ import annotations

from typing import Any


def handoff_report(
    *,
    project_status: dict[str, Any],
    roadmap_status: dict[str, Any],
    measurement_queue: dict[str, Any],
    execution_unblock: dict[str, Any],
    publication_readiness: dict[str, Any] | None = None,
    risk_register: dict[str, Any] | None = None,
    report_consistency: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a compact handoff view from generated status artifacts."""

    deliverables = [
        {
            "deliverable": item.get("deliverable"),
            "status": item.get("status"),
            "top_evidence": list(item.get("evidence", []))[:3],
            "top_remaining": list(item.get("remaining", []))[:3],
        }
        for item in roadmap_status.get("deliverables", [])
    ]
    next_batch = [
        {
            "substance": item.get("substance"),
            "action_type": item.get("action_type"),
            "priority_score": item.get("priority_score"),
            "blocked": item.get("blocked"),
            "active_runner_blocked": item.get("active_runner_blocked"),
            "first_step": item.get("first_step"),
        }
        for item in measurement_queue.get("next_batch", [])
    ]
    return {
        "schema_version": "0.1.0",
        "status": "handoff_recorded",
        "verification": project_status.get("verification", {}),
        "ampetp": project_status.get("ampetp", {}),
        "cposs_bridge": project_status.get("cposs_bridge", {}),
        "evidence_tiers": project_status.get("evidence_tiers", {}),
        "execution_unblock": {
            "status": execution_unblock.get("status"),
            "blocker_count": execution_unblock.get("blocker_count", 0),
            "counts": dict(execution_unblock.get("counts", {})),
            "approval_batch": list(execution_unblock.get("approval_batch", [])),
        },
        "publication_readiness": _publication_summary(publication_readiness),
        "report_consistency": _report_consistency_summary(report_consistency),
        "top_risks": _top_risks(risk_register),
        "deliverables": deliverables,
        "next_batch": next_batch,
        "human_input_needed": list(project_status.get("remaining_user_input", [])),
        "policy": [
            "This is a handoff summary generated from local reports; source reports remain canonical.",
            "Do not promote candidate pairs to benchmark records until experimental stability evidence and license decisions are complete.",
            "Keep raw CCDC/CSD-derived coordinate files local unless redistribution is explicitly permitted.",
        ],
    }


def handoff_markdown(report: dict[str, Any]) -> str:
    """Render the handoff report as Markdown."""

    verification = report.get("verification", {})
    ampetp = report.get("ampetp", {})
    cposs = report.get("cposs_bridge", {})
    unblock = report.get("execution_unblock", {})
    publication = report.get("publication_readiness", {})
    consistency = report.get("report_consistency", {})
    lines = [
        "# CrystalProbe Handoff Summary",
        "",
        f"- Status: `{report['status']}`",
        f"- Tests: `{verification.get('latest_local_test_summary', 'not_recorded')}`",
        f"- Git: `{verification.get('git_status', 'not_recorded')}`",
        f"- AMPETP readiness: `{ampetp.get('readiness_status')}`",
        f"- CPOSS bridge: `{cposs.get('structure_count')}` structures / `{cposs.get('family_count')}` families",
        f"- Execution blockers: `{unblock.get('blocker_count', 0)}`",
        f"- Publication readiness: `{publication.get('status', 'not_available')}`",
        f"- Publication blocked gates: `{publication.get('blocked_gate_count', 0)}`",
        f"- Report consistency: `{consistency.get('status', 'not_available')}`",
        f"- Report consistency blocked checks: `{consistency.get('blocked_check_count', 0)}`",
        "",
        "## Approval Batch",
        "",
    ]
    if unblock.get("approval_batch"):
        lines.extend(f"- {item}" for item in unblock["approval_batch"])
    else:
        lines.append("- None currently recorded.")
    lines.extend(
        [
            "",
            "## Deliverables",
            "",
            "| Deliverable | Status | Top Remaining |",
            "|---|---|---|",
        ]
    )
    for item in report["deliverables"]:
        remaining = "; ".join(item.get("top_remaining", [])) or "none"
        lines.append(f"| {item['deliverable']} | `{item['status']}` | {remaining} |")
    lines.extend(["", "## Publication Gates", ""])
    if publication.get("gates"):
        lines.extend(f"- `{gate['gate']}`: `{gate['status']}` - {gate['detail']}" for gate in publication["gates"])
    else:
        lines.append("- Publication readiness report is not available.")
    if publication.get("next_publication_steps"):
        lines.extend(["", "## Top Publication Steps", ""])
        lines.extend(f"- {item}" for item in publication["next_publication_steps"])
    lines.extend(["", "## Report Consistency", ""])
    if consistency.get("checks"):
        lines.extend(
            f"- `{check['check']}`: `{check['status']}` - {check['detail']}"
            for check in consistency["checks"]
        )
    else:
        lines.append("- Report consistency report is not available.")
    lines.extend(["", "## Top Risks", ""])
    if report.get("top_risks"):
        lines.extend(
            f"- `{risk['risk_id']}`: `{risk['severity']}` / `{risk['status']}` - {risk['next_mitigation']}"
            for risk in report["top_risks"]
        )
    else:
        lines.append("- Risk register is not available.")
    lines.extend(
        [
            "",
            "## Next Measurement Batch",
            "",
            "| Substance | Action | Priority | Blocked | Runner Blocked | First Step |",
            "|---|---|---:|---|---|---|",
        ]
    )
    for item in report["next_batch"]:
        lines.append(
            f"| {item['substance']} | `{item['action_type']}` | {item['priority_score']} | "
            f"`{item['blocked']}` | `{item['active_runner_blocked']}` | {item['first_step']} |"
        )
    lines.extend(["", "## Human Input Needed", ""])
    if report["human_input_needed"]:
        lines.extend(f"- {item}" for item in report["human_input_needed"])
    else:
        lines.append("- None currently recorded.")
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _publication_summary(publication_readiness: dict[str, Any] | None) -> dict[str, Any]:
    if not publication_readiness:
        return {
            "status": "not_available",
            "ready": False,
            "blocked_gate_count": 0,
            "gates": [],
            "next_publication_steps": [],
        }
    return {
        "status": publication_readiness.get("status"),
        "ready": bool(publication_readiness.get("ready")),
        "blocked_gate_count": publication_readiness.get("blocked_gate_count", 0),
        "gates": list(publication_readiness.get("gates", [])),
        "next_publication_steps": list(publication_readiness.get("next_publication_steps", []))[:5],
    }


def _report_consistency_summary(report_consistency: dict[str, Any] | None) -> dict[str, Any]:
    if not report_consistency:
        return {
            "status": "not_available",
            "blocked_check_count": 0,
            "checks": [],
        }
    return {
        "status": report_consistency.get("status"),
        "blocked_check_count": report_consistency.get("blocked_check_count", 0),
        "checks": list(report_consistency.get("checks", [])),
    }


def _top_risks(risk_register: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not risk_register:
        return []
    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    status_rank = {"open": 0, "watch": 1, "blocked": 1, "mitigated": 3}
    risks = [
        dict(risk)
        for risk in risk_register.get("risks", [])
        if risk.get("status") != "mitigated"
    ]
    risks.sort(
        key=lambda risk: (
            severity_rank.get(str(risk.get("severity")), 9),
            status_rank.get(str(risk.get("status")), 9),
            str(risk.get("risk_id")),
        )
    )
    return risks[:5]
