"""Source-discovery reporting for CrystalProbe candidate substances."""

from __future__ import annotations

from collections import Counter
from typing import Any


def source_discovery_report(discovery_targets: dict[str, Any]) -> dict[str, Any]:
    """Summarize source availability and actionability for target substances."""

    records = [_record(target) for target in discovery_targets.get("targets", [])]
    counts = Counter(record["actionability"] for record in records)
    return {
        "schema_version": "0.1.0",
        "status": "source_discovery_recorded",
        "target_count": len(records),
        "actionability_counts": dict(sorted(counts.items())),
        "targets": records,
        "policy": list(discovery_targets.get("policy", [])),
    }


def source_discovery_markdown(report: dict[str, Any]) -> str:
    """Render source-discovery report as Markdown."""

    lines = [
        "# CrystalProbe Source Discovery Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Targets: `{report['target_count']}`",
        "",
        "## Actionability",
        "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in report["actionability_counts"].items())
    lines.extend(
        [
            "",
            "## Targets",
            "",
            "| Target | Source Status | Actionability | Coordinate Access | Next Step |",
            "|---|---|---|---|---|",
        ]
    )
    for target in report["targets"]:
        lines.append(
            f"| {target['name']} | `{target['source_status']}` | `{target['actionability']}` | "
            f"{target['coordinate_access_summary']} | {target['recommended_next_actions'][0]} |"
        )
    for target in report["targets"]:
        lines.extend(["", f"## {target['name']}", ""])
        lines.append(f"- Actionability: `{target['actionability']}`")
        lines.append(f"- Claim boundary: {target['claim_boundary']}")
        if target["identity_sources"]:
            lines.append("- Identity sources:")
            lines.extend(f"  - {source['label']}: {source['url']}" for source in target["identity_sources"])
        if target["structure_sources"]:
            lines.append("- Structure sources:")
            lines.extend(
                f"  - {source['label']} (`{source.get('coordinate_access', 'not_recorded')}`): {source['url']}"
                for source in target["structure_sources"]
            )
        if target["recommended_next_actions"]:
            lines.append("- Recommended next actions:")
            lines.extend(f"  - {item}" for item in target["recommended_next_actions"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _record(target: dict[str, Any]) -> dict[str, Any]:
    structure_sources = list(target.get("structure_sources", []))
    coordinate_statuses = [str(source.get("coordinate_access", "not_recorded")) for source in structure_sources]
    return {
        "name": target.get("name"),
        "normalized_name": target.get("normalized_name"),
        "source_status": target.get("source_status"),
        "priority_reason": target.get("priority_reason"),
        "identity_sources": list(target.get("identity_sources", [])),
        "structure_sources": structure_sources,
        "coordinate_access_summary": _coordinate_access_summary(coordinate_statuses),
        "actionability": _actionability(coordinate_statuses),
        "claim_boundary": target.get("claim_boundary"),
        "recommended_next_actions": list(target.get("recommended_next_actions", [])),
    }


def _coordinate_access_summary(statuses: list[str]) -> str:
    if not statuses:
        return "none recorded"
    return ", ".join(sorted(set(statuses)))


def _actionability(statuses: list[str]) -> str:
    if any(status == "public_si_candidate" for status in statuses):
        return "download_candidate"
    if any(status in {"publication_known_cif_not_confirmed", "requires_primary_database_validation"} for status in statuses):
        return "validate_coordinate_access"
    if any(status == "not_found" for status in statuses):
        return "deeper_source_search"
    return "review_required"
