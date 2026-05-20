"""CPOSS promotion burn-down planning reports."""

from __future__ import annotations

from collections import Counter
from typing import Any


PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2, "unspecified": 3}


def cposs_promotion_burndown_report(
    cposs_promotion: dict[str, Any],
    cposs_block_mapping: dict[str, Any],
    *,
    target_pair_count: int = 20,
) -> dict[str, Any]:
    """Build an actionable plan for reaching a verified CPOSS pair milestone."""

    promoted_count = int(cposs_promotion.get("promoted_count", 0))
    remaining_to_target = max(target_pair_count - promoted_count, 0)
    candidate_rows = _candidate_rows(cposs_promotion, cposs_block_mapping)
    selected_candidates = candidate_rows[:remaining_to_target] if remaining_to_target else []
    selected_ids = {row["candidate_id"] for row in selected_candidates}
    block_rows = _block_rows(cposs_block_mapping, selected_ids)
    blocker_summary = _blocker_summary(selected_candidates, block_rows)
    status = "target_reached" if remaining_to_target == 0 else "burndown_required"
    return {
        "schema_version": "0.1.0",
        "status": status,
        "target_pair_count": target_pair_count,
        "promoted_count": promoted_count,
        "remaining_to_target": remaining_to_target,
        "available_candidate_count": len(candidate_rows),
        "selected_candidate_count": len(selected_candidates),
        "selected_block_count": len(block_rows),
        "candidate_plan": selected_candidates,
        "block_action_plan": block_rows,
        "blocker_summary": blocker_summary,
        "acceptance_gates": [
            "Every selected candidate must have a non-ambiguous experimental stability ordering.",
            "Both blocks in every selected candidate must be block_form_mapping_locked with high confidence.",
            "Every selected block must have explicit cell, space-group, formula, and source-label checks.",
            "Every selected block must have resolved license and true/false disorder annotations.",
            "Every selected candidate needs curator and reviewer fields before promotion_decision can become promote.",
        ],
        "policy": [
            "This is a burn-down plan, not a benchmark result.",
            "Candidate order is a local curation priority and must not be reported as scientific ranking.",
            "The promotion gate remains canonical for deciding whether verified PolymorphPair records can be emitted.",
        ],
    }


def cposs_promotion_burndown_markdown(report: dict[str, Any]) -> str:
    """Render the CPOSS promotion burn-down report as Markdown."""

    lines = [
        "# CPOSS Promotion Burn-Down",
        "",
        f"- Status: `{report['status']}`",
        f"- Target verified pairs: `{report['target_pair_count']}`",
        f"- Promoted pairs: `{report['promoted_count']}`",
        f"- Remaining to target: `{report['remaining_to_target']}`",
        f"- Available candidates: `{report['available_candidate_count']}`",
        f"- Selected candidates: `{report['selected_candidate_count']}`",
        f"- Selected block rows: `{report['selected_block_count']}`",
        "",
        "## Candidate Plan",
        "",
        "| Order | Candidate | Family | Priority | Status | Mapping Ready | Next Actions |",
        "|---:|---|---|---|---|---|---|",
    ]
    for index, row in enumerate(report["candidate_plan"], start=1):
        actions = "; ".join(row["next_actions"]) or "none"
        lines.append(
            f"| `{index}` | `{row['candidate_id']}` | `{row['family']}` | `{row['priority']}` | "
            f"`{row['promotion_status']}` | `{row['mapping_ready']}` | {actions} |"
        )
    lines.extend(
        [
            "",
            "## Block Action Plan",
            "",
            "| Block | Family | Selected Uses | Priority | Top Candidate | Status | Blockers |",
            "|---|---|---:|---|---|---|---|",
        ]
    )
    for row in report["block_action_plan"]:
        blockers = "; ".join(row["blockers"]) or "none"
        lines.append(
            f"| `{row['block_id']}` | `{row['family']}` | `{row['selected_candidate_count']}` | "
            f"`{row['priority']}` | `{row['top_candidate_id']}` | `{row['mapping_status']}` | {blockers} |"
        )
    lines.extend(
        [
            "",
            "## Blocker Summary",
            "",
            "| Blocker | Count |",
            "|---|---:|",
        ]
    )
    for row in report["blocker_summary"]:
        lines.append(f"| {row['blocker']} | `{row['count']}` |")
    lines.extend(["", "## Acceptance Gates", ""])
    lines.extend(f"- {item}" for item in report["acceptance_gates"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _candidate_rows(
    cposs_promotion: dict[str, Any],
    cposs_block_mapping: dict[str, Any],
) -> list[dict[str, Any]]:
    mapping_by_id = {
        str(row.get("candidate_id")): dict(row)
        for row in cposs_block_mapping.get("candidate_rows", [])
        if row.get("candidate_id")
    }
    rows = []
    for row in cposs_promotion.get("curation_queue", []):
        candidate_id = str(row.get("candidate_id") or "")
        mapping = mapping_by_id.get(candidate_id, {})
        promotion_status = str(row.get("promotion_status") or "unspecified")
        next_actions = _next_actions(row, mapping)
        rows.append(
            {
                "candidate_id": candidate_id,
                "family": str(row.get("family") or mapping.get("family") or ""),
                "priority": str(row.get("priority") or mapping.get("priority") or "unspecified"),
                "promotion_status": promotion_status,
                "mapping_ready": bool(mapping.get("mapping_ready", False)),
                "structure_a": str(mapping.get("structure_a") or ""),
                "structure_b": str(mapping.get("structure_b") or ""),
                "model_gap_kj_mol_per_formula_unit": float(mapping.get("model_gap_kj_mol_per_formula_unit") or 0.0),
                "next_actions": next_actions,
                "upgrade_requirements": list(row.get("upgrade_requirements", [])),
                "mapping_blockers": list(mapping.get("blockers", [])),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            PRIORITY_RANK.get(row["priority"], PRIORITY_RANK["unspecified"]),
            0 if row["promotion_status"] == "literature_mapped_candidate" else 1,
            float(row["model_gap_kj_mol_per_formula_unit"]),
            row["candidate_id"],
        ),
    )


def _next_actions(promotion_row: dict[str, Any], mapping_row: dict[str, Any]) -> list[str]:
    actions = []
    if mapping_row and mapping_row.get("mapping_ready") is not True:
        actions.append("lock block-to-form mapping for both structures")
    if promotion_row.get("upgrade_requirements"):
        actions.extend(str(item) for item in promotion_row["upgrade_requirements"][:3])
    if not actions and promotion_row.get("next_required_fields"):
        actions.append("fill required evidence fields")
    return actions


def _block_rows(cposs_block_mapping: dict[str, Any], selected_candidate_ids: set[str]) -> list[dict[str, Any]]:
    selected_candidates = [
        row for row in cposs_block_mapping.get("candidate_rows", []) if row.get("candidate_id") in selected_candidate_ids
    ]
    selected_by_block = _selected_uses_by_block(selected_candidates)
    rows = []
    for block in cposs_block_mapping.get("block_rows", []):
        block_key = (str(block.get("family") or ""), str(block.get("block_id") or ""))
        uses = selected_by_block.get(block_key, [])
        if not uses:
            continue
        priority = _best_priority(uses)
        top_candidate = _top_candidate(uses)
        rows.append(
            {
                "family": block_key[0],
                "block_id": block_key[1],
                "mapping_status": str(block.get("mapping_status") or "unmapped"),
                "mapping_confidence": str(block.get("mapping_confidence") or "unknown"),
                "promotion_ready": bool(block.get("promotion_ready", False)),
                "priority": priority,
                "selected_candidate_count": len(uses),
                "top_candidate_id": str(top_candidate.get("candidate_id") if top_candidate else ""),
                "blockers": list(block.get("blockers", [])),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            0 if row["promotion_ready"] else 1,
            PRIORITY_RANK.get(row["priority"], PRIORITY_RANK["unspecified"]),
            -int(row["selected_candidate_count"]),
            row["block_id"],
        ),
    )


def _selected_uses_by_block(candidate_rows: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    uses: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in candidate_rows:
        family = str(row.get("family") or "")
        for key in ("structure_a", "structure_b"):
            block_id = str(row.get(key) or "")
            if family and block_id:
                uses.setdefault((family, block_id), []).append(dict(row))
    return uses


def _blocker_summary(candidate_rows: list[dict[str, Any]], block_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for row in candidate_rows:
        counts.update(str(item) for item in row.get("upgrade_requirements", []))
        counts.update(str(item) for item in row.get("mapping_blockers", []))
    for row in block_rows:
        counts.update(str(item) for item in row.get("blockers", []))
    return [{"blocker": blocker, "count": count} for blocker, count in counts.most_common()]


def _best_priority(candidate_rows: list[dict[str, Any]]) -> str:
    if not candidate_rows:
        return "unspecified"
    return min(
        (str(row.get("priority", "unspecified")) for row in candidate_rows),
        key=lambda priority: PRIORITY_RANK.get(priority, PRIORITY_RANK["unspecified"]),
    )


def _top_candidate(candidate_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not candidate_rows:
        return None
    return sorted(
        candidate_rows,
        key=lambda row: (
            PRIORITY_RANK.get(str(row.get("priority", "unspecified")), PRIORITY_RANK["unspecified"]),
            float(row.get("model_gap_kj_mol_per_formula_unit", 0.0)),
            str(row.get("candidate_id")),
        ),
    )[0]
