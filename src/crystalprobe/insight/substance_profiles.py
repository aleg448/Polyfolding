"""Substance-level research profiles assembled from local CrystalProbe evidence."""

from __future__ import annotations

from typing import Any


def substance_profile_report(
    *,
    therapeutic_priority: dict[str, Any],
    ccdc_sources: dict[str, Any] | None = None,
    lisdexamfetamine_proof: dict[str, Any] | None = None,
    evidence_tiers: dict[str, Any] | None = None,
    cposs_disagreement: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge local curation and measurement artifacts into substance profiles."""

    profiles: dict[str, dict[str, Any]] = {}
    for group in therapeutic_priority.get("priority_groups", []):
        for target in group.get("targets", []):
            profile = _base_profile(target, group)
            profiles[_key(profile["name"])] = profile

    _merge_ccdc_sources(profiles, ccdc_sources or {})
    _merge_lisdexamfetamine_proof(profiles, lisdexamfetamine_proof or {})
    _merge_evidence_tiers(profiles, evidence_tiers or {})
    _merge_cposs_disagreement(profiles, cposs_disagreement or {})

    for profile in profiles.values():
        profile["readiness"] = _readiness(profile)
        profile["claim_boundary"] = _claim_boundary(profile)

    ordered = sorted(profiles.values(), key=lambda item: (item["priority_group"], item["name"].casefold()))
    return {
        "schema_version": "0.1.0",
        "status": "substance_profiles_recorded",
        "profile_count": len(ordered),
        "profiles": ordered,
        "policy": [
            "Profiles summarize research evidence and are not medical advice.",
            "Medication relevance is used only to prioritize solid-form and backend-behaviour curation.",
            "Backend measurements are not experimental stability labels unless a verified evidence tier says so.",
            "Coordinate-bearing gated CCDC/CSD artifacts remain local unless redistribution is license-cleared.",
        ],
    }


def substance_profile_markdown(report: dict[str, Any]) -> str:
    """Render substance profiles as a compact Markdown report."""

    lines = [
        "# CrystalProbe Substance Profiles",
        "",
        f"- Status: `{report['status']}`",
        f"- Profiles: `{report['profile_count']}`",
        "",
        "## Summary",
        "",
        "| Substance | Role | Readiness | Evidence Tier | Backend Signal | Next Action |",
        "|---|---|---|---|---|---|",
    ]
    for profile in report["profiles"]:
        lines.append(
            f"| {profile['name']} | {profile.get('role') or 'not recorded'} | "
            f"`{profile['readiness']}` | `{profile.get('evidence_tier') or 'not_assigned'}` | "
            f"{_backend_signal(profile)} | {_first(profile.get('next_actions'))} |"
        )

    for profile in report["profiles"]:
        lines.extend(["", f"## {profile['name']}", ""])
        lines.append(f"- Role: {profile.get('role') or 'not recorded'}")
        lines.append(f"- Priority group: `{profile['priority_group']}`")
        lines.append(f"- Source status: `{profile.get('source_status') or 'not_recorded'}`")
        lines.append(f"- Readiness: `{profile['readiness']}`")
        lines.append(f"- Claim boundary: {profile['claim_boundary']}")
        if profile.get("known_public_evidence"):
            lines.append("- Public evidence:")
            lines.extend(f"  - {item}" for item in profile["known_public_evidence"])
        if profile.get("local_sources"):
            lines.append("- Local source records:")
            lines.extend(f"  - {item}" for item in profile["local_sources"])
        if profile.get("measurement_outputs"):
            lines.append("- Measurement outputs:")
            lines.extend(f"  - `{item}`" for item in profile["measurement_outputs"])
        if profile.get("proof_layers"):
            lines.append("- Proof layers:")
            lines.extend(
                f"  - `{layer.get('layer')}`: `{layer.get('status')}`"
                for layer in profile["proof_layers"]
            )
        if profile.get("cposs_backend_profile"):
            backend = profile["cposs_backend_profile"]
            lines.append(
                "- CPOSS backend profile: "
                f"family `{backend['family']}`, ranking consensus `{backend['ranking_consensus']}`, "
                f"mean flag Jaccard `{float(backend['mean_flag_jaccard']):.3f}`, "
                f"decision `{backend['decision']}`."
            )
        if profile.get("blocked_claims"):
            lines.append("- Blocked claims:")
            lines.extend(f"  - {item}" for item in profile["blocked_claims"])
        if profile.get("next_actions"):
            lines.append("- Next actions:")
            lines.extend(f"  - {item}" for item in profile["next_actions"])

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _base_profile(target: dict[str, Any], group: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": target["name"],
        "role": target.get("role"),
        "priority_group": group.get("group_id", "unassigned"),
        "priority_rationale": group.get("rationale"),
        "source_status": target.get("status"),
        "cposs_family_code": target.get("cposs_family_code"),
        "known_public_evidence": list(target.get("known_public_evidence", [])),
        "local_sources": [],
        "measurement_outputs": [],
        "proof_layers": [],
        "next_actions": [target["next_action"]] if target.get("next_action") else [],
        "allowed_uses": [],
        "blocked_claims": [],
        "required_next_steps": [],
    }


def _merge_ccdc_sources(profiles: dict[str, dict[str, Any]], ccdc_sources: dict[str, Any]) -> None:
    for record in ccdc_sources.get("records", []):
        name = str(record.get("name") or record.get("therapeutic_context") or "unknown")
        key = _key(name)
        if key not in profiles and record.get("selected_block_id") == "AMPETP":
            profiles[key] = _ccdc_only_profile(record)
        profile = profiles.get(key) or profiles.get(_key(str(record.get("therapeutic_context", ""))))
        if not profile:
            continue
        source = f"{record.get('selected_block_id')} ({record.get('ccdc_deposition') or 'no deposition recorded'})"
        if source not in profile["local_sources"]:
            profile["local_sources"].append(source)
        for output in record.get("measurement_outputs", []):
            _append_unique(profile["measurement_outputs"], output)
        if record.get("interpretation"):
            _append_unique(profile["known_public_evidence"], record["interpretation"])


def _ccdc_only_profile(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": record.get("name", "unknown CCDC target"),
        "role": record.get("therapeutic_context"),
        "priority_group": "measured_proxy_targets",
        "priority_rationale": "Measured local CCDC/CSD target used to prove the CrystalProbe workflow.",
        "source_status": "measured_ccdc_local_export",
        "cposs_family_code": None,
        "known_public_evidence": [record.get("interpretation", "")],
        "local_sources": [],
        "measurement_outputs": [],
        "proof_layers": [],
        "next_actions": ["Keep this as a guarded methods pilot unless license and stability evidence support promotion."],
        "allowed_uses": [],
        "blocked_claims": [],
        "required_next_steps": [],
    }


def _merge_lisdexamfetamine_proof(profiles: dict[str, dict[str, Any]], proof: dict[str, Any]) -> None:
    target = proof.get("target", {})
    profile = profiles.get(_key(str(target.get("name", ""))))
    if not profile:
        return
    profile["proof_layers"] = list(proof.get("proof_layers", []))
    for layer in proof.get("proof_layers", []):
        for output in layer.get("measurement_outputs", []):
            _append_unique(profile["measurement_outputs"], output)
        if layer.get("blocker"):
            _append_unique(profile["required_next_steps"], layer["blocker"])
        if layer.get("limitation"):
            _append_unique(profile["blocked_claims"], layer["limitation"])
    for action in proof.get("next_actions", []):
        _append_unique(profile["next_actions"], action)


def _merge_evidence_tiers(profiles: dict[str, dict[str, Any]], evidence_tiers: dict[str, Any]) -> None:
    for target in evidence_tiers.get("targets", []):
        matched = _match_profiles(profiles, str(target.get("target", "")))
        if not matched:
            continue
        tier = target.get("tier", {})
        for profile in matched:
            profile["evidence_tier"] = tier.get("tier")
            profile["evidence_status"] = tier.get("status")
            profile["allowed_uses"] = list(tier.get("allowed_uses", []))
            profile["blocked_claims"] = list(dict.fromkeys(profile["blocked_claims"] + list(tier.get("blocked_claims", []))))
            profile["required_next_steps"] = list(
                dict.fromkeys(profile["required_next_steps"] + list(tier.get("required_next_steps", [])))
            )


def _merge_cposs_disagreement(profiles: dict[str, dict[str, Any]], disagreement: dict[str, Any]) -> None:
    family_to_profile = {
        str(profile.get("cposs_family_code")): profile
        for profile in profiles.values()
        if profile.get("cposs_family_code")
    }
    for family in disagreement.get("families", []):
        profile = family_to_profile.get(str(family.get("family")))
        if not profile:
            continue
        decision = "inspect"
        if family.get("ranking_consensus") and float(family.get("mean_flag_jaccard", 0.0)) >= 0.75:
            decision = "high_confidence_behavioral"
        profile["cposs_backend_profile"] = {
            "family": family.get("family"),
            "backend_count": family.get("backend_count"),
            "ranking_consensus": family.get("ranking_consensus"),
            "mean_flag_jaccard": family.get("mean_flag_jaccard"),
            "decision": decision,
            "lower_structures": {
                backend: row.get("lower_structure")
                for backend, row in family.get("backends", {}).items()
            },
        }
        _append_unique(profile["measurement_outputs"], "outputs/cposs_high_priority_backend_disagreement.json")
        if decision == "inspect":
            _append_unique(profile["next_actions"], "Inspect CPOSS backend disagreement before using this family as a paper-facing example.")


def _readiness(profile: dict[str, Any]) -> str:
    tier = profile.get("evidence_tier")
    if tier == "blocked_no_coordinates":
        return "blocked_no_crystal_coordinates"
    if profile.get("cposs_backend_profile", {}).get("decision") == "inspect":
        return "backend_disagreement_inspection"
    if tier == "agi_assisted_guardrailed_pilot":
        return "guardrailed_pilot_profile"
    if profile.get("measurement_outputs"):
        return "measured_needs_claim_guardrails"
    if profile.get("known_public_evidence"):
        return "source_discovery_profile"
    return "queue_seed_needs_sources"


def _claim_boundary(profile: dict[str, Any]) -> str:
    if profile.get("blocked_claims"):
        return "guardrails_explicit"
    if profile.get("measurement_outputs"):
        return "measurements_present_but_claims_unassigned"
    return "source_discovery_only"


def _match_profiles(profiles: dict[str, dict[str, Any]], target: str) -> list[dict[str, Any]]:
    normalized = _key(target)
    if "lisdexamfetamine" in normalized:
        return _present(profiles.get("lisdexamfetamine dimesylate"))
    if "ampetp" in normalized or "amphetamine dihydrogen phosphate" in normalized:
        return _present(profiles.get("(+)-amphetamine dihydrogen phosphate"))
    if "ibuprofen" in normalized:
        return _present(profiles.get("ibuprofen"))
    if "cposs" in normalized and ("ibp" in normalized or "cbz" in normalized):
        return [
            profile
            for profile in (profiles.get("ibuprofen"), profiles.get("carbamazepine"))
            if profile is not None
        ]
    return _present(profiles.get(normalized))


def _backend_signal(profile: dict[str, Any]) -> str:
    if profile.get("evidence_tier") == "blocked_no_coordinates" and profile.get("measurement_outputs"):
        return "parent/proxy measured"
    backend = profile.get("cposs_backend_profile")
    if backend:
        return f"{backend['decision']} ({backend['family']})"
    if profile.get("measurement_outputs"):
        return "measured"
    return "not measured"


def _first(items: list[str] | None) -> str:
    return items[0] if items else "Add source evidence."


def _append_unique(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def _present(profile: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [profile] if profile is not None else []


def _key(value: str) -> str:
    return " ".join(value.casefold().split())
