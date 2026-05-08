"""Promotion gates from CPOSS evidence workpacks to benchmark records."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from crystalprobe.benchmark.schema import PolymorphPair


REQUIRED_EVIDENCE_FIELDS = [
    "experimental_stability_ordering",
    "citation_doi",
    "source_license_a",
    "source_license_b",
    "has_disorder_a",
    "has_disorder_b",
    "curator",
    "reviewer",
    "promotion_decision",
]


def cposs_promotion_report(
    evidence_workpack: dict[str, Any],
    *,
    family_annotations: dict[str, Any] | None = None,
    block_mapping_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate completed CPOSS evidence forms before benchmark promotion."""

    annotations = family_annotations or {}
    block_mapping_rows = _candidate_block_mapping_rows(block_mapping_report)
    rows = [
        _promotion_row(
            item,
            annotations.get(str(item.get("family")), {}),
            None if block_mapping_rows is None else block_mapping_rows.get(str(item.get("candidate_id"))),
            enforce_block_mapping=block_mapping_rows is not None,
        )
        for item in evidence_workpack.get("work_items", [])
    ]
    promoted = [row["record"] for row in rows if row["promotion_status"] == "promoted"]
    literature_mapped = [row for row in rows if row["promotion_status"] == "literature_mapped_candidate"]
    blocked = [row for row in rows if row["promotion_status"] == "blocked"]
    milestones = _milestones(len(promoted))
    field_completion = _field_completion(evidence_workpack.get("work_items", []))
    curation_queue = _curation_queue(rows)
    family_summary = _family_summary(rows)
    return {
        "schema_version": "0.1.0",
        "status": "cposs_promotion_gate_recorded",
        "candidate_count": len(rows),
        "promoted_count": len(promoted),
        "literature_mapped_count": len(literature_mapped),
        "blocked_count": len(blocked),
        "not_promoted_count": len(rows) - len(promoted),
        "block_mapping_enforced": block_mapping_rows is not None,
        "milestones": milestones,
        "family_summary": family_summary,
        "field_completion": field_completion,
        "curation_queue": curation_queue,
        "upgrade_requirements": _upgrade_requirements(rows),
        "rows": rows,
        "promoted_records": promoted,
        "policy": [
            "No CPOSS candidate becomes a benchmark record without experimental stability evidence.",
            "Literature-mapped candidates are evidence-populated prebenchmark records, not verified benchmark pairs.",
            "When a block-to-form mapping report is supplied, promotion requires mapping-ready candidate pairs.",
            "Verified records require source license decisions and explicit disorder annotations.",
            "Ambiguous or incomplete records remain excluded from headline fingerprint and calibration metrics.",
        ],
    }


def cposs_promotion_markdown(report: dict[str, Any]) -> str:
    """Render CPOSS promotion gate status as Markdown."""

    lines = [
        "# CPOSS Benchmark Promotion Gate",
        "",
        f"- Status: `{report['status']}`",
        f"- Candidates: `{report['candidate_count']}`",
        f"- Promoted: `{report['promoted_count']}`",
        f"- Literature mapped: `{report.get('literature_mapped_count', 0)}`",
        f"- Blocked: `{report['blocked_count']}`",
        f"- Block mapping enforced: `{report.get('block_mapping_enforced', False)}`",
        "",
        "## Milestones",
        "",
    ]
    lines.extend(
        f"- `{row['pair_count']}` verified pairs: `{row['status']}`; remaining `{row['remaining']}`"
        for row in report.get("milestones", [])
    )
    lines.extend(
        [
            "",
            "## Family Summary",
            "",
            "| Family | Candidates | Promoted | Literature Mapped | Blocked | High Priority Not Promoted |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("family_summary", []):
        lines.append(
            f"| `{row['family']}` | `{row['candidate_count']}` | `{row['promoted_count']}` | "
            f"`{row.get('literature_mapped_count', 0)}` | `{row['blocked_count']}` | "
            f"`{row['high_priority_not_promoted_count']}` |"
        )
    lines.extend(
        [
            "",
            "## Evidence Field Completion",
            "",
            "| Field | Complete | Missing |",
            "|---|---:|---:|",
        ]
    )
    for row in report.get("field_completion", []):
        lines.append(f"| `{row['field']}` | `{row['complete_count']}` | `{row['missing_count']}` |")
    lines.extend(
        [
            "",
            "## Curation Queue",
            "",
            "| Candidate | Family | Priority | Missing | Next fields |",
            "|---|---|---|---:|---|",
        ]
    )
    for row in report.get("curation_queue", []):
        lines.append(
            f"| `{row['candidate_id']}` | `{row['family']}` | `{row['priority']}` | "
            f"`{row['missing_count']}` | {', '.join(f'`{field}`' for field in row['next_required_fields'])} |"
        )
    lines.extend(
        [
            "",
            "## Candidates",
            "",
            "| Candidate | Status | Missing/Errors |",
            "|---|---|---|",
        ]
    )
    for row in report["rows"]:
        reasons = row.get("blockers") or row.get("validation_errors") or []
        lines.append(f"| `{row['candidate_id']}` | `{row['promotion_status']}` | {'; '.join(reasons) or 'none'} |")
    if report.get("upgrade_requirements"):
        lines.extend(
            [
                "",
                "## Upgrade Requirements",
                "",
                "| Candidate | Status | Requirements |",
                "|---|---|---|",
            ]
        )
        for row in report["upgrade_requirements"]:
            lines.append(
                f"| `{row['candidate_id']}` | `{row['promotion_status']}` | "
                f"{'; '.join(row['requirements']) or 'none'} |"
            )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _promotion_row(
    item: dict[str, Any],
    annotation: dict[str, Any],
    block_mapping_row: dict[str, Any] | None,
    *,
    enforce_block_mapping: bool,
) -> dict[str, Any]:
    candidate_id = str(item.get("candidate_id"))
    form = dict(item.get("evidence_form", {}))
    blockers = _missing_fields(form)
    if not annotation:
        blockers.append("family chemistry annotation is missing")
    if blockers:
        return {
            "candidate_id": candidate_id,
            "family": item.get("family"),
            "priority": item.get("priority", "unspecified"),
            "promotion_status": "blocked",
            "next_required_fields": _next_required_fields(form),
            "blockers": blockers,
            "upgrade_requirements": _upgrade_requirements_for_form(form),
        }
    if form.get("promotion_decision") != "promote":
        return {
            "candidate_id": candidate_id,
            "family": item.get("family"),
            "priority": item.get("priority", "unspecified"),
            "promotion_status": "literature_mapped_candidate",
            "next_required_fields": [],
            "upgrade_requirements": _upgrade_requirements_for_form(form),
        }
    mapping_blockers = _block_mapping_blockers(block_mapping_row, enforce_block_mapping)
    if mapping_blockers:
        return {
            "candidate_id": candidate_id,
            "family": item.get("family"),
            "priority": item.get("priority", "unspecified"),
            "promotion_status": "blocked",
            "next_required_fields": [],
            "blockers": mapping_blockers,
            "upgrade_requirements": [
                *_upgrade_requirements_for_form(form),
                "Lock block-to-experimental-form mapping for both candidate structures.",
            ],
        }
    record = _record(item, form, annotation)
    try:
        validated = PolymorphPair.model_validate(record)
    except ValidationError as exc:
        return {
            "candidate_id": candidate_id,
            "family": item.get("family"),
            "priority": item.get("priority", "unspecified"),
            "promotion_status": "blocked",
            "next_required_fields": [],
            "validation_errors": [error["msg"] for error in exc.errors()],
            "upgrade_requirements": ["Fix schema validation errors before promotion."],
        }
    return {
        "candidate_id": candidate_id,
        "family": item.get("family"),
        "priority": item.get("priority", "unspecified"),
        "promotion_status": "promoted",
        "next_required_fields": [],
        "upgrade_requirements": [],
        "record": validated.model_dump(mode="json"),
    }


def _missing_fields(form: dict[str, Any]) -> list[str]:
    missing = []
    for field in REQUIRED_EVIDENCE_FIELDS:
        value = form.get(field)
        if value in {None, ""}:
            missing.append(f"{field} is required")
    if not form.get("citation_doi") and not form.get("citation_url"):
        missing.append("citation_doi or citation_url is required")
    return missing


def _candidate_block_mapping_rows(block_mapping_report: dict[str, Any] | None) -> dict[str, dict[str, Any]] | None:
    if block_mapping_report is None:
        return None
    return {
        str(row.get("candidate_id")): dict(row)
        for row in block_mapping_report.get("candidate_rows", [])
        if row.get("candidate_id")
    }


def _block_mapping_blockers(block_mapping_row: dict[str, Any] | None, enforce_block_mapping: bool) -> list[str]:
    if not enforce_block_mapping:
        return []
    if block_mapping_row is None:
        return ["block-to-form mapping row is missing"]
    if block_mapping_row.get("mapping_ready") is True:
        return []
    blockers = list(block_mapping_row.get("blockers", []))
    return blockers or ["block-to-form mapping is not locked for both structures"]


def _field_completion(work_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fields = [*REQUIRED_EVIDENCE_FIELDS, "citation_doi_or_url"]
    rows = []
    total = len(work_items)
    for field in fields:
        complete = sum(1 for item in work_items if _field_has_value(item.get("evidence_form", {}), field))
        rows.append(
            {
                "field": field,
                "complete_count": complete,
                "missing_count": total - complete,
            }
        )
    return rows


def _field_has_value(form: dict[str, Any], field: str) -> bool:
    if field == "citation_doi_or_url":
        return bool(form.get("citation_doi") or form.get("citation_url"))
    return form.get(field) not in {None, ""}


def _next_required_fields(form: dict[str, Any]) -> list[str]:
    fields = [
        "experimental_stability_ordering",
        "citation_doi_or_url",
        "source_license_a",
        "source_license_b",
        "has_disorder_a",
        "has_disorder_b",
        "curator",
        "reviewer",
        "promotion_decision",
    ]
    return [field for field in fields if not _field_has_value(form, field)]


def _curation_queue(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority_rank = {"high": 0, "medium": 1, "low": 2, "unspecified": 3}
    queue = [
        {
            "candidate_id": row["candidate_id"],
            "family": row.get("family"),
            "priority": row.get("priority", "unspecified"),
            "missing_count": len(row.get("next_required_fields", [])),
            "next_required_fields": row.get("next_required_fields", []),
            "promotion_status": row.get("promotion_status"),
            "upgrade_requirements": row.get("upgrade_requirements", []),
        }
        for row in rows
        if row.get("promotion_status") != "promoted"
    ]
    return sorted(
        queue,
        key=lambda row: (
            priority_rank.get(str(row["priority"]), priority_rank["unspecified"]),
            row["missing_count"],
            str(row["candidate_id"]),
        ),
    )


def _family_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    families = sorted({str(row.get("family")) for row in rows})
    summary = []
    for family in families:
        family_rows = [row for row in rows if str(row.get("family")) == family]
        promoted_count = sum(1 for row in family_rows if row.get("promotion_status") == "promoted")
        literature_mapped_count = sum(1 for row in family_rows if row.get("promotion_status") == "literature_mapped_candidate")
        blocked_rows = [row for row in family_rows if row.get("promotion_status") == "blocked"]
        not_promoted_rows = [row for row in family_rows if row.get("promotion_status") != "promoted"]
        summary.append(
            {
                "family": family,
                "candidate_count": len(family_rows),
                "promoted_count": promoted_count,
                "literature_mapped_count": literature_mapped_count,
                "blocked_count": len(blocked_rows),
                "high_priority_blocked_count": sum(1 for row in blocked_rows if row.get("priority") == "high"),
                "high_priority_not_promoted_count": sum(
                    1 for row in not_promoted_rows if row.get("priority") == "high"
                ),
            }
        )
    return summary


def _upgrade_requirements(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": row["candidate_id"],
            "family": row.get("family"),
            "priority": row.get("priority", "unspecified"),
            "promotion_status": row.get("promotion_status"),
            "requirements": row.get("upgrade_requirements", []),
        }
        for row in rows
        if row.get("promotion_status") != "promoted"
    ]


def _upgrade_requirements_for_form(form: dict[str, Any]) -> list[str]:
    requirements = []
    if _next_required_fields(form):
        requirements.append("Complete all required evidence fields.")
    if form.get("experimental_stability_ordering") in {None, "", "ambiguous"}:
        requirements.append("Map CPOSS block IDs to experimental form labels and assign a non-ambiguous stability ordering.")
    if str(form.get("has_disorder_a", "")).strip().casefold() == "unknown" or str(
        form.get("has_disorder_b", "")
    ).strip().casefold() == "unknown":
        requirements.append("Replace unknown disorder annotations with explicit true/false values and notes.")
    if "requires review" in str(form.get("source_license_a", "")).casefold() or "requires review" in str(
        form.get("source_license_b", "")
    ).casefold():
        requirements.append("Resolve source-license review into benchmark-schema license values.")
    if form.get("promotion_decision") != "promote":
        requirements.append("Set promotion_decision to promote only after independent review confirms the mapping.")
    return requirements


def _milestones(promoted_count: int) -> list[dict[str, Any]]:
    return [
        {
            "pair_count": target,
            "status": "reached" if promoted_count >= target else "pending",
            "remaining": max(target - promoted_count, 0),
        }
        for target in (20, 50, 100)
    ]


def _record(item: dict[str, Any], form: dict[str, Any], annotation: dict[str, Any]) -> dict[str, Any]:
    structure_a = item.get("structure_a", {})
    structure_b = item.get("structure_b", {})
    license_a = form["source_license_a"]
    license_b = form["source_license_b"]
    return {
        "pair_id": str(item["candidate_id"]).replace("_psicrys", "_psicrys"),
        "molecule": {
            "smiles": annotation["smiles"],
            "inchi": annotation.get("inchi"),
            "common_name": annotation.get("common_name") or item.get("family"),
            "cas_number": annotation.get("cas_number"),
            "flexibility_class": annotation.get("flexibility_class", "unknown"),
            "h_bond_motifs": list(annotation.get("h_bond_motifs", [])),
            "functional_groups": list(annotation.get("functional_groups", [])),
            "has_halogen": bool(annotation.get("has_halogen", False)),
            "has_charge": bool(annotation.get("has_charge", False)),
            "is_chiral": bool(annotation.get("is_chiral", False)),
        },
        "structure_a": {
            "structure_id": structure_a["block_id"],
            "cif_path": f"cposs209/{structure_a['block_id']}.cif",
            "label": structure_a["block_id"],
            "source": "CPOSS209",
            "source_id": structure_a["block_id"],
            "license": license_a,
        },
        "structure_b": {
            "structure_id": structure_b["block_id"],
            "cif_path": f"cposs209/{structure_b['block_id']}.cif",
            "label": structure_b["block_id"],
            "source": "CPOSS209",
            "source_id": structure_b["block_id"],
            "license": license_b,
        },
        "evidence": {
            "stability_ordering": form["experimental_stability_ordering"],
            "temperature_K": _optional_float(form.get("temperature_K")),
            "relative_humidity": _optional_float(form.get("relative_humidity")),
            "free_energy_diff_kJ_per_mol": _optional_float(form.get("free_energy_diff_kJ_per_mol")),
            "citation_doi": form.get("citation_doi") or None,
            "citation_url": form.get("citation_url") or None,
            "notes": form.get("notes", ""),
        },
        "curation_status": "verified" if form.get("promotion_decision") == "promote" else "reviewed",
        "chemistry_tags": list(annotation.get("chemistry_tags", [])),
        "has_disorder": _bool_field(form.get("has_disorder_a")) or _bool_field(form.get("has_disorder_b")),
        "disorder_notes": form.get("disorder_notes", ""),
    }


def _optional_float(value: Any) -> float | None:
    if value in {None, ""}:
        return None
    return float(value)


def _bool_field(value: Any) -> bool:
    return str(value).strip().casefold() in {"true", "yes", "1"}
