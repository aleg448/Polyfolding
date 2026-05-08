"""Block-to-form mapping readiness for CPOSS benchmark promotion."""

from __future__ import annotations

from typing import Any


LOCKED_STATUS = "block_form_mapping_locked"
PROMOTION_CONFIDENCE = "high"


def seed_cposs_block_form_mapping_manifest(
    evidence_workpack: dict[str, Any],
    *,
    mapping_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Seed missing CPOSS block mapping rows while preserving existing curation."""

    manifest = dict(mapping_manifest or {})
    manifest.setdefault("schema_version", "0.1.0")
    manifest.setdefault("status", "block_form_mapping_scaffold")
    manifest.setdefault(
        "scope",
        "Local CPOSS block-to-experimental-form mapping manifest. This file records metadata needed for promotion and does not contain coordinate-bearing CIF content.",
    )
    manifest.pop("seeded_block_count", None)
    families = {family: dict(record) for family, record in manifest.get("families", {}).items()}
    for family, block_id in _unique_candidate_blocks(evidence_workpack):
        family_record = dict(families.get(family, {}))
        blocks = dict(family_record.get("blocks", {}))
        if block_id not in blocks:
            blocks[block_id] = _empty_block_mapping()
        family_record["blocks"] = blocks
        families[family] = family_record
    manifest["families"] = {family: families[family] for family in sorted(families)}
    manifest["total_block_count"] = sum(len(record.get("blocks", {})) for record in manifest["families"].values())
    return manifest


def cposs_block_mapping_report(
    evidence_workpack: dict[str, Any],
    *,
    mapping_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Summarize CPOSS block-to-experimental-form mapping readiness."""

    manifest = mapping_manifest or {}
    block_rows = [
        _block_row(family, block_id, manifest)
        for family, block_id in _unique_candidate_blocks(evidence_workpack)
    ]
    candidate_rows = [_candidate_row(item, block_rows) for item in evidence_workpack.get("work_items", [])]
    ready_blocks = [row for row in block_rows if row["promotion_ready"]]
    locked_blocks = [row for row in block_rows if row["mapping_status"] == LOCKED_STATUS]
    mapping_curation_queue = _mapping_curation_queue(candidate_rows)
    block_curation_queue = _block_curation_queue(block_rows, candidate_rows)
    return {
        "schema_version": "0.1.0",
        "status": "cposs_block_form_mapping_recorded",
        "block_count": len(block_rows),
        "locked_block_count": len(locked_blocks),
        "promotion_ready_block_count": len(ready_blocks),
        "candidate_count": len(candidate_rows),
        "candidate_mapping_ready_count": sum(1 for row in candidate_rows if row["mapping_ready"]),
        "family_summary": _family_summary(block_rows),
        "mapping_curation_queue": mapping_curation_queue,
        "block_curation_queue": block_curation_queue,
        "block_rows": block_rows,
        "candidate_rows": candidate_rows,
        "policy": [
            "Block-to-form mapping is required before literature-mapped CPOSS candidates can become verified benchmark pairs.",
            "A family-level literature citation is not enough; each CPOSS block ID must map to an experimental form label.",
            "Promotion-ready mappings require high confidence, explicit cell/space-group/formula/source-label checks, license resolution, and disorder annotation.",
            "This report records mapping metadata only and does not publish coordinate-bearing CIF content.",
        ],
    }


def cposs_block_mapping_markdown(report: dict[str, Any]) -> str:
    """Render CPOSS block-to-form mapping readiness as Markdown."""

    lines = [
        "# CPOSS Block-to-Form Mapping",
        "",
        f"- Status: `{report['status']}`",
        f"- Blocks: `{report['block_count']}`",
        f"- Locked blocks: `{report['locked_block_count']}`",
        f"- Promotion-ready blocks: `{report['promotion_ready_block_count']}`",
        f"- Candidate pairs: `{report['candidate_count']}`",
        f"- Mapping-ready candidate pairs: `{report['candidate_mapping_ready_count']}`",
        "",
        "## Family Summary",
        "",
        "| Family | Blocks | Locked | Promotion Ready | Unmapped |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in report["family_summary"]:
        lines.append(
            f"| `{row['family']}` | `{row['block_count']}` | `{row['locked_block_count']}` | "
            f"`{row['promotion_ready_block_count']}` | `{row['unmapped_count']}` |"
        )
    lines.extend(
        [
            "",
            "## Mapping Curation Queue",
            "",
            "| Priority | Candidate | Family | Gap | A | B | Blockers |",
            "|---|---|---|---:|---|---|---|",
        ]
    )
    for row in report.get("mapping_curation_queue", []):
        lines.append(
            f"| `{row['priority']}` | `{row['candidate_id']}` | `{row['family']}` | "
            f"{float(row['model_gap_kj_mol_per_formula_unit']):.3f} | `{row['structure_a']}` | "
            f"`{row['structure_b']}` | {'; '.join(row['blockers']) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Block Curation Queue",
            "",
            "| Priority | Family | Block | Candidate Uses | Best Gap | Top Candidate | Blockers |",
            "|---|---|---|---:|---:|---|---|",
        ]
    )
    for row in report.get("block_curation_queue", []):
        lines.append(
            f"| `{row['priority']}` | `{row['family']}` | `{row['block_id']}` | "
            f"`{row['candidate_count']}` | {float(row['best_model_gap_kj_mol_per_formula_unit']):.3f} | "
            f"`{row['top_candidate_id']}` | {'; '.join(row['blockers']) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Block Mapping Queue",
            "",
            "| Family | Block | Status | Form Label | Confidence | Blockers |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in report["block_rows"]:
        lines.append(
            f"| `{row['family']}` | `{row['block_id']}` | `{row['mapping_status']}` | "
            f"{row['experimental_form_label'] or ''} | `{row['mapping_confidence']}` | "
            f"{'; '.join(row['blockers']) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Candidate Pair Gate",
            "",
            "| Candidate | A | B | Ready | Blockers |",
            "|---|---|---|---|---|",
        ]
    )
    for row in report["candidate_rows"]:
        lines.append(
            f"| `{row['candidate_id']}` | `{row['structure_a']}` | `{row['structure_b']}` | "
            f"`{row['mapping_ready']}` | {'; '.join(row['blockers']) or 'none'} |"
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def cposs_block_mapping_dossier(
    block_mapping_report: dict[str, Any],
    *,
    block_id: str | None = None,
) -> dict[str, Any]:
    """Build a focused dossier for one CPOSS block mapping target."""

    target = _dossier_target(block_mapping_report, block_id)
    candidate_uses = _dossier_candidate_uses(block_mapping_report, target)
    return {
        "schema_version": "0.1.0",
        "status": "cposs_block_mapping_dossier_recorded",
        "target": {
            "family": target.get("family"),
            "block_id": target.get("block_id"),
            "mapping_status": target.get("mapping_status"),
            "priority": target.get("priority", "unspecified"),
            "candidate_count": target.get("candidate_count", len(candidate_uses)),
            "top_candidate_id": target.get("top_candidate_id") or (candidate_uses[0]["candidate_id"] if candidate_uses else ""),
            "best_model_gap_kj_mol_per_formula_unit": target.get("best_model_gap_kj_mol_per_formula_unit", 0.0),
        },
        "block_record": _block_record(block_mapping_report, target),
        "candidate_uses": candidate_uses,
        "required_actions": _dossier_required_actions(target),
        "policy": [
            "This dossier is a curation checklist, not a verified benchmark record.",
            "Do not set promotion_decision to promote until this block and its paired block are both mapping-ready.",
            "The dossier records metadata and blockers only; it does not contain coordinate-bearing CIF content.",
        ],
    }


def cposs_block_mapping_dossier_markdown(dossier: dict[str, Any]) -> str:
    """Render a focused CPOSS block mapping dossier."""

    target = dossier["target"]
    block = dossier["block_record"]
    lines = [
        "# CPOSS Block Mapping Dossier",
        "",
        f"- Status: `{dossier['status']}`",
        f"- Family: `{target['family']}`",
        f"- Block: `{target['block_id']}`",
        f"- Mapping status: `{target['mapping_status']}`",
        f"- Priority: `{target['priority']}`",
        f"- Candidate uses: `{target['candidate_count']}`",
        f"- Top candidate: `{target['top_candidate_id']}`",
        f"- Best local gap: `{float(target['best_model_gap_kj_mol_per_formula_unit']):.3f}` kJ/mol/f.u.",
        "",
        "## Current Block Record",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| experimental_form_label | {block.get('experimental_form_label') or ''} |",
        f"| mapping_confidence | {block.get('mapping_confidence') or ''} |",
        f"| family_source_doi | {block.get('family_source_doi') or ''} |",
        f"| family_source_url | {block.get('family_source_url') or ''} |",
        f"| citation_doi | {block.get('citation_doi') or ''} |",
        f"| citation_url | {block.get('citation_url') or ''} |",
        f"| license_decision | {block.get('license_decision') or ''} |",
        f"| disorder_annotation | {block.get('disorder_annotation') or ''} |",
        f"| curator | {block.get('curator') or ''} |",
        f"| reviewer | {block.get('reviewer') or ''} |",
        "",
        "## Candidate Uses",
        "",
        "| Candidate | Priority | Gap | A | B | Ready | Blockers |",
        "|---|---|---:|---|---|---|---|",
    ]
    if block.get("family_literature_context"):
        lines[lines.index("## Candidate Uses"):lines.index("## Candidate Uses")] = [
            "",
            "## Family Literature Context",
            "",
            str(block["family_literature_context"]),
        ]
    for row in dossier["candidate_uses"]:
        lines.append(
            f"| `{row['candidate_id']}` | `{row['priority']}` | "
            f"{float(row['model_gap_kj_mol_per_formula_unit']):.3f} | `{row['structure_a']}` | "
            f"`{row['structure_b']}` | `{row['mapping_ready']}` | {'; '.join(row['blockers']) or 'none'} |"
        )
    lines.extend(["", "## Required Actions", ""])
    lines.extend(f"- {item}" for item in dossier["required_actions"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in dossier["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _dossier_target(block_mapping_report: dict[str, Any], block_id: str | None) -> dict[str, Any]:
    if block_id:
        for row in block_mapping_report.get("block_curation_queue", []):
            if row.get("block_id") == block_id:
                return dict(row)
        for row in block_mapping_report.get("block_rows", []):
            if row.get("block_id") == block_id:
                return dict(row)
        raise ValueError(f"Unknown CPOSS block_id: {block_id}")
    queue = block_mapping_report.get("block_curation_queue", [])
    if queue:
        return dict(queue[0])
    rows = block_mapping_report.get("block_rows", [])
    if rows:
        return dict(rows[0])
    raise ValueError("Block mapping report does not contain block rows")


def _block_record(block_mapping_report: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    for row in block_mapping_report.get("block_rows", []):
        if row.get("family") == target.get("family") and row.get("block_id") == target.get("block_id"):
            return dict(row)
    return dict(target)


def _dossier_candidate_uses(block_mapping_report: dict[str, Any], target: dict[str, Any]) -> list[dict[str, Any]]:
    block_id = target.get("block_id")
    family = target.get("family")
    rows = [
        dict(row)
        for row in block_mapping_report.get("candidate_rows", [])
        if row.get("family") == family and block_id in {row.get("structure_a"), row.get("structure_b")}
    ]
    return _mapping_curation_queue(rows)


def _dossier_required_actions(target: dict[str, Any]) -> list[str]:
    blockers = list(target.get("blockers", []))
    if not blockers:
        return ["No block-level blockers remain; verify the paired block before promotion."]
    return [
        "Fill the block row in data/curation/cposs_block_form_mapping_v0.1.json.",
        *blockers,
        "Regenerate the block mapping, promotion, publication-readiness, and roadmap reports.",
    ]


def _unique_candidate_blocks(evidence_workpack: dict[str, Any]) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    for item in evidence_workpack.get("work_items", []):
        family = str(item.get("family") or "")
        for key in ("structure_a", "structure_b"):
            block_id = str(item.get(key, {}).get("block_id") or "")
            if family and block_id:
                seen.add((family, block_id))
    return sorted(seen, key=lambda row: (row[0], row[1]))


def _empty_block_mapping() -> dict[str, Any]:
    return {
        "mapping_status": "unmapped",
        "experimental_form_label": "",
        "mapping_confidence": "unknown",
        "citation_doi": "",
        "citation_url": "",
        "matching_evidence": {
            "cell_match": None,
            "space_group_match": None,
            "formula_match": None,
            "source_label_match": None,
        },
        "license_decision": "",
        "disorder_annotation": "unknown",
        "curator": "",
        "reviewer": "",
        "mapping_notes": "",
    }


def _block_row(family: str, block_id: str, manifest: dict[str, Any]) -> dict[str, Any]:
    family_record = dict(manifest.get("families", {}).get(family, {}))
    mapping = _mapping_for_block(family, block_id, manifest)
    matching = dict(mapping.get("matching_evidence", {}))
    license_decision = str(mapping.get("license_decision") or "")
    disorder = str(mapping.get("disorder_annotation") or "")
    blockers = _blockers(mapping, matching, license_decision, disorder)
    return {
        "family": family,
        "block_id": block_id,
        "family_source_doi": family_record.get("family_source_doi") or "",
        "family_source_url": family_record.get("family_source_url") or "",
        "family_literature_context": family_record.get("family_literature_context") or "",
        "mapping_status": mapping.get("mapping_status") or "unmapped",
        "experimental_form_label": mapping.get("experimental_form_label") or "",
        "mapping_confidence": mapping.get("mapping_confidence") or "unknown",
        "citation_doi": mapping.get("citation_doi") or "",
        "citation_url": mapping.get("citation_url") or "",
        "matching_evidence": matching,
        "license_decision": license_decision,
        "disorder_annotation": disorder or "unknown",
        "curator": mapping.get("curator") or "",
        "reviewer": mapping.get("reviewer") or "",
        "blockers": blockers,
        "promotion_ready": not blockers,
    }


def _mapping_for_block(family: str, block_id: str, manifest: dict[str, Any]) -> dict[str, Any]:
    family_record = manifest.get("families", {}).get(family, {})
    return dict(family_record.get("blocks", {}).get(block_id, {}))


def _blockers(
    mapping: dict[str, Any],
    matching: dict[str, Any],
    license_decision: str,
    disorder: str,
) -> list[str]:
    blockers = []
    if mapping.get("mapping_status") != LOCKED_STATUS:
        blockers.append("mapping_status must be block_form_mapping_locked")
    if not mapping.get("experimental_form_label"):
        blockers.append("experimental_form_label is required")
    if mapping.get("mapping_confidence") != PROMOTION_CONFIDENCE:
        blockers.append("mapping_confidence must be high")
    if not (mapping.get("citation_doi") or mapping.get("citation_url")):
        blockers.append("block-level citation_doi or citation_url is required")
    for field in ("cell_match", "space_group_match", "formula_match", "source_label_match"):
        if matching.get(field) is not True:
            blockers.append(f"matching_evidence.{field} must be true")
    if not license_decision or "requires review" in license_decision.casefold():
        blockers.append("license_decision must be resolved")
    if disorder.strip().casefold() not in {"true", "false"}:
        blockers.append("disorder_annotation must be true or false")
    if not mapping.get("curator"):
        blockers.append("curator is required")
    if not mapping.get("reviewer"):
        blockers.append("reviewer is required")
    return blockers


def _candidate_row(item: dict[str, Any], block_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_key = {(row["family"], row["block_id"]): row for row in block_rows}
    family = str(item.get("family") or "")
    structure_a = str(item.get("structure_a", {}).get("block_id") or "")
    structure_b = str(item.get("structure_b", {}).get("block_id") or "")
    blockers = []
    for label, block_id in (("A", structure_a), ("B", structure_b)):
        row = by_key.get((family, block_id))
        if row is None:
            blockers.append(f"{label} block mapping row is missing")
        elif not row["promotion_ready"]:
            blockers.append(f"{label} {block_id}: {len(row['blockers'])} mapping blockers")
    return {
        "candidate_id": item.get("candidate_id"),
        "family": family,
        "priority": item.get("priority", "unspecified"),
        "model_gap_kj_mol_per_formula_unit": float(item.get("model_gap_kj_mol_per_formula_unit") or 0.0),
        "model_lower_energy_structure": item.get("model_lower_energy_structure") or "",
        "structure_a": structure_a,
        "structure_b": structure_b,
        "mapping_ready": not blockers,
        "blockers": blockers,
    }


def _mapping_curation_queue(candidate_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority_rank = {"high": 0, "medium": 1, "low": 2, "unspecified": 3}
    queue = [row for row in candidate_rows if not row["mapping_ready"]]
    return sorted(
        queue,
        key=lambda row: (
            priority_rank.get(str(row.get("priority")), priority_rank["unspecified"]),
            float(row.get("model_gap_kj_mol_per_formula_unit", 0.0)),
            str(row.get("candidate_id")),
        ),
    )


def _block_curation_queue(
    block_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    priority_rank = {"high": 0, "medium": 1, "low": 2, "unspecified": 3}
    queue = []
    for block in block_rows:
        if block["promotion_ready"]:
            continue
        uses = [
            candidate
            for candidate in candidate_rows
            if candidate["family"] == block["family"]
            and block["block_id"] in {candidate["structure_a"], candidate["structure_b"]}
        ]
        priority = _best_priority(uses)
        top_candidate = _top_candidate(uses)
        queue.append(
            {
                "family": block["family"],
                "block_id": block["block_id"],
                "mapping_status": block["mapping_status"],
                "priority": priority,
                "candidate_count": len(uses),
                "best_model_gap_kj_mol_per_formula_unit": float(
                    top_candidate.get("model_gap_kj_mol_per_formula_unit", 0.0)
                )
                if top_candidate
                else 0.0,
                "top_candidate_id": top_candidate.get("candidate_id", "") if top_candidate else "",
                "blockers": block["blockers"],
            }
        )
    return sorted(
        queue,
        key=lambda row: (
            priority_rank.get(str(row["priority"]), priority_rank["unspecified"]),
            -int(row["candidate_count"]),
            float(row["best_model_gap_kj_mol_per_formula_unit"]),
            str(row["block_id"]),
        ),
    )


def _best_priority(candidate_rows: list[dict[str, Any]]) -> str:
    priority_rank = {"high": 0, "medium": 1, "low": 2, "unspecified": 3}
    if not candidate_rows:
        return "unspecified"
    return min(
        (str(row.get("priority", "unspecified")) for row in candidate_rows),
        key=lambda priority: priority_rank.get(priority, priority_rank["unspecified"]),
    )


def _top_candidate(candidate_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    priority_rank = {"high": 0, "medium": 1, "low": 2, "unspecified": 3}
    if not candidate_rows:
        return None
    return sorted(
        candidate_rows,
        key=lambda row: (
            priority_rank.get(str(row.get("priority", "unspecified")), priority_rank["unspecified"]),
            float(row.get("model_gap_kj_mol_per_formula_unit", 0.0)),
            str(row.get("candidate_id")),
        ),
    )[0]


def _family_summary(block_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    families = sorted({row["family"] for row in block_rows})
    summary = []
    for family in families:
        rows = [row for row in block_rows if row["family"] == family]
        summary.append(
            {
                "family": family,
                "block_count": len(rows),
                "locked_block_count": sum(1 for row in rows if row["mapping_status"] == LOCKED_STATUS),
                "promotion_ready_block_count": sum(1 for row in rows if row["promotion_ready"]),
                "unmapped_count": sum(1 for row in rows if row["mapping_status"] == "unmapped"),
            }
        )
    return summary
