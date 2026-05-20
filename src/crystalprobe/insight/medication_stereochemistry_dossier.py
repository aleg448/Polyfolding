"""Curator dossiers for medication stereochemistry claim scopes."""

from __future__ import annotations

from typing import Any


REQUIRED_STEREOCHEMISTRY_FIELDS = (
    "source_racemate_or_enantiomer_scope",
    "local_block_stereochemistry_map",
    "solid_form_label_map",
    "ranking_interpretation",
    "promotion_decision",
)


def medication_stereochemistry_dossier_report(
    stereochemistry_report: dict[str, Any],
    seed_ranking_report: dict[str, Any],
    evidence_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build curation dossiers for enantiomer-scope medication targets."""

    evidence_by_target = {
        str(record.get("target")): dict(record)
        for record in (evidence_manifest or {}).get("records", [])
        if record.get("target")
    }
    ranking_by_target = {
        str(target.get("target")): dict(target)
        for target in seed_ranking_report.get("targets", [])
        if target.get("target")
    }
    dossiers = [
        _dossier_row(target, ranking_by_target.get(str(target.get("target")), {}), evidence_by_target.get(str(target.get("target")), {}))
        for target in stereochemistry_report.get("targets", [])
        if target.get("stereochemistry_status") != "no_enantiomeric_scope_detected"
    ]
    return {
        "schema_version": "0.1.0",
        "status": "medication_stereochemistry_dossier_recorded",
        "dossier_count": len(dossiers),
        "ready_for_claim_scope_count": sum(1 for dossier in dossiers if dossier["dossier_status"] == "claim_scope_ready"),
        "dossiers": dossiers,
        "required_fields": list(REQUIRED_STEREOCHEMISTRY_FIELDS),
        "policy": [
            "This dossier supports enantiomeric crystal comparison, not polymorph benchmark promotion.",
            "S/R model rankings remain inspection evidence until source scope and solid-form labels are curated.",
            "Racemate and single-enantiomer records must be separated before any stability or benchmark claim.",
        ],
    }


def medication_stereochemistry_dossier_markdown(report: dict[str, Any]) -> str:
    """Render stereochemistry curation dossiers as Markdown."""

    lines = [
        "# Medication Stereochemistry Dossier",
        "",
        f"- Status: `{report['status']}`",
        f"- Dossiers: `{report['dossier_count']}`",
        f"- Claim-scope ready: `{report['ready_for_claim_scope_count']}`",
        "",
        "## Dossiers",
        "",
        "| Target | Status | Rankable Backends | Missing Fields | Blockers |",
        "|---|---|---|---:|---|",
    ]
    for dossier in report["dossiers"]:
        lines.append(
            f"| {dossier['target']} | `{dossier['dossier_status']}` | "
            f"{', '.join(dossier['ranked_backends']) or 'none'} | `{len(dossier['missing_fields'])}` | "
            f"{'; '.join(dossier['blockers']) or 'none'} |"
        )
    for dossier in report["dossiers"]:
        lines.extend(["", f"## {dossier['target']}", ""])
        lines.append("- Enantiomer blocks:")
        for block in dossier["enantiomer_blocks"]:
            lines.append(
                f"  - `{block['structure_id']}` block `{block['block_id']}`: "
                f"`{block['stereochemical_scope']}` / CCDC `{block.get('ccdc_deposition') or 'not_recorded'}`"
            )
        lines.append("- Ranking rows:")
        for row in dossier["ranking_rows"]:
            lines.append(
                f"  - `{row['backend']}` rank `{row['rank']}` `{row['structure_id']}`: "
                f"delta `{float(row['delta_ev_per_formula_unit']):.6f}` eV/formula unit"
            )
        if not dossier["ranking_rows"]:
            lines.append("  - none")
        lines.append("- Next actions:")
        lines.extend(f"  - {action}" for action in dossier["next_actions"])
    lines.extend(["", "## Required Fields", ""])
    lines.extend(f"- `{field}`" for field in report["required_fields"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _dossier_row(target: dict[str, Any], ranking: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    present = _present_fields(target, ranking, evidence)
    missing = [field for field in REQUIRED_STEREOCHEMISTRY_FIELDS if field not in present]
    blockers = list(target.get("blockers", []))
    blockers.extend(f"{field} is required" for field in missing)
    status = "claim_scope_ready" if not blockers else "curation_required"
    return {
        "target": target.get("target"),
        "dossier_status": status,
        "stereochemistry_status": target.get("stereochemistry_status"),
        "enantiomer_blocks": list(target.get("enantiomer_labeled_blocks", [])),
        "ranked_backends": list(target.get("ranked_backends", [])),
        "ranking_rows": _ranking_rows(ranking),
        "present_fields": sorted(present),
        "missing_fields": missing,
        "blockers": _dedupe(blockers),
        "next_actions": _next_actions(missing, blockers),
    }


def _present_fields(target: dict[str, Any], ranking: dict[str, Any], evidence: dict[str, Any]) -> set[str]:
    present = set()
    if target.get("enantiomer_labeled_blocks"):
        present.add("local_block_stereochemistry_map")
    if evidence.get("form_label_map") and not _unresolved(evidence.get("form_label_map")):
        present.add("solid_form_label_map")
    if evidence.get("stereochemistry_decision") and not _unresolved(evidence.get("stereochemistry_decision")):
        present.add("source_racemate_or_enantiomer_scope")
    if ranking.get("ranking_status") == "ranked_within_backend":
        present.add("ranking_interpretation")
    if evidence.get("promotion_decision") in {"promote_enantiomeric_claim_scope", "promote_source_verified"}:
        present.add("promotion_decision")
    return present


def _ranking_rows(ranking: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for backend in ranking.get("backend_rankings", []):
        for row in backend.get("rows", []):
            rows.append({"backend": backend.get("backend"), **row})
    return rows


def _next_actions(missing: list[str], blockers: list[str]) -> list[str]:
    actions = []
    if "source_racemate_or_enantiomer_scope" in missing:
        actions.append("Lock whether each source form is racemic, single-enantiomer, conglomerate, or unresolved.")
    if "solid_form_label_map" in missing:
        actions.append("Map each local block to a source solid-form label before using rankings.")
    if "promotion_decision" in missing:
        actions.append("Record an explicit promote/do-not-promote decision for enantiomeric claim scope.")
    if blockers:
        actions.append("Keep S/R rankings below polymorph benchmark status until all blockers are resolved.")
    return actions or ["Dossier is claim-scope ready; proceed to release-boundary review."]


def _unresolved(value: Any) -> bool:
    if isinstance(value, str):
        text = value.casefold().strip()
        return text.startswith(("blocked", "pending", "unknown", "unresolved"))
    if isinstance(value, dict):
        text = " ".join(str(item).casefold() for item in value.values())
        return any(token in text for token in ("blocked", "pending", "unknown", "unresolved"))
    return not bool(value)


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
