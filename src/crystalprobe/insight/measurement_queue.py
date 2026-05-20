"""Prioritized measurement and curation queue from substance profiles."""

from __future__ import annotations

from typing import Any


def measurement_queue_report(
    substance_profiles: dict[str, Any],
    *,
    environment_blockers: dict[str, Any] | None = None,
    title: str = "CrystalProbe measurement and curation queue",
) -> dict[str, Any]:
    """Convert substance profiles into next actions ranked by suite impact."""

    active_missing = _active_missing_modules(environment_blockers or {})
    items = [_queue_item(profile, active_missing=active_missing) for profile in substance_profiles.get("profiles", [])]
    ordered = sorted(items, key=lambda item: (-int(item["priority_score"]), item["substance"].casefold()))
    return {
        "schema_version": "0.1.0",
        "title": title,
        "status": "measurement_queue_recorded",
        "item_count": len(ordered),
        "active_runner_missing_modules": sorted(active_missing),
        "active_runner_blocked_count": sum(1 for item in ordered if item["active_runner_blocked"]),
        "items": ordered,
        "next_batch": ordered[:5],
        "policy": [
            "Queue priority estimates project utility, not medical importance or clinical value.",
            "Actions that require new gated coordinates stay in curation/source-acquisition status until access is resolved.",
            "Active-runner blockers mean the current Python cannot run the dependency-heavy step; use `.venv`, Docker, or a Python with the listed modules visible.",
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
        f"- Active-runner blocked items: `{report.get('active_runner_blocked_count', 0)}`",
        "",
        "## Next Batch",
        "",
        "| Rank | Substance | Action | Priority | Runner Blocked | Why | First Step |",
        "|---:|---|---|---:|---|---|---|",
    ]
    for rank, item in enumerate(report["next_batch"], start=1):
        lines.append(
            f"| {rank} | {item['substance']} | `{item['action_type']}` | "
            f"{item['priority_score']} | `{item['active_runner_blocked']}` | "
            f"{item['rationale']} | {item['first_step']} |"
        )
    lines.extend(
        [
            "",
            "## Full Queue",
            "",
            "| Substance | Readiness | Evidence Tier | Action | Priority | Blocked | Runner Blocked |",
            "|---|---|---|---|---:|---|---|",
        ]
    )
    for item in report["items"]:
        lines.append(
            f"| {item['substance']} | `{item['readiness']}` | `{item['evidence_tier']}` | "
            f"`{item['action_type']}` | {item['priority_score']} | `{item['blocked']}` | "
            f"`{item['active_runner_blocked']}` |"
        )
    blocked = [item for item in report["items"] if item["active_runner_blocked"]]
    if blocked:
        lines.extend(["", "## Active Runner Blockers", ""])
        lines.extend(
            f"- {item['substance']}: missing `{', '.join(item['active_runner_missing_modules'])}` for `{item['action_type']}`."
            for item in blocked
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _queue_item(profile: dict[str, Any], *, active_missing: set[str]) -> dict[str, Any]:
    readiness = str(profile.get("readiness") or "unknown")
    evidence_tier = str(profile.get("evidence_tier") or "not_assigned")
    action_type, priority, blocked, rationale = _classify(profile, readiness, evidence_tier)
    runner_missing = sorted(_runner_required_modules(action_type).intersection(active_missing))
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
        "first_step": _runner_aware_first_step(_first_step(profile, action_type), runner_missing),
        "active_runner_blocked": bool(runner_missing),
        "active_runner_missing_modules": runner_missing,
        "next_actions": list(profile.get("next_actions", [])),
        "blocked_claims": list(profile.get("blocked_claims", [])),
        "measurement_outputs": list(profile.get("measurement_outputs", [])),
    }


def _active_missing_modules(environment_blockers: dict[str, Any]) -> set[str]:
    return {
        str(row.get("module"))
        for row in environment_blockers.get("dependencies", [])
        if row.get("module") and row.get("status") != "available"
    }


def _runner_required_modules(action_type: str) -> set[str]:
    if action_type in {
        "run_local_measurements",
        "inspect_backend_disagreement",
        "download_public_cif_candidate",
    }:
        return {"ase", "mace", "aimnet", "fairchem"}
    if action_type in {"curate_claim_boundary", "maintain_guardrailed_pilot"}:
        return {"ase", "aimnet", "fairchem"}
    return set()


def _runner_aware_first_step(first_step: str, runner_missing: list[str]) -> str:
    if not runner_missing:
        return first_step
    return (
        f"{first_step} Active runner is missing {', '.join(runner_missing)}; "
        "use `.venv`, Docker, or a Python with those modules visible for dependency-heavy steps."
    )


def _classify(profile: dict[str, Any], readiness: str, evidence_tier: str) -> tuple[str, int, bool, str]:
    name = str(profile.get("name", "")).casefold()
    priority_group = str(profile.get("priority_group") or "")
    has_public_evidence = bool(profile.get("known_public_evidence"))
    has_measurements = bool(profile.get("measurement_outputs"))
    actionability = str(profile.get("source_discovery_actionability") or "")

    if readiness == "blocked_no_crystal_coordinates":
        return (
            "coordinate_acquisition",
            95 if "lisdexamfetamine" in name else 82,
            True,
            "high-value target is blocked by missing license-compatible crystal coordinates",
        )
    if readiness == "coordinates_available_locally":
        return (
            "run_local_measurements",
            92,
            False,
            "license-controlled local coordinates are available and should be measured before claim curation",
        )
    if readiness == "measured_needs_claim_guardrails":
        if int(profile.get("enantiomer_labeled_block_count", 0) or 0) > 0:
            return (
                "curate_stereochemistry_scope",
                91,
                False,
                "paired or partial enantiomer evidence needs stereochemical claim-scope curation before polymorph use",
            )
        return (
            "curate_claim_boundary",
            89 if priority_group == "adhd_core" else 60,
            False,
            "local measurements exist and now need claim-boundary, backend-completion, and evidence-tier curation",
        )
    if actionability == "download_candidate" or readiness == "source_download_candidate":
        return (
            "download_public_cif_candidate",
            90,
            False,
            "source discovery found a public supporting-information CIF candidate for local measurement",
        )
    if readiness == "backend_disagreement_inspection":
        base = 88 if "carbamazepine" in name else 76
        return (
            "inspect_backend_disagreement",
            base,
            False,
            "backend disagreement can sharpen the uncertainty wrapper and paper case selection",
        )
    if actionability == "validate_coordinate_access" or readiness == "coordinate_access_validation":
        return (
            "validate_coordinate_access",
            86,
            False,
            "literature reports a structure but coordinate access and license terms are unresolved",
        )
    if actionability == "deeper_source_search" or readiness == "deeper_source_search":
        return (
            "deeper_source_search",
            78,
            False,
            "identity is known but the quick pass did not find usable crystal coordinates",
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
    if action_type == "download_public_cif_candidate":
        return "Download the public supporting-information CIFs into ignored local sources after license review, then inspect the CIF blocks."
    if action_type == "coordinate_acquisition":
        return "Search for license-compatible CIF or atom-coordinate evidence; do not run crystal MLIP without coordinates."
    if action_type == "run_local_measurements":
        return "Run MACE first, then AIMNet2 and UMA where the selected CIF block parses cleanly."
    if action_type == "curate_claim_boundary":
        return "Record which backends are complete, keep coordinates local-only, and block stability claims until experimental evidence exists."
    if action_type == "curate_stereochemistry_scope":
        return "Map S/R, racemate, and form labels; keep enantiomeric crystal comparison separate from polymorph benchmark claims."
    if action_type == "validate_coordinate_access":
        return "Validate the cited CSD/CCDC or publication coordinate route and record license constraints before measurement."
    if action_type == "deeper_source_search":
        return "Run a deeper CSD/CCDC, patent supplementary, and journal supporting-data search for crystal coordinates."
    if action_type == "source_discovery":
        return "Create a source-discovery proof record with DOI, structure availability, license status, and next measurement command."
    if action_type == "seed_source_discovery":
        return "Replace the queue seed with at least one concrete public structure/source candidate."
    if action_type == "maintain_guardrailed_pilot":
        return "Keep generated artifacts current and avoid promoting to stability-ranking claims."
    actions = profile.get("next_actions") or []
    return actions[0] if actions else "Review profile and assign a concrete next action."
