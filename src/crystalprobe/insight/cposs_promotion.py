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
) -> dict[str, Any]:
    """Validate completed CPOSS evidence forms before benchmark promotion."""

    annotations = family_annotations or {}
    rows = [
        _promotion_row(item, annotations.get(str(item.get("family")), {}))
        for item in evidence_workpack.get("work_items", [])
    ]
    promoted = [row["record"] for row in rows if row["promotion_status"] == "promoted"]
    milestones = _milestones(len(promoted))
    field_completion = _field_completion(evidence_workpack.get("work_items", []))
    curation_queue = _curation_queue(rows)
    family_summary = _family_summary(rows)
    return {
        "schema_version": "0.1.0",
        "status": "cposs_promotion_gate_recorded",
        "candidate_count": len(rows),
        "promoted_count": len(promoted),
        "blocked_count": sum(1 for row in rows if row["promotion_status"] != "promoted"),
        "milestones": milestones,
        "family_summary": family_summary,
        "field_completion": field_completion,
        "curation_queue": curation_queue,
        "rows": rows,
        "promoted_records": promoted,
        "policy": [
            "No CPOSS candidate becomes a benchmark record without experimental stability evidence.",
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
        f"- Blocked: `{report['blocked_count']}`",
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
            "| Family | Candidates | Promoted | Blocked | High Priority Blocked |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("family_summary", []):
        lines.append(
            f"| `{row['family']}` | `{row['candidate_count']}` | `{row['promoted_count']}` | "
            f"`{row['blocked_count']}` | `{row['high_priority_blocked_count']}` |"
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
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _promotion_row(item: dict[str, Any], annotation: dict[str, Any]) -> dict[str, Any]:
    candidate_id = str(item.get("candidate_id"))
    form = dict(item.get("evidence_form", {}))
    blockers = _missing_fields(form)
    if form.get("promotion_decision") != "promote":
        blockers.append("promotion_decision must be promote")
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
        }
    return {
        "candidate_id": candidate_id,
        "family": item.get("family"),
        "priority": item.get("priority", "unspecified"),
        "promotion_status": "promoted",
        "next_required_fields": [],
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
        blocked_rows = [row for row in family_rows if row.get("promotion_status") != "promoted"]
        summary.append(
            {
                "family": family,
                "candidate_count": len(family_rows),
                "promoted_count": promoted_count,
                "blocked_count": len(blocked_rows),
                "high_priority_blocked_count": sum(1 for row in blocked_rows if row.get("priority") == "high"),
            }
        )
    return summary


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
