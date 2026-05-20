"""Medication stereochemistry and enantiomeric crystal comparison reports."""

from __future__ import annotations

from typing import Any


def medication_stereochemistry_report(
    autonomy_report: dict[str, Any],
    seed_ranking_report: dict[str, Any],
) -> dict[str, Any]:
    """Summarize enantiomer/racemate claim scopes without promoting polymorph claims."""

    ranking_by_target = {
        str(target.get("target")): dict(target)
        for target in seed_ranking_report.get("targets", [])
        if target.get("target")
    }
    targets = [
        _target_row(target, ranking_by_target.get(str(target.get("target")), {}))
        for target in autonomy_report.get("targets", [])
    ]
    enantiomer_targets = [
        target
        for target in targets
        if target["stereochemistry_status"] != "no_enantiomeric_scope_detected"
    ]
    return {
        "schema_version": "0.1.0",
        "status": "medication_stereochemistry_recorded",
        "target_count": len(targets),
        "enantiomer_scope_target_count": len(enantiomer_targets),
        "rankable_enantiomer_scope_target_count": sum(
            1 for target in enantiomer_targets if target["ranking_status"] == "ranked_within_backend"
        ),
        "targets": targets,
        "policy": [
            "Enantiomeric crystal comparison is a first-class medication-crystallography scope.",
            "S/R or +/- records must not be treated as polymorphs unless the evidence dossier explicitly maps the solid-form scope.",
            "Racemates, conglomerates, salts, solvates, co-crystals, and true polymorphs require separate claim labels.",
            "Within-backend enantiomer rankings are model inspection evidence, not experimental stereochemical stability truth.",
        ],
    }


def medication_stereochemistry_markdown(report: dict[str, Any]) -> str:
    """Render medication stereochemistry report as Markdown."""

    lines = [
        "# Medication Stereochemistry Scope",
        "",
        f"- Status: `{report['status']}`",
        f"- Targets: `{report['target_count']}`",
        f"- Enantiomer-scope targets: `{report['enantiomer_scope_target_count']}`",
        f"- Rankable enantiomer-scope targets: `{report['rankable_enantiomer_scope_target_count']}`",
        "",
        "## Targets",
        "",
        "| Target | Status | S/R Blocks | Claim Scopes | Ranking | Blockers |",
        "|---|---|---:|---|---|---|",
    ]
    for target in report["targets"]:
        lines.append(
            f"| {target['target']} | `{target['stereochemistry_status']}` | "
            f"`{target['enantiomer_labeled_block_count']}` | "
            f"{', '.join(target['claim_scopes']) or 'none'} | `{target['ranking_status']}` | "
            f"{'; '.join(target['blockers']) or 'none'} |"
        )
    for target in report["targets"]:
        lines.extend(["", f"## {target['target']}", ""])
        lines.append("- Stereochemical groups:")
        for scope, count in target["solid_form_scope_counts"].items():
            lines.append(f"  - `{scope}`: `{count}`")
        if not target["solid_form_scope_counts"]:
            lines.append("  - none")
        lines.append("- Candidate blocks:")
        for block in target["enantiomer_labeled_blocks"]:
            lines.append(
                f"  - `{block['structure_id']}` block `{block['block_id']}`: "
                f"`{block['stereochemical_scope']}`"
            )
        if not target["enantiomer_labeled_blocks"]:
            lines.append("  - none")
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _target_row(target: dict[str, Any], ranking: dict[str, Any]) -> dict[str, Any]:
    blocks = list(target.get("candidate_blocks", []))
    enantiomer_blocks = [
        dict(block)
        for block in blocks
        if str(block.get("stereochemical_scope", "")).startswith("single_enantiomer")
    ]
    claim_scopes = list(target.get("claim_scopes", []))
    blockers = []
    if enantiomer_blocks and "enantiomeric_crystal_comparison" not in claim_scopes:
        blockers.append("enantiomer-labeled blocks require enantiomeric_crystal_comparison claim scope")
    if enantiomer_blocks:
        blockers.append("do not collapse enantiomeric records into polymorph benchmark claims")
    blockers.extend(
        str(blocker)
        for blocker in target.get("blockers", [])
        if "stereochemistry" in str(blocker).casefold() or "enantiomer" in str(blocker).casefold()
    )
    return {
        "target": target.get("target"),
        "stereochemistry_status": _stereochemistry_status(enantiomer_blocks, claim_scopes),
        "claim_scopes": claim_scopes,
        "solid_form_scope_counts": dict(target.get("solid_form_scope_counts", {})),
        "enantiomer_labeled_block_count": len(enantiomer_blocks),
        "enantiomer_labeled_blocks": enantiomer_blocks,
        "ranking_status": ranking.get("ranking_status", "not_rankable"),
        "ranked_backends": list(ranking.get("ranked_backends", [])),
        "blockers": _dedupe(blockers),
    }


def _stereochemistry_status(enantiomer_blocks: list[dict[str, Any]], claim_scopes: list[str]) -> str:
    if not enantiomer_blocks:
        return "no_enantiomeric_scope_detected"
    scopes = {str(block.get("stereochemical_scope")) for block in enantiomer_blocks}
    if {"single_enantiomer_s_or_plus", "single_enantiomer_r_or_minus"}.issubset(scopes):
        return "paired_enantiomer_records_available"
    if "enantiomeric_crystal_comparison" in claim_scopes:
        return "partial_enantiomeric_scope_detected"
    return "enantiomer_labeled_records_need_claim_scope"


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
