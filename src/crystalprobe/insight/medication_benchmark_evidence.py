"""Evidence-dossier gates for medication polymorphism benchmark candidates."""

from __future__ import annotations

from typing import Any


REQUIRED_DOSSIER_FIELDS = (
    "citation_doi_or_url",
    "stability_ordering",
    "stability_claim",
    "form_label_map",
    "identity_decision",
    "stereochemistry_decision",
    "license_decision",
    "disorder_decision",
    "contradiction_search",
    "curator",
    "reviewer",
    "promotion_decision",
)


def medication_benchmark_evidence_report(
    autonomy_report: dict[str, Any],
    evidence_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate source evidence before medication polymorphism benchmark promotion."""

    manifest_records = {
        str(record.get("target")): dict(record)
        for record in (evidence_manifest or {}).get("records", [])
        if record.get("target")
    }
    rows = [
        _target_evidence_row(target, manifest_records.get(str(target.get("target"))))
        for target in autonomy_report.get("targets", [])
    ]
    promotable = [row for row in rows if row["claim_tier"] == "source_verified_autonomous_benchmark_candidate"]
    return {
        "schema_version": "0.1.0",
        "status": "medication_benchmark_evidence_recorded",
        "target_count": len(rows),
        "autonomous_candidate_count": sum(1 for row in rows if row["autonomy_status"] != "single_structure_only"),
        "source_verified_autonomous_count": len(promotable),
        "targets": rows,
        "required_dossier_fields": list(REQUIRED_DOSSIER_FIELDS),
        "policy": [
            "Autonomous candidates remain unverified until external source evidence is complete.",
            "Without human expert review, the highest allowed tier is source_verified_autonomous_benchmark_candidate, not expert-verified benchmark truth.",
            "Rankable backend coverage is required for CrystalProbe benchmark use, but backend rankings do not establish experimental stability.",
            "Coordinate-bearing or CCDC/CSD-derived evidence remains local-only unless license review clears redistribution.",
        ],
    }


def medication_benchmark_evidence_markdown(report: dict[str, Any]) -> str:
    """Render the medication benchmark evidence gate."""

    lines = [
        "# Medication Benchmark Evidence Gate",
        "",
        f"- Status: `{report['status']}`",
        f"- Targets: `{report['target_count']}`",
        f"- Autonomous candidates: `{report['autonomous_candidate_count']}`",
        f"- Source-verified autonomous candidates: `{report['source_verified_autonomous_count']}`",
        "",
        "## Targets",
        "",
        "| Target | Autonomy | Claim Tier | Missing | Blockers |",
        "|---|---|---|---:|---|",
    ]
    for row in report["targets"]:
        lines.append(
            f"| {row['target']} | `{row['autonomy_status']}` | `{row['claim_tier']}` | "
            f"`{len(row['missing_fields'])}` | {'; '.join(row['blockers']) or 'none'} |"
        )
    lines.extend(["", "## Required Dossier Fields", ""])
    lines.extend(f"- `{field}`" for field in report["required_dossier_fields"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _target_evidence_row(target: dict[str, Any], dossier: dict[str, Any] | None) -> dict[str, Any]:
    autonomy_status = str(target.get("autonomous_detection_status") or "")
    measurement_readiness = str(target.get("measurement_readiness") or "")
    missing = _missing_fields(dossier or {})
    blockers = []
    if autonomy_status == "single_structure_only":
        blockers.append("autonomous polymorphism candidate is not established")
    if measurement_readiness != "rankable_within_backend":
        blockers.append("at least two candidate structures need shared-backend measurements")
    blockers.extend(str(item) for item in target.get("blockers", []))
    blockers.extend(f"{field} is required" for field in missing)
    if dossier and dossier.get("promotion_decision") not in {None, "", "promote_source_verified"}:
        blockers.append("promotion_decision is not promote_source_verified")
    claim_tier = _claim_tier(autonomy_status, measurement_readiness, missing, blockers, dossier or {})
    return {
        "target": target.get("target"),
        "autonomy_status": autonomy_status,
        "measurement_readiness": measurement_readiness,
        "claim_tier": claim_tier,
        "dossier_present": dossier is not None,
        "missing_fields": missing,
        "blockers": blockers,
        "candidate_block_count": target.get("candidate_block_count", 0),
        "shared_measured_backends": list(target.get("shared_measured_backends", [])),
    }


def _claim_tier(
    autonomy_status: str,
    measurement_readiness: str,
    missing: list[str],
    blockers: list[str],
    dossier: dict[str, Any],
) -> str:
    if autonomy_status == "single_structure_only":
        return "not_a_polymorphism_candidate"
    if missing or blockers:
        return "unverified_autonomous_candidate"
    if dossier.get("human_expert_review") is True:
        return "expert_reviewed_benchmark_candidate"
    return "source_verified_autonomous_benchmark_candidate"


def _missing_fields(dossier: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_DOSSIER_FIELDS if not _has_field(dossier, field)]


def _has_field(dossier: dict[str, Any], field: str) -> bool:
    if field == "citation_doi_or_url":
        return bool(dossier.get("citation_doi") or dossier.get("citation_url"))
    value = dossier.get(field)
    if value is None or value == "" or value == [] or value == {}:
        return False
    if _is_unresolved_value(value):
        return False
    return True


def _is_unresolved_value(value: Any) -> bool:
    if isinstance(value, str):
        text = value.strip().casefold()
        return text in {"unknown", "unresolved", "blocked", "pending"} or text.startswith(
            ("unknown:", "unresolved:", "blocked:", "pending:")
        )
    if isinstance(value, dict):
        status_text = " ".join(
            str(value.get(key, "")).strip().casefold()
            for key in ("status", "mapping_status", "decision_status")
        )
        return any(token in status_text for token in ("unknown", "unresolved", "blocked", "pending"))
    return False
