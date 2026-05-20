"""Consistency checks across generated CrystalProbe status reports."""

from __future__ import annotations

from typing import Any


def report_consistency_report(
    *,
    project_status: dict[str, Any],
    roadmap_status: dict[str, Any],
    handoff_summary: dict[str, Any],
    publication_readiness: dict[str, Any],
    release_boundary: dict[str, Any],
    status_chain: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Check whether generated status reports agree on shared fields."""

    checks = [
        _test_summary_check(project_status, roadmap_status, handoff_summary),
        _release_boundary_count_check(release_boundary, publication_readiness, handoff_summary),
        _publication_gate_count_check(publication_readiness, handoff_summary),
        _status_chain_order_check(status_chain or {}),
        _status_chain_summary_check(status_chain or {}, project_status),
    ]
    blocked = [check for check in checks if check["status"] != "passed"]
    return {
        "schema_version": "0.1.0",
        "status": "reports_consistent" if not blocked else "report_consistency_blocked",
        "blocked_check_count": len(blocked),
        "checks": checks,
        "policy": [
            "Generated status reports must agree before using handoff or publication-readiness summaries as current state.",
            "Run scripts/build_status_chain.py after a live test run to avoid stale project, roadmap, and handoff summaries.",
            "Release-boundary counts in publication readiness must match the release-boundary report.",
        ],
    }


def report_consistency_markdown(report: dict[str, Any]) -> str:
    """Render report consistency checks as Markdown."""

    lines = [
        "# CrystalProbe Report Consistency",
        "",
        f"- Status: `{report['status']}`",
        f"- Blocked checks: `{report['blocked_check_count']}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for check in report["checks"]:
        lines.append(f"| `{check['check']}` | `{check['status']}` | {check['detail']} |")
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _test_summary_check(
    project_status: dict[str, Any],
    roadmap_status: dict[str, Any],
    handoff_summary: dict[str, Any],
) -> dict[str, str]:
    values = {
        "project": project_status.get("verification", {}).get("latest_local_test_summary"),
        "roadmap": roadmap_status.get("local_verification"),
        "handoff": handoff_summary.get("verification", {}).get("latest_local_test_summary"),
    }
    unique = {value for value in values.values() if value}
    status = "passed" if len(unique) == 1 and "not_recorded" not in unique else "blocked"
    return {
        "check": "test_summary_alignment",
        "status": status,
        "detail": ", ".join(f"{key}={value or 'missing'}" for key, value in values.items()),
    }


def _release_boundary_count_check(
    release_boundary: dict[str, Any],
    publication_readiness: dict[str, Any],
    handoff_summary: dict[str, Any],
) -> dict[str, str]:
    counts = release_boundary.get("counts", {})
    expected = _release_boundary_detail(counts)
    publication_detail = _gate_detail(publication_readiness, "release_boundary")
    handoff_detail = _gate_detail(handoff_summary.get("publication_readiness", {}), "release_boundary")
    status = "passed" if expected and publication_detail == expected and handoff_detail == expected else "blocked"
    return {
        "check": "release_boundary_count_alignment",
        "status": status,
        "detail": (
            f"release={expected or 'missing'}; "
            f"publication={publication_detail or 'missing'}; "
            f"handoff={handoff_detail or 'missing'}"
        ),
    }


def _publication_gate_count_check(
    publication_readiness: dict[str, Any],
    handoff_summary: dict[str, Any],
) -> dict[str, str]:
    gates = publication_readiness.get("gates", [])
    computed = sum(1 for gate in gates if gate.get("status") != "passed")
    publication_count = publication_readiness.get("blocked_gate_count")
    handoff_count = handoff_summary.get("publication_readiness", {}).get("blocked_gate_count")
    status = "passed" if computed == publication_count == handoff_count else "blocked"
    return {
        "check": "publication_gate_count_alignment",
        "status": status,
        "detail": f"computed={computed}; publication={publication_count}; handoff={handoff_count}",
    }


def _status_chain_order_check(status_chain: dict[str, Any]) -> dict[str, str]:
    steps = [str(step.get("step")) for step in status_chain.get("steps", [])]
    expected = ["project_status", "roadmap_status", "handoff_summary"]
    status = "passed" if steps == expected else "blocked"
    return {
        "check": "status_chain_order",
        "status": status,
        "detail": f"steps={', '.join(steps) or 'missing'}",
    }


def _status_chain_summary_check(status_chain: dict[str, Any], project_status: dict[str, Any]) -> dict[str, str]:
    project_summary = project_status.get("verification", {}).get("latest_local_test_summary")
    chain_summary = ""
    for step in status_chain.get("steps", []):
        if step.get("step") != "project_status":
            continue
        command = list(step.get("command", []))
        if "--test-summary" in command:
            index = command.index("--test-summary")
            if index + 1 < len(command):
                chain_summary = str(command[index + 1])
    status = "passed" if chain_summary and chain_summary == project_summary else "blocked"
    return {
        "check": "status_chain_test_summary",
        "status": status,
        "detail": f"status_chain={chain_summary or 'missing'}; project={project_summary or 'missing'}",
    }


def _release_boundary_detail(counts: dict[str, Any]) -> str:
    if not counts:
        return ""
    return (
        f"{counts.get('candidate_public', 0)} candidate-public, "
        f"{counts.get('license_review_required', 0)} license-review-required, "
        f"{counts.get('local_only', 0)} local-only artifacts."
    )


def _gate_detail(report: dict[str, Any], gate_name: str) -> str:
    for gate in report.get("gates", []):
        if gate.get("gate") == gate_name:
            return str(gate.get("detail") or "")
    return ""
