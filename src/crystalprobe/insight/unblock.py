"""Execution unblock reports for blocked CrystalProbe follow-ups."""

from __future__ import annotations

from collections import Counter
from typing import Any


def execution_unblock_report(
    *,
    environment_blockers: dict[str, Any],
    medication_backend_blockers: dict[str, Any],
    measurement_queue: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Combine active-runner and backend blockers into one execution checklist."""

    environment_rows = [
        {
            "blocker_type": "active_python_dependency",
            "module": row.get("module"),
            "package": row.get("package"),
            "status": row.get("status"),
            "required_for": list(row.get("required_for", [])),
            "next_action": _dependency_next_action(str(row.get("module") or "")),
        }
        for row in environment_blockers.get("dependencies", [])
        if row.get("status") != "available"
    ]
    backend_rows = [
        {
            "blocker_type": "backend_execution",
            "structure_id": row.get("structure_id"),
            "backend": row.get("backend"),
            "status": row.get("status"),
            "reason": row.get("reason"),
            "next_action": row.get("next_action"),
            "command": row.get("command"),
        }
        for row in medication_backend_blockers.get("blockers", [])
    ]
    queue_rows = [
        {
            "blocker_type": "queue_active_runner",
            "substance": row.get("substance"),
            "action_type": row.get("action_type"),
            "missing_modules": list(row.get("active_runner_missing_modules", [])),
            "first_step": row.get("first_step"),
        }
        for row in (measurement_queue or {}).get("items", [])
        if row.get("active_runner_blocked")
    ]
    rows = environment_rows + backend_rows + queue_rows
    counts = Counter(row["blocker_type"] for row in rows)
    return {
        "schema_version": "0.1.0",
        "status": "execution_unblock_queue_recorded" if rows else "execution_unblock_queue_clear",
        "blocker_count": len(rows),
        "counts": dict(sorted(counts.items())),
        "environment_blockers": environment_rows,
        "backend_blockers": backend_rows,
        "queue_runner_blockers": queue_rows,
        "approval_batch": _approval_batch(environment_rows, backend_rows),
        "policy": [
            "This report is an execution checklist, not a license grant or benchmark promotion.",
            "Do not publish CCDC/CSD-derived coordinates unless source-specific redistribution terms permit it.",
            "Docker/backend commands should be run only after user approval and environment limits permit them.",
        ],
    }


def execution_unblock_markdown(report: dict[str, Any]) -> str:
    """Render the execution unblock report as Markdown."""

    lines = [
        "# CrystalProbe Execution Unblock Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Blockers: `{report['blocker_count']}`",
        "",
        "## Counts",
        "",
    ]
    for blocker_type, count in report["counts"].items():
        lines.append(f"- `{blocker_type}`: `{count}`")
    lines.extend(["", "## Approval Batch", ""])
    if report["approval_batch"]:
        lines.extend(f"- {item}" for item in report["approval_batch"])
    else:
        lines.append("- No approvals currently needed.")
    if report["environment_blockers"]:
        lines.extend(["", "## Active Python Dependencies", ""])
        lines.extend(
            f"- `{row['module']}` / `{row['package']}`: `{row['status']}`. {row['next_action']}"
            for row in report["environment_blockers"]
        )
    if report["backend_blockers"]:
        lines.extend(["", "## Backend Execution Blockers", ""])
        lines.extend(
            f"- `{row['structure_id']}` `{row['backend']}`: `{row['status']}` - {row['next_action']}"
            for row in report["backend_blockers"]
        )
        commands = [row.get("command") for row in report["backend_blockers"] if row.get("command")]
        if commands:
            lines.extend(["", "## Pending Commands", ""])
            lines.extend(f"- `{command}`" for command in commands)
    if report["queue_runner_blockers"]:
        lines.extend(["", "## Queue Items Blocked By Active Runner", ""])
        lines.extend(
            f"- {row['substance']} `{row['action_type']}`: missing `{', '.join(row['missing_modules'])}`."
            for row in report["queue_runner_blockers"]
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _dependency_next_action(module: str) -> str:
    if module == "fairchem":
        return "Use the fairchem Docker service or isolated fairchem environment for UMA work."
    if module in {"ase", "mace", "aimnet"}:
        return "Use the project `.venv`, Docker core service, or install the package into the active Python."
    return "Use an environment where this module is visible before running dependent workflows."


def _approval_batch(environment_rows: list[dict[str, Any]], backend_rows: list[dict[str, Any]]) -> list[str]:
    approvals: list[str] = []
    modules = {str(row.get("module")) for row in environment_rows}
    if modules.intersection({"ase", "mace", "aimnet"}):
        approvals.append("Select or repair the CrystalProbe Python runner for CIF, MACE, and AIMNet2 workflows.")
    if "fairchem" in modules:
        approvals.append("Use Docker/fairchem or the isolated fairchem environment for UMA workflows.")
    if backend_rows:
        approvals.append("Run the recorded AIMNet2/UMA medication backend commands when Docker/escalation limits allow.")
    return approvals
