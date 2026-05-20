"""Autonomous medication polymorphism triage reports."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any


BACKENDS = ("mace", "aimnet2", "uma")


def medication_polymorphism_autonomy_report(
    ingestion_report: dict[str, Any],
    measurement_summary: dict[str, Any],
) -> dict[str, Any]:
    """Detect unverified medication polymorphism candidates from local CIF metadata."""

    measurement_lookup = _measurement_lookup(measurement_summary)
    target_rows = [
        _target_row(target, measurement_lookup)
        for target in ingestion_report.get("targets", [])
    ]
    candidate_targets = [
        row for row in target_rows if row["autonomous_detection_status"] != "single_structure_only"
    ]
    rankable_targets = [
        row for row in target_rows if row["measurement_readiness"] == "rankable_within_backend"
    ]
    return {
        "schema_version": "0.1.0",
        "status": "medication_polymorphism_autonomy_recorded",
        "target_count": len(target_rows),
        "autonomous_candidate_target_count": len(candidate_targets),
        "rankable_target_count": len(rankable_targets),
        "targets": target_rows,
        "policy": [
            "Autonomous detection can identify same-formula local structure sets, but it does not verify polymorphism without form-label and stereochemistry review.",
            "Enantiomer, racemate, salt, solvate, co-crystal, and polymorph evidence are distinct medication-crystallography claim scopes.",
            "Enantiomer-labeled records can support enantiomeric crystal comparison, but must not be collapsed into polymorph claims.",
            "A target becomes rankable only when at least two eligible structures have measurements from the same backend.",
            "Backend rankings are within-backend inspection evidence, not cross-backend thermodynamic truth.",
            "All CCDC/CSD-derived medication evidence remains local-only until license review clears redistribution.",
        ],
    }


def medication_polymorphism_autonomy_markdown(report: dict[str, Any]) -> str:
    """Render the autonomous medication polymorphism triage report."""

    lines = [
        "# Medication Polymorphism Autonomy",
        "",
        f"- Status: `{report['status']}`",
        f"- Targets: `{report['target_count']}`",
        f"- Autonomous candidate targets: `{report['autonomous_candidate_target_count']}`",
        f"- Rankable targets: `{report['rankable_target_count']}`",
        "",
        "## Target Summary",
        "",
        "| Target | Detection | Measurement Readiness | Candidate Blocks | Shared Backends | Blockers |",
        "|---|---|---|---:|---|---|",
    ]
    for target in report["targets"]:
        lines.append(
            f"| {target['target']} | `{target['autonomous_detection_status']}` | "
            f"`{target['measurement_readiness']}` | `{target['candidate_block_count']}` | "
            f"{', '.join(target['shared_measured_backends']) or 'none'} | "
            f"{'; '.join(target['blockers']) or 'none'} |"
        )
    for target in report["targets"]:
        lines.extend(["", f"## {target['target']}", ""])
        lines.append(f"- Best formula group: `{target['best_formula_key'] or 'none'}`")
        lines.append(f"- Candidate block count: `{target['candidate_block_count']}`")
        lines.append(f"- Distinct space groups: `{target['distinct_space_group_count']}`")
        lines.append(f"- Claim scopes: `{', '.join(target['claim_scopes']) or 'none'}`")
        lines.append("- Candidate blocks:")
        if target["candidate_blocks"]:
            lines.extend(
                "  - "
                f"`{block['structure_id']}` block `{block['block_id']}`; role `{block['target_role']}`; "
                f"stereochemistry `{block['stereochemical_scope']}`; "
                f"space group `{block['space_group'] or 'unknown'}`; measured backends "
                f"`{', '.join(block['measured_backends']) or 'none'}`."
                for block in target["candidate_blocks"]
            )
        else:
            lines.append("  - none")
        lines.append("- Next actions:")
        lines.extend(f"  - {action}" for action in target["next_actions"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _target_row(target: dict[str, Any], measurement_lookup: dict[str, dict[str, Any]]) -> dict[str, Any]:
    eligible = [
        _block_row(block, measurement_lookup.get(str(block.get("structure_id")), {}))
        for block in target.get("selected_blocks", [])
        if _eligible_parent_like_block(block)
    ]
    grouped = _group_by_formula(eligible)
    best_group = _best_group(grouped)
    candidate_blocks = best_group["blocks"] if best_group else []
    shared_backends = _shared_measured_backends(candidate_blocks)
    blockers = _target_blockers(candidate_blocks, shared_backends)
    detection_status = _detection_status(candidate_blocks)
    readiness = _measurement_readiness(candidate_blocks, shared_backends)
    claim_scopes = _claim_scopes(candidate_blocks)
    return {
        "target": target.get("name"),
        "autonomous_detection_status": detection_status,
        "measurement_readiness": readiness,
        "best_formula_key": best_group["formula_key"] if best_group else "",
        "candidate_block_count": len(candidate_blocks),
        "distinct_space_group_count": len({block["space_group"] for block in candidate_blocks if block["space_group"]}),
        "shared_measured_backends": shared_backends,
        "candidate_blocks": candidate_blocks,
        "solid_form_scope_counts": _scope_counts(candidate_blocks),
        "claim_scopes": claim_scopes,
        "excluded_block_count": len(target.get("selected_blocks", [])) - len(eligible),
        "blockers": blockers,
        "next_actions": _next_actions(detection_status, readiness, blockers),
    }


def _eligible_parent_like_block(block: dict[str, Any]) -> bool:
    if not block.get("promote_to_profile"):
        return False
    role = str(block.get("target_role") or "").casefold()
    if "analogue" in role or "not_parent_proof" in role or "parse_check" in role:
        return False
    formula = _formula_key(block.get("formula") or block.get("expected_formula") or "")
    return bool(formula)


def _block_row(block: dict[str, Any], measurement: dict[str, Any]) -> dict[str, Any]:
    backend_rows = list(measurement.get("backend_measurements", []))
    measured_backends = [
        str(row.get("backend"))
        for row in backend_rows
        if row.get("status") == "measured" and row.get("backend")
    ]
    diagnostic_flags = sorted(
        {
            str(flag)
            for row in backend_rows
            for flag in row.get("diagnostic_flags", [])
        }
    )
    formula = str(block.get("formula") or block.get("expected_formula") or "")
    return {
        "block_id": str(block.get("block_id") or ""),
        "structure_id": str(block.get("structure_id") or ""),
        "target_role": str(block.get("target_role") or ""),
        "formula": formula,
        "formula_key": _formula_key(formula),
        "space_group": str(block.get("space_group") or ""),
        "ccdc_deposition": str(block.get("ccdc_deposition") or ""),
        "stereochemical_scope": _stereochemical_scope(block),
        "measured_backends": measured_backends,
        "diagnostic_flags": diagnostic_flags,
    }


def _measurement_lookup(measurement_summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(block.get("structure_id")): dict(block)
        for target in measurement_summary.get("targets", [])
        for block in target.get("blocks", [])
        if block.get("structure_id")
    }


def _group_by_formula(blocks: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for block in blocks:
        key = block["formula_key"]
        if key:
            grouped.setdefault(key, []).append(block)
    return grouped


def _best_group(grouped: dict[str, list[dict[str, Any]]]) -> dict[str, Any] | None:
    if not grouped:
        return None
    formula_key, blocks = sorted(
        grouped.items(),
        key=lambda item: (-len(item[1]), item[0]),
    )[0]
    return {"formula_key": formula_key, "blocks": blocks}


def _shared_measured_backends(blocks: list[dict[str, Any]]) -> list[str]:
    if len(blocks) < 2:
        return []
    counts: Counter[str] = Counter()
    for block in blocks:
        counts.update(set(block["measured_backends"]))
    return [backend for backend in BACKENDS if counts[backend] >= 2]


def _detection_status(candidate_blocks: list[dict[str, Any]]) -> str:
    if len(candidate_blocks) < 2:
        return "single_structure_only"
    space_groups = {block["space_group"] for block in candidate_blocks if block["space_group"]}
    if len(space_groups) >= 2:
        return "autonomous_polymorphism_candidate"
    return "same_formula_multi_record_candidate"


def _measurement_readiness(candidate_blocks: list[dict[str, Any]], shared_backends: list[str]) -> str:
    if len(candidate_blocks) < 2:
        return "insufficient_candidate_structures"
    if shared_backends:
        return "rankable_within_backend"
    measured = [block for block in candidate_blocks if block["measured_backends"]]
    if measured:
        return "partial_measurement_coverage"
    return "coordinates_only"


def _target_blockers(candidate_blocks: list[dict[str, Any]], shared_backends: list[str]) -> list[str]:
    blockers = []
    if len(candidate_blocks) < 2:
        blockers.append("at least two eligible same-formula parent-like structures are required")
    if len(candidate_blocks) >= 2 and not shared_backends:
        blockers.append("measure at least two candidate structures with the same backend")
    labels = " ".join(block["block_id"] for block in candidate_blocks).casefold()
    if any(token in labels for token in ("(+)", "(-)", "(r)", "(s)", " r-", " s-")):
        blockers.append("resolve stereochemistry/enantiomer labels before calling records polymorphs")
        blockers.append("route enantiomer-labeled records through enantiomeric crystal comparison")
    if any("related_" in block["target_role"].casefold() for block in candidate_blocks):
        blockers.append("resolve related-record form labels before promotion")
    return blockers


def _next_actions(detection_status: str, readiness: str, blockers: list[str]) -> list[str]:
    if detection_status == "single_structure_only":
        return ["Acquire or select an additional parent-like structure before autonomous polymorphism triage."]
    actions = []
    if readiness != "rankable_within_backend":
        actions.append("Run the same backend on at least two selected candidate structures.")
    actions.extend(blocker for blocker in blockers if "measure at least two candidate structures" not in blocker)
    actions.append("Keep the result below verified benchmark status until form labels and license boundaries are resolved.")
    return actions


def _formula_key(formula: str) -> str:
    text = formula.replace(",", " ")
    counts: Counter[str] = Counter()
    for element, count in re.findall(r"([A-Z][a-z]?)(\d*)", text):
        counts[element] += int(count or "1")
    if not counts:
        return ""
    return " ".join(f"{element}{counts[element]}" for element in sorted(counts))


def _stereochemical_scope(block: dict[str, Any]) -> str:
    text = f"{block.get('block_id', '')} {block.get('target_role', '')}".casefold()
    if "(s)" in text or "(+)" in text or "s_plus" in text:
        return "single_enantiomer_s_or_plus"
    if "(r)" in text or "(-)" in text or "r_minus" in text:
        return "single_enantiomer_r_or_minus"
    if "racem" in text:
        return "racemate"
    if "salt" in text:
        return "salt_form_unspecified_chirality"
    return "unspecified_or_achiral"


def _scope_counts(blocks: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter(block["stereochemical_scope"] for block in blocks)
    return dict(sorted(counts.items()))


def _claim_scopes(blocks: list[dict[str, Any]]) -> list[str]:
    scopes = set()
    stereo_scopes = {block["stereochemical_scope"] for block in blocks}
    if any(scope.startswith("single_enantiomer") for scope in stereo_scopes):
        scopes.add("enantiomeric_crystal_comparison")
    if len({block["space_group"] for block in blocks if block["space_group"]}) >= 2:
        scopes.add("candidate_polymorph_or_form_comparison")
    if any("salt" in block["target_role"].casefold() for block in blocks):
        scopes.add("salt_form_comparison")
    return sorted(scopes)
