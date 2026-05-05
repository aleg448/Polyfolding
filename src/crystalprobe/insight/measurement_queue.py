"""Prioritized measurement and curation queue from substance profiles."""

from __future__ import annotations

from typing import Any


def measurement_queue_report(
    substance_profiles: dict[str, Any],
    *,
    title: str = "CrystalProbe measurement and curation queue",
) -> dict[str, Any]:
    """Convert substance profiles into next actions ranked by suite impact."""

    items = [_queue_item(profile) for profile in substance_profiles.get("profiles", [])]
    ordered = sorted(items, key=lambda item: (-int(item["priority_score"]), item["substance"].casefold()))
    return {
        "schema_version": "0.1.0",
        "title": title,
        "status": "measurement_queue_recorded",
        "item_count": len(ordered),
        "items": ordered,
        "next_batch": ordered[:5],
        "policy": [
            "Queue priority estimates project utility, not medical importance or clinical value.",
            "Actions that require new gated coordinates stay in curation/source-acquisition status until access is resolved.",
            "Backend-disagreement actions are inspection tasks and do not create experimental stability labels.",
            "Only license-clean coordinates with stability evidence can promote a target toward benchmark use.",
        ],
    }


def measurement_queue_markdown(report: dict[str, Any]) -> str:
    """Render the measurement and curation queue as Markdown."""

    lines = [
        f"# {report['title']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Items: `{report['item_count']}`",
        "",
        "## Next Batch",
        "",
        "| Rank | Substance | Action | Priority | Why | First Step |",
        "|---:|---|---|---:|---|---|",
    ]
    for rank, item in enumerate(report["next_batch"], start=1):
        lines.append(
            f"| {rank} | {item['substance']} | `{item['action_type']}` | "
            f"{item['priority_score']} | {item['rationale']} | {item['first_step']} |"
        )
    lines.extend(
        [
            "",
            "## Full Queue",
            "",
            "| Substance | Readiness | Evidence Tier | Action | Priority | Blocked |",
            "|---|---|---|---|---:|---|",
        ]
    )
    for item in report["items"]:
        lines.append(
            f"| {item['substance']} | `{item['readiness']}` | `{item['evidence_tier']}` | "
            f"`{item['action_type']}` | {item['priority_score']} | `{item['blocked']}` |"
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _queue_item(profile: dict[str, Any]) -> dict[str, Any]:
    readiness = str(profile.get("readiness") or "unknown")
    evidence_tier = str(profile.get("evidence_tier") or "not_assigned")
    action_type, priority, blocked, rationale = _classify(profile, readiness, evidence_tier)
    return {
        "substance": profile.get("name"),
        "role": profile.get("role"),
        "priority_group": profile.get("priority_group"),
        "readiness": readiness,
        "evidence_tier": evidence_tier,
        "action_type": action_type,
        "priority_score": priority,
        "blocked": blocked,
        "rationale": rationale,
        "first_step": _first_step(profile, action_type),
        "next_actions": list(profile.get("next_actions", [])),
        "blocked_claims": list(profile.get("blocked_claims", [])),
        "measurement_outputs": list(profile.get("measurement_outputs", [])),
    }


def _classify(profile: dict[str, Any], readiness: str, evidence_tier: str) -> tuple[str, int, bool, str]:
    name = str(profile.get("name", "")).casefold()
    priority_group = str(profile.get("priority_group") or "")
    has_public_evidence = bool(profile.get("known_public_evidence"))
    has_measurements = bool(profile.get("measurement_outputs"))

    if readiness == "blocked_no_crystal_coordinates":
        return (
            "coordinate_acquisition",
            95 if "lisdexamfetamine" in name else 82,
            True,
            "high-value target is blocked by missing license-compatible crystal coordinates",
        )
    if readiness == "backend_disagreement_inspection":
        base = 88 if "carbamazepine" in name else 76
        return (
            "inspect_backend_disagreement",
            base,
            False,
            "backend disagreement can sharpen the uncertainty wrapper and paper case selection",
        )
    if readiness == "source_discovery_profile" and priority_group == "adhd_core":
        return (
            "source_discovery",
            84 if has_public_evidence else 74,
            False,
            "ADHD-priority source has public evidence but no local computable crystal path",
        )
    if readiness == "guardrailed_pilot_profile":
        return (
            "maintain_guardrailed_pilot",
            65,
            False,
            "measured pilot remains useful for methods evidence and regression checks",
        )
    if readiness == "queue_seed_needs_sources":
        return (
            "seed_source_discovery",
            54,
            False,
            "foundation medicine is in the queue but lacks source evidence",
        )
    if has_measurements and evidence_tier != "not_assigned":
        return (
            "curate_claim_boundary",
            60,
            False,
            "measurements exist but claim promotion still depends on evidence-tier work",
        )
    return (
        "review_profile",
        40,
        False,
        "profile exists but needs manual review before measurement planning",
    )


def _first_step(profile: dict[str, Any], action_type: str) -> str:
    if action_type == "inspect_backend_disagreement":
        backend = profile.get("cposs_backend_profile") or {}
        family = backend.get("family") or profile.get("cposs_family_code") or "unknown"
        return f"Open the CPOSS disagreement details for family {family} and decide whether to run more adjacent pairs."
    if action_type == "coordinate_acquisition":
        return "Search for license-compatible CIF or atom-coordinate evidence; do not run crystal MLIP without coordinates."
    if action_type == "source_discovery":
        return "Create a source-discovery proof record with DOI, structure availability, license status, and next measurement command."
    if action_type == "seed_source_discovery":
        return "Replace the queue seed with at least one concrete public structure/source candidate."
    if action_type == "maintain_guardrailed_pilot":
        return "Keep generated artifacts current and avoid promoting to stability-ranking claims."
    actions = profile.get("next_actions") or []
    return actions[0] if actions else "Review profile and assign a concrete next action."
