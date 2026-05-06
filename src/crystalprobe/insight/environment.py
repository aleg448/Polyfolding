"""Active Python environment checks for CrystalProbe workflows."""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Callable
from typing import Any


OPTIONAL_DEPENDENCIES = [
    {
        "module": "ase",
        "package": "ase",
        "required_for": [
            "CIF parseability checks",
            "AMPETP structure-projection figure regeneration",
            "single-structure inference scripts",
        ],
    },
    {
        "module": "torch",
        "package": "torch",
        "required_for": ["MACE/AIMNet2 local inference"],
    },
    {
        "module": "mace",
        "package": "mace-torch",
        "required_for": ["MACE-OFF local inference"],
    },
    {
        "module": "aimnet",
        "package": "aimnet2calc",
        "required_for": ["AIMNet2 local inference"],
    },
    {
        "module": "fairchem",
        "package": "fairchem-core",
        "required_for": ["UMA/fairchem inference"],
    },
]


def environment_blockers_report(
    *,
    finder: Callable[[str], Any | None] | None = None,
    python_executable: str | None = None,
    configured_runners: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Report optional scientific dependencies visible to the active Python."""

    find_spec = finder or importlib.util.find_spec
    runners = list(configured_runners or [])
    rows = []
    for dependency in OPTIONAL_DEPENDENCIES:
        module = dependency["module"]
        active_available = find_spec(module) is not None
        runner_names = [
            str(runner.get("name"))
            for runner in runners
            if (runner.get("modules") or {}).get(module) is True
        ]
        available = active_available or bool(runner_names)
        rows.append(
            {
                "module": module,
                "package": dependency["package"],
                "status": "available" if available else "missing_from_configured_runners",
                "active_python_status": "available" if active_available else "missing",
                "available_in_runners": runner_names,
                "required_for": list(dependency["required_for"]),
            }
        )
    missing = [row for row in rows if row["status"] != "available"]
    return {
        "schema_version": "0.1.0",
        "status": "environment_ready" if not missing else "environment_blockers_recorded",
        "python_executable": python_executable or sys.executable,
        "dependency_count": len(rows),
        "available_count": len(rows) - len(missing),
        "missing_count": len(missing),
        "configured_runners": runners,
        "dependencies": rows,
        "recommendations": _recommendations(missing),
    }


def environment_blockers_markdown(report: dict[str, Any]) -> str:
    """Render active-environment blockers as Markdown."""

    lines = [
        "# CrystalProbe Active Environment Blockers",
        "",
        f"- Status: `{report['status']}`",
        f"- Python executable: `{report['python_executable']}`",
        f"- Dependencies available through configured runners: `{report['available_count']}` / `{report['dependency_count']}`",
        "",
        "## Dependency Visibility",
        "",
        "| Module | Package | Status | Active Python | Configured Runners | Required for |",
        "|---|---|---|---|---|---|",
    ]
    for row in report["dependencies"]:
        lines.append(
            f"| `{row['module']}` | `{row['package']}` | `{row['status']}` | "
            f"`{row.get('active_python_status', 'unknown')}` | "
            f"{', '.join(row.get('available_in_runners', [])) or 'none'} | "
            f"{'; '.join(row['required_for'])} |"
        )
    lines.extend(["", "## Recommendations", ""])
    if report["recommendations"]:
        lines.extend(f"- {item}" for item in report["recommendations"])
    else:
        lines.append("- No active Python dependency blockers detected.")
    return "\n".join(lines).rstrip() + "\n"


def _recommendations(missing: list[dict[str, Any]]) -> list[str]:
    if not missing:
        return []
    modules = {row["module"] for row in missing}
    recommendations = [
        "Run workflow scripts through the configured CrystalProbe environment, or install the missing package into the active Python before rerunning blocked commands.",
    ]
    if "ase" in modules:
        recommendations.append(
            "Use the project `.venv` Python, Docker core service, or install `ase` into the active Python before regenerating CIF-dependent figures or inference inputs."
        )
    if "fairchem" in modules:
        recommendations.append(
            "Keep UMA/fairchem execution in the fairchem Docker or isolated fairchem environment unless dependency conflicts are resolved."
        )
    return recommendations
