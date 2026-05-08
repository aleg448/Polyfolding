"""CPOSS pair-candidate reports from local mini-benchmark summaries."""

from __future__ import annotations

from typing import Any

from crystalprobe.insight.evidence_tiers import classify_evidence_tier


def cposs_pair_candidate_report(cposs_bridge: dict[str, Any]) -> dict[str, Any]:
    """Convert a CPOSS mini-benchmark bridge into adjacent pair candidates."""

    candidates: list[dict[str, Any]] = []
    for family, data in sorted(cposs_bridge.get("families", {}).items()):
        structures = sorted(
            data.get("structures", []),
            key=lambda row: float(row.get("relative_kj_mol_per_formula_unit", 0.0)),
        )
        for index, (left, right) in enumerate(zip(structures, structures[1:]), start=1):
            left_energy = float(left["relative_kj_mol_per_formula_unit"])
            right_energy = float(right["relative_kj_mol_per_formula_unit"])
            candidates.append(
                {
                    "candidate_id": f"{family.lower()}_{left['block_id'].lower()}_vs_{right['block_id'].lower()}",
                    "family": family,
                    "rank_index": index,
                    "structure_a": _structure_stub(left),
                    "structure_b": _structure_stub(right),
                    "model_gap_kj_mol_per_formula_unit": right_energy - left_energy,
                    "model_lower_energy_structure": left["block_id"],
                    "curation_status": "needs_experimental_evidence",
                    "promotion_blockers": [
                        "Attach experimental stability ordering with DOI or durable URL.",
                        "Verify source redistribution license for both structures.",
                        "Record explicit disorder annotations for both structures.",
                        "Review local diagnostic flags before using this pair in headline metrics.",
                    ],
                    "diagnostic_flags": sorted(
                        set(left.get("local_diagnostic_flags", [])) | set(right.get("local_diagnostic_flags", []))
                    ),
                }
            )
    return {
        "schema_version": "0.1.0",
        "title": "CPOSS local pair-candidate queue",
        "status": "candidate_queue_requires_curation",
        "family_count": len(cposs_bridge.get("families", {})),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "guardrails": [
            "These are adjacent local MACE relative-energy pairs, not verified polymorph benchmark records.",
            "No candidate can be promoted until experimental stability evidence, source license, and disorder annotations are reviewed.",
            "Candidate IDs preserve CPOSS block IDs to keep the queue auditable without embedding coordinate data.",
        ],
    }


def cposs_pair_candidate_markdown(report: dict[str, Any]) -> str:
    """Render CPOSS pair candidates as Markdown."""

    lines = [
        f"# {report['title']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Families: `{report['family_count']}`",
        f"- Candidate pairs: `{report['candidate_count']}`",
        "",
        "## Candidates",
        "",
        "| Candidate | Family | A | B | Model lower | Gap (kJ/mol/f.u.) | Status | Flags |",
        "|---|---|---|---|---|---:|---|---|",
    ]
    for candidate in report["candidates"]:
        lines.append(
            f"| `{candidate['candidate_id']}` | {candidate['family']} | "
            f"{candidate['structure_a']['block_id']} | {candidate['structure_b']['block_id']} | "
            f"{candidate['model_lower_energy_structure']} | "
            f"{float(candidate['model_gap_kj_mol_per_formula_unit']):.3f} | "
            f"`{candidate['curation_status']}` | "
            f"{', '.join(candidate['diagnostic_flags']) or 'none'} |"
        )
    lines.extend(["", "## Promotion Blockers", ""])
    for blocker in report["candidates"][0]["promotion_blockers"] if report["candidates"] else []:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Guardrails", ""])
    lines.extend(f"- {guardrail}" for guardrail in report["guardrails"])
    return "\n".join(lines).rstrip() + "\n"


def cposs_pair_triage_report(candidate_report: dict[str, Any]) -> dict[str, Any]:
    """Prioritize CPOSS pair candidates for human evidence curation."""

    triaged = [_triage_candidate(candidate) for candidate in candidate_report.get("candidates", [])]
    triaged.sort(key=lambda row: (-row["priority_score"], row["model_gap_kj_mol_per_formula_unit"], row["candidate_id"]))
    family_counts: dict[str, int] = {}
    for row in triaged:
        family_counts[row["family"]] = family_counts.get(row["family"], 0) + 1
    return {
        "schema_version": "0.1.0",
        "title": "CPOSS pair-candidate triage",
        "status": "triage_requires_human_evidence_review",
        "candidate_count": len(triaged),
        "family_counts": family_counts,
        "priority_counts": _priority_counts(triaged),
        "top_candidates": triaged,
        "guardrails": [
            "Triage priority is based on local model gaps and queue position only.",
            "A high-priority candidate is not a verified stability claim.",
            "Every candidate still requires experimental stability evidence, source-license review, and disorder annotation.",
        ],
    }


def cposs_pair_triage_markdown(report: dict[str, Any]) -> str:
    """Render a CPOSS candidate triage report as Markdown."""

    lines = [
        f"# {report['title']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Candidate pairs: `{report['candidate_count']}`",
        "",
        "## Priority Counts",
        "",
    ]
    for priority, count in sorted(report["priority_counts"].items()):
        lines.append(f"- `{priority}`: `{count}`")
    lines.extend(
        [
            "",
            "## Triage Queue",
            "",
            "| Priority | Score | Candidate | Family | Gap (kJ/mol/f.u.) | Why first | Evidence tasks |",
            "|---|---:|---|---|---:|---|---|",
        ]
    )
    for row in report["top_candidates"]:
        lines.append(
            f"| `{row['priority']}` | {row['priority_score']} | `{row['candidate_id']}` | "
            f"{row['family']} | {float(row['model_gap_kj_mol_per_formula_unit']):.3f} | "
            f"{'; '.join(row['triage_reasons'])} | {'; '.join(row['evidence_tasks'])} |"
        )
    lines.extend(["", "## Guardrails", ""])
    lines.extend(f"- {guardrail}" for guardrail in report["guardrails"])
    return "\n".join(lines).rstrip() + "\n"


def cposs_evidence_workpack(
    triage_report: dict[str, Any],
    *,
    max_candidates: int | None = None,
    evidence_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create curator-fillable evidence forms from the CPOSS triage queue."""

    candidates = triage_report.get("top_candidates", [])
    if max_candidates is not None:
        candidates = candidates[:max_candidates]
    overrides = evidence_overrides or {}
    work_items = [_apply_evidence_override(_evidence_form(candidate), overrides) for candidate in candidates]
    return {
        "schema_version": "0.1.0",
        "title": "CPOSS pair evidence workpack",
        "status": "awaiting_curator_input",
        "work_item_count": len(work_items),
        "work_items": work_items,
        "completion_criteria": [
            "Every promoted pair has a primary stability citation DOI or durable URL.",
            "Every promoted pair records stability ordering and measurement conditions.",
            "Every promoted pair records source redistribution license decisions for both structures.",
            "Every promoted pair records explicit disorder annotations for both structures.",
            "No pair with unresolved ambiguity is used for headline ranking or calibration metrics.",
        ],
    }


def _apply_evidence_override(item: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    family_defaults = overrides.get("family_defaults", {})
    by_candidate = overrides.get("candidate_overrides", {})
    family_override = family_defaults.get(item["family"], {})
    candidate_override = by_candidate.get(item["candidate_id"], {})
    override = _merge_evidence_override(family_override, candidate_override)
    if not override:
        return item
    updated = dict(item)
    updated["evidence_form"] = {**item["evidence_form"], **override.get("evidence_form", {})}
    if override.get("review_notes"):
        updated["review_notes"] = list(override["review_notes"])
    if override.get("source_review"):
        updated["source_review"] = dict(override["source_review"])
    return updated


def _merge_evidence_override(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    if base.get("evidence_form") or override.get("evidence_form"):
        merged["evidence_form"] = {**base.get("evidence_form", {}), **override.get("evidence_form", {})}
    if base.get("review_notes") or override.get("review_notes"):
        merged["review_notes"] = [*base.get("review_notes", []), *override.get("review_notes", [])]
    if base.get("source_review") or override.get("source_review"):
        merged["source_review"] = {**base.get("source_review", {}), **override.get("source_review", {})}
    return merged


def cposs_evidence_workpack_markdown(workpack: dict[str, Any]) -> str:
    """Render curator evidence forms as Markdown."""

    lines = [
        f"# {workpack['title']}",
        "",
        f"- Status: `{workpack['status']}`",
        f"- Work items: `{workpack['work_item_count']}`",
        "",
        "## Completion Criteria",
        "",
    ]
    lines.extend(f"- {criterion}" for criterion in workpack["completion_criteria"])
    for item in workpack["work_items"]:
        lines.extend(
            [
                "",
                f"## {item['candidate_id']}",
                "",
                f"- Priority: `{item['priority']}`",
                f"- Family: `{item['family']}`",
                f"- Model lower-energy structure: `{item['model_lower_energy_structure']}`",
                f"- Local model gap: `{float(item['model_gap_kj_mol_per_formula_unit']):.3f}` kJ/mol/f.u.",
                f"- Diagnostic flags: `{', '.join(item['diagnostic_flags']) or 'none'}`",
                "",
                "### Candidate Structures",
                "",
                f"- A: `{item['structure_a']['block_id']}`",
                f"- B: `{item['structure_b']['block_id']}`",
                "",
                "### Evidence Form",
                "",
                "| Field | Value |",
                "|---|---|",
            ]
        )
        for field, value in item["evidence_form"].items():
            lines.append(f"| {field} | {value or ''} |")
        if item.get("review_notes"):
            lines.extend(["", "### Review Notes", ""])
            lines.extend(f"- {note}" for note in item["review_notes"])
    return "\n".join(lines).rstrip() + "\n"


def cposs_candidate_cards(triage_report: dict[str, Any], *, max_candidates: int | None = None) -> dict[str, Any]:
    """Create AGI-reviewable candidate cards without benchmark promotion."""

    candidates = triage_report.get("top_candidates", [])
    if max_candidates is not None:
        candidates = candidates[:max_candidates]
    cards = [_candidate_card(candidate) for candidate in candidates]
    return {
        "schema_version": "0.1.0",
        "title": "CPOSS AGI-assisted candidate cards",
        "status": "claim_safe_candidate_cards",
        "card_count": len(cards),
        "cards": cards,
        "guardrails": [
            "Cards are designed for AGI-assisted review and planning, not benchmark promotion.",
            "Every card keeps the evidence tier below verified benchmark status until stability evidence is attached.",
            "Use cards to choose the next backend measurements, literature searches, and release-boundary checks.",
        ],
    }


def cposs_candidate_cards_markdown(report: dict[str, Any]) -> str:
    """Render CPOSS AGI-assisted candidate cards as Markdown."""

    lines = [
        f"# {report['title']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Cards: `{report['card_count']}`",
        "",
        "## Guardrails",
        "",
    ]
    lines.extend(f"- {guardrail}" for guardrail in report["guardrails"])
    for card in report["cards"]:
        tier = card["evidence_tier"]
        lines.extend(
            [
                "",
                f"## {card['candidate_id']}",
                "",
                f"- Family: `{card['family']}`",
                f"- Priority: `{card['priority']}`",
                f"- Evidence tier: `{tier['tier']}` (`{tier['status']}`)",
                f"- Local model gap: `{float(card['model_gap_kj_mol_per_formula_unit']):.3f}` kJ/mol/f.u.",
                f"- Model lower-energy structure: `{card['model_lower_energy_structure']}`",
                f"- Diagnostic flags: `{', '.join(card['diagnostic_flags']) or 'none'}`",
                "",
                "### Claim Boundary",
                "",
            ]
        )
        lines.extend(f"- Blocked: {claim}" for claim in tier["blocked_claims"])
        lines.extend(["", "### Next Actions", ""])
        lines.extend(f"- {action}" for action in card["next_actions"])
        lines.extend(["", "### Backend Commands", ""])
        lines.extend(f"- `{command}`" for command in card["backend_commands"])
    return "\n".join(lines).rstrip() + "\n"


def _structure_stub(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "block_id": row["block_id"],
        "formula": row.get("formula"),
        "formula_unit_count": row.get("formula_unit_count"),
        "relative_kj_mol_per_formula_unit": row.get("relative_kj_mol_per_formula_unit"),
        "local_diagnostic_flags": row.get("local_diagnostic_flags", []),
    }


def _triage_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    gap = float(candidate["model_gap_kj_mol_per_formula_unit"])
    score = 0
    reasons: list[str] = []
    if candidate.get("rank_index") == 1:
        score += 2
        reasons.append("first adjacent gap in family")
    if gap <= 2.0:
        score += 3
        reasons.append("small local model gap <= 2 kJ/mol/f.u.")
    elif gap <= 3.0:
        score += 2
        reasons.append("small local model gap <= 3 kJ/mol/f.u.")
    elif gap <= 5.0:
        score += 1
        reasons.append("moderate local model gap <= 5 kJ/mol/f.u.")
    if candidate.get("diagnostic_flags"):
        reasons.append("requires diagnostic flag review")
    priority = "high" if score >= 4 else "medium" if score >= 2 else "low"
    return {
        "candidate_id": candidate["candidate_id"],
        "family": candidate["family"],
        "priority": priority,
        "priority_score": score,
        "rank_index": candidate.get("rank_index"),
        "model_gap_kj_mol_per_formula_unit": gap,
        "model_lower_energy_structure": candidate.get("model_lower_energy_structure"),
        "structure_a": candidate.get("structure_a", {}),
        "structure_b": candidate.get("structure_b", {}),
        "diagnostic_flags": candidate.get("diagnostic_flags", []),
        "triage_reasons": reasons or ["wide local model gap"],
        "evidence_tasks": [
            "Find primary experimental stability citation.",
            "Record stability ordering and measurement conditions.",
            "Verify source redistribution license.",
            "Annotate disorder for both structures.",
        ],
    }


def _priority_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"high": 0, "medium": 0, "low": 0}
    for row in rows:
        counts[row["priority"]] += 1
    return counts


def _evidence_form(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": candidate["candidate_id"],
        "family": candidate["family"],
        "priority": candidate["priority"],
        "model_gap_kj_mol_per_formula_unit": candidate["model_gap_kj_mol_per_formula_unit"],
        "model_lower_energy_structure": candidate["model_lower_energy_structure"],
        "diagnostic_flags": candidate.get("diagnostic_flags", []),
        "triage_reasons": candidate.get("triage_reasons", []),
        "structure_a": {
            "block_id": candidate.get("structure_a", {}).get("block_id") or _side_from_candidate(candidate["candidate_id"], side="a"),
            "role": "candidate_structure_a",
        },
        "structure_b": {
            "block_id": candidate.get("structure_b", {}).get("block_id") or _side_from_candidate(candidate["candidate_id"], side="b"),
            "role": "candidate_structure_b",
        },
        "evidence_form": {
            "experimental_stability_ordering": "",
            "temperature_K": "",
            "relative_humidity": "",
            "free_energy_diff_kJ_per_mol": "",
            "citation_doi": "",
            "citation_url": "",
            "source_license_a": "",
            "source_license_b": "",
            "has_disorder_a": "",
            "has_disorder_b": "",
            "disorder_notes": "",
            "curator": "",
            "reviewer": "",
            "promotion_decision": "pending",
            "notes": "",
        },
    }


def _side_from_candidate(candidate_id: str, *, side: str) -> str:
    pair = candidate_id.split("_vs_")
    if len(pair) != 2:
        return ""
    token = pair[0] if side == "a" else pair[1]
    if side == "a":
        parts = token.split("_", 1)
        return parts[1].upper() if len(parts) == 2 else token.upper()
    return token.upper()


def _candidate_card(candidate: dict[str, Any]) -> dict[str, Any]:
    tier = classify_evidence_tier(
        {
            "target": candidate["candidate_id"],
            "has_atom_coordinates": True,
            "backend_count": 1,
            "has_sensitivity_grid": False,
            "has_therapeutic_contrast": False,
            "has_source_provenance": True,
            "license_clean_for_redistribution": True,
            "human_database_validation": False,
            "experimental_stability_evidence": False,
        }
    )
    next_actions = [
        "Run AIMNet2 and UMA single-point checks before using the candidate for backend-disagreement analysis.",
        "Search for experimental stability evidence and record the citation in the evidence workpack.",
        "Inspect diagnostic flags before using the local model gap for any qualitative narrative.",
        "Keep the card below verified benchmark status until the evidence tier changes.",
    ]
    if candidate.get("diagnostic_flags"):
        next_actions.insert(0, "Prioritize local geometry review because diagnostic flags are present.")
    return {
        "candidate_id": candidate["candidate_id"],
        "family": candidate["family"],
        "priority": candidate["priority"],
        "priority_score": candidate["priority_score"],
        "rank_index": candidate.get("rank_index"),
        "model_gap_kj_mol_per_formula_unit": candidate["model_gap_kj_mol_per_formula_unit"],
        "model_lower_energy_structure": candidate.get("model_lower_energy_structure"),
        "structure_a": candidate.get("structure_a", {}),
        "structure_b": candidate.get("structure_b", {}),
        "diagnostic_flags": candidate.get("diagnostic_flags", []),
        "triage_reasons": candidate.get("triage_reasons", []),
        "evidence_tier": tier.as_dict(),
        "next_actions": next_actions,
        "backend_commands": _backend_commands(candidate),
    }


def _backend_commands(candidate: dict[str, Any]) -> list[str]:
    block_ids = [
        candidate.get("structure_a", {}).get("block_id"),
        candidate.get("structure_b", {}).get("block_id"),
    ]
    powershell_block_args = " ".join(f"--block-id {block_id}" for block_id in block_ids if block_id)
    docker_block_args = powershell_block_args
    stem = candidate["candidate_id"]
    return [
        f"python scripts\\run_cposs_structure_inference.py --backend mace {powershell_block_args} --output outputs\\cposs_candidates_{stem}_mace.jsonl",
        f"docker compose run --rm crystalprobe-core python scripts/run_cposs_structure_inference.py --backend aimnet2 {docker_block_args} --output outputs/cposs_candidates_{stem}_aimnet2.jsonl --continue-on-error",
        f"docker compose run --rm crystalprobe-fairchem python scripts/run_cposs_structure_inference.py --backend uma {docker_block_args} --output outputs/cposs_candidates_{stem}_uma.jsonl --continue-on-error",
    ]
