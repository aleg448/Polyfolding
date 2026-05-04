"""Project status dashboard generation."""

from __future__ import annotations

from typing import Any


def project_status_report(
    *,
    readiness: dict[str, Any],
    bundle: dict[str, Any],
    cposs_bridge: dict[str, Any],
    blockers_text: str,
    test_summary: str,
    therapeutic_contrast: dict[str, Any] | None = None,
    evidence_tiers: dict[str, Any] | None = None,
    docker_status: str = "not_run",
    git_status: str = "not_recorded",
) -> dict[str, Any]:
    """Build a compact status report for a CrystalProbe work session."""

    blockers = _extract_bullets(blockers_text, heading="## Remaining User Input")
    next_steps = [
        "Design OMAT24 and OMol25 validation paths before using those models for scientific claims.",
        "Promote CPOSS bridge records into curated pair records with experimental stability evidence.",
    ]
    if "aimnet2_therapeutic_contrast" not in docker_status:
        next_steps.append("Run AIMNet2 on the ibuprofen sensitivity grid in Linux/Docker.")
    if "uma_therapeutic_contrast" not in docker_status:
        next_steps.insert(0, "Extend UMA from AMPETP sensitivity into therapeutic contrast workflows.")
    return {
        "schema_version": "0.1.0",
        "status": "active_research_pilot",
        "ampetp": {
            "readiness_status": readiness.get("status"),
            "readiness_passed": readiness.get("passed"),
            "readiness_failed": readiness.get("failed"),
            "bundle_artifacts": len(bundle.get("artifacts", [])),
            "bundle_manifest_sha256": bundle.get("manifest_sha256"),
        },
        "cposs_bridge": {
            "family_count": cposs_bridge.get("family_count"),
            "structure_count": cposs_bridge.get("structure_count"),
            "families": sorted(cposs_bridge.get("families", {})),
        },
        "therapeutic_contrast": _contrast_status(therapeutic_contrast),
        "evidence_tiers": _evidence_tier_status(evidence_tiers),
        "verification": {
            "latest_local_test_summary": test_summary,
            "docker_status": docker_status,
            "git_status": git_status,
        },
        "remaining_user_input": blockers,
        "next_recommended_steps": next_steps,
    }


def project_status_markdown(report: dict[str, Any]) -> str:
    """Render project status as Markdown."""

    lines = [
        "# CrystalProbe Project Status Dashboard",
        "",
        f"- Status: `{report['status']}`",
        f"- AMPETP readiness: `{report['ampetp']['readiness_status']}`",
        f"- AMPETP readiness checks: `{report['ampetp']['readiness_passed']}` passed, `{report['ampetp']['readiness_failed']}` failed",
        f"- AMPETP bundle artifacts: `{report['ampetp']['bundle_artifacts']}`",
        f"- AMPETP bundle SHA-256: `{report['ampetp']['bundle_manifest_sha256']}`",
        "",
        "## CPOSS Bridge",
        "",
        f"- Families: `{report['cposs_bridge']['family_count']}`",
        f"- Structures: `{report['cposs_bridge']['structure_count']}`",
        f"- Family codes: `{', '.join(report['cposs_bridge']['families'])}`",
        "",
        "## Therapeutic Contrast",
        "",
        f"- Backend: `{report['therapeutic_contrast']['backend']}`",
        f"- Targets: `{report['therapeutic_contrast']['target_count']}`",
        f"- Status: `{report['therapeutic_contrast']['status']}`",
        "",
        "## Evidence Tiers",
        "",
        f"- Targets: `{report['evidence_tiers']['target_count']}`",
        f"- Guardrailed pilots: `{report['evidence_tiers']['guardrailed_pilot_count']}`",
        f"- Blocked targets: `{report['evidence_tiers']['blocked_count']}`",
        f"- Verified benchmark candidates: `{report['evidence_tiers']['verified_candidate_count']}`",
        "",
        "## Verification",
        "",
        f"- Latest local tests: `{report['verification']['latest_local_test_summary']}`",
        f"- Docker: `{report['verification']['docker_status']}`",
        f"- Git: `{report['verification']['git_status']}`",
        "",
        "## Remaining User Input",
        "",
    ]
    lines.extend(f"- {item}" for item in report["remaining_user_input"])
    if not report["remaining_user_input"]:
        lines.append("- None currently recorded.")
    lines.extend(["", "## Next Recommended Steps", ""])
    lines.extend(f"- {item}" for item in report["next_recommended_steps"])
    return "\n".join(lines).rstrip() + "\n"


def _extract_bullets(text: str, *, heading: str) -> list[str]:
    lines = text.splitlines()
    collecting = False
    bullets: list[str] = []
    for line in lines:
        if line.strip() == heading:
            collecting = True
            continue
        if collecting and line.startswith("## "):
            break
        if collecting and line.startswith("- "):
            bullets.append(line[2:].strip())
    return bullets


def _contrast_status(report: dict[str, Any] | None) -> dict[str, Any]:
    if not report:
        return {"status": "not_available", "backend": None, "target_count": 0}
    return {
        "status": "mace_contrast_ready" if report.get("backend") == "mace" else "available",
        "backend": report.get("backend"),
        "target_count": report.get("target_count"),
    }


def _evidence_tier_status(report: dict[str, Any] | None) -> dict[str, Any]:
    if not report:
        return {
            "status": "not_available",
            "target_count": 0,
            "guardrailed_pilot_count": 0,
            "blocked_count": 0,
            "verified_candidate_count": 0,
            "tiers": {},
        }
    tiers = {}
    for target in report.get("targets", []):
        tier = target.get("tier", {}).get("tier", "unknown")
        tiers[tier] = tiers.get(tier, 0) + 1
    return {
        "status": report.get("status"),
        "target_count": len(report.get("targets", [])),
        "guardrailed_pilot_count": tiers.get("agi_assisted_guardrailed_pilot", 0),
        "blocked_count": tiers.get("blocked_no_coordinates", 0),
        "verified_candidate_count": tiers.get("verified_benchmark_candidate", 0),
        "tiers": tiers,
    }
