"""Source-acquisition reporting for medication crystallographic targets."""

from __future__ import annotations

from collections import Counter
from typing import Any


def source_acquisition_report(acquisition_attempts: dict[str, Any]) -> dict[str, Any]:
    """Summarize concrete coordinate-acquisition attempts and blockers."""

    targets = [_target_record(target) for target in acquisition_attempts.get("targets", [])]
    status_counts = Counter(target["status"] for target in targets)
    input_count = sum(1 for target in targets if target["requires_user_input"])
    return {
        "schema_version": "0.1.0",
        "status": "source_acquisition_recorded",
        "target_count": len(targets),
        "status_counts": dict(sorted(status_counts.items())),
        "targets_requiring_user_input": input_count,
        "targets": targets,
        "policy": list(acquisition_attempts.get("policy", [])),
    }


def source_acquisition_markdown(report: dict[str, Any]) -> str:
    """Render a source-acquisition report as Markdown."""

    lines = [
        "# CrystalProbe Source Acquisition Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Targets: `{report['target_count']}`",
        f"- Targets requiring review input: `{report['targets_requiring_user_input']}`",
        "",
        "## Status Counts",
        "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in report["status_counts"].items())
    lines.extend(
        [
            "",
            "## Targets",
            "",
            "| Target | Task | Status | Local coordinate sources | Download attempts | Review input | Claim boundary |",
            "|---|---|---|---:|---:|---|---|",
        ]
    )
    for target in report["targets"]:
        user_input = "required" if target["requires_user_input"] else "not required"
        lines.append(
            f"| {target['name']} | `{target['task']}` | `{target['status']}` | "
            f"{target['local_coordinate_source_count']} | {target['download_attempt_count']} | {user_input} | "
            f"`{target['claim_boundary']}` |"
        )
    for target in report["targets"]:
        lines.extend(["", f"## {target['name']}", ""])
        lines.append(f"- Task: `{target['task']}`")
        lines.append(f"- Status: `{target['status']}`")
        lines.append(f"- Claim boundary: `{target['claim_boundary']}`")
        if target["source_evidence"]:
            lines.append("- Source evidence:")
            lines.extend(
                f"  - {source['label']}: {source['url']}"
                for source in target["source_evidence"]
            )
        if target["download_attempts"]:
            lines.append("- Download attempts:")
            lines.extend(
                f"  - `{attempt['result']}` via `{attempt['method']}` for {attempt['url']}"
                for attempt in target["download_attempts"]
            )
        if target["local_coordinate_sources"]:
            lines.append("- Local coordinate sources:")
            lines.extend(
                f"  - `{source['path']}` ({source.get('status', 'status_not_recorded')})"
                for source in target["local_coordinate_sources"]
            )
        if target["required_user_input"]:
            lines.append("- Required user input:")
            lines.extend(f"  - {item}" for item in target["required_user_input"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _target_record(target: dict[str, Any]) -> dict[str, Any]:
    required_user_input = list(target.get("required_user_input", []))
    download_attempts = list(target.get("download_attempts", []))
    local_coordinate_sources = list(target.get("local_coordinate_sources", []))
    return {
        "name": target.get("name"),
        "task": target.get("task"),
        "status": target.get("status"),
        "source_evidence": list(target.get("source_evidence", [])),
        "download_attempts": download_attempts,
        "local_coordinate_sources": local_coordinate_sources,
        "local_coordinate_source_count": len(local_coordinate_sources),
        "download_attempt_count": len(download_attempts),
        "failed_download_attempt_count": sum(
            1 for attempt in download_attempts if str(attempt.get("result")) == "failed"
        ),
        "candidate_files": list(target.get("candidate_files", [])),
        "measurement_outputs": list(target.get("measurement_outputs", [])),
        "required_user_input": required_user_input,
        "requires_user_input": bool(required_user_input),
        "claim_boundary": target.get("claim_boundary"),
    }
