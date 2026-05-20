"""Medication polymorph generation readiness reports."""

from __future__ import annotations

from typing import Any


def medication_polymorph_generation_report(
    autonomy_report: dict[str, Any],
    benchmark_evidence: dict[str, Any],
    extraction_report: dict[str, Any],
    evidence_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Plan local-only generation work from verified-safe medication inputs."""

    evidence_by_target = {
        str(record.get("target")): dict(record)
        for record in (evidence_manifest or {}).get("records", [])
        if record.get("target")
    }
    gate_by_target = {
        str(row.get("target")): dict(row)
        for row in benchmark_evidence.get("targets", [])
        if row.get("target")
    }
    extraction_by_structure = {
        str(row.get("structure_id")): dict(row)
        for row in extraction_report.get("rows", [])
        if row.get("structure_id")
    }
    targets = [
        _target_generation_row(target, gate_by_target.get(str(target.get("target")), {}), extraction_by_structure, evidence_by_target.get(str(target.get("target")), {}))
        for target in autonomy_report.get("targets", [])
    ]
    return {
        "schema_version": "0.1.0",
        "status": "medication_polymorph_generation_planned",
        "target_count": len(targets),
        "generation_candidate_count": sum(1 for target in targets if target["generation_status"] != "not_ready"),
        "rankable_seed_target_count": sum(1 for target in targets if target["generation_status"] == "rankable_seed_set_ready"),
        "targets": targets,
        "policy": [
            "Existing local CIF blocks are seed candidates, not generated crystal landscapes.",
            "Potential generated forms must stay local-only until source and model licenses are reviewed.",
            "CrystalProbe should generate or import candidate forms only after identity, stereochemistry, and form-label scope are explicit.",
            "Generated forms are hypotheses; benchmark truth still requires external experimental source evidence.",
        ],
    }


def medication_polymorph_generation_markdown(report: dict[str, Any]) -> str:
    """Render the medication polymorph generation readiness report."""

    lines = [
        "# Medication Polymorph Generation Readiness",
        "",
        f"- Status: `{report['status']}`",
        f"- Targets: `{report['target_count']}`",
        f"- Generation candidates: `{report['generation_candidate_count']}`",
        f"- Rankable seed targets: `{report['rankable_seed_target_count']}`",
        "",
        "## Targets",
        "",
        "| Target | Status | Source Forms | Extracted Seeds | Coordinate Seeds | Shared Backends | Next Generation Step |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for target in report["targets"]:
        lines.append(
            f"| {target['target']} | `{target['generation_status']}` | "
            f"{', '.join(target['source_forms']) or 'none'} | `{target['extracted_seed_count']}` | "
            f"`{target['coordinate_bearing_seed_count']}` | "
            f"{', '.join(target['shared_measured_backends']) or 'none'} | {target['next_generation_step']} |"
        )
    for target in report["targets"]:
        lines.extend(["", f"## {target['target']}", ""])
        lines.append(f"- Claim tier: `{target['claim_tier']}`")
        lines.append("- Seed structures:")
        lines.extend(
            f"  - `{seed['structure_id']}` from block `{seed['block_id']}`: "
            f"`{seed['extraction_status']}` / `{seed['coordinate_status']}`"
            for seed in target["seed_structures"]
        )
        if not target["seed_structures"]:
            lines.append("  - none")
        lines.append("- Blockers:")
        lines.extend(f"  - {blocker}" for blocker in target["blockers"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _target_generation_row(
    target: dict[str, Any],
    gate: dict[str, Any],
    extraction_by_structure: dict[str, dict[str, Any]],
    evidence_record: dict[str, Any],
) -> dict[str, Any]:
    seeds = [
        _seed_row(block, extraction_by_structure.get(str(block.get("structure_id")), {}))
        for block in target.get("candidate_blocks", [])
    ]
    extracted_seed_count = sum(1 for seed in seeds if seed["extraction_status"] == "extracted")
    coordinate_bearing_seed_count = sum(
        1
        for seed in seeds
        if seed["extraction_status"] == "extracted" and seed["coordinate_status"] == "coordinate_bearing"
    )
    shared_backends = list(target.get("shared_measured_backends", []))
    source_forms = _source_forms(evidence_record)
    blockers = list(gate.get("blockers", []))
    if extracted_seed_count >= 2 and coordinate_bearing_seed_count < 2:
        blockers.append("at least two extracted seed blocks must contain atom-site coordinates")
    generation_status = _generation_status(target, gate, extracted_seed_count, coordinate_bearing_seed_count, shared_backends)
    return {
        "target": target.get("target"),
        "generation_status": generation_status,
        "claim_tier": gate.get("claim_tier", "unknown"),
        "source_forms": source_forms,
        "candidate_block_count": target.get("candidate_block_count", 0),
        "extracted_seed_count": extracted_seed_count,
        "coordinate_bearing_seed_count": coordinate_bearing_seed_count,
        "shared_measured_backends": shared_backends,
        "seed_structures": seeds,
        "blockers": blockers,
        "next_generation_step": _next_generation_step(generation_status, blockers),
    }


def _seed_row(block: dict[str, Any], extraction: dict[str, Any]) -> dict[str, str]:
    return {
        "block_id": str(block.get("block_id") or ""),
        "structure_id": str(block.get("structure_id") or ""),
        "target_role": str(block.get("target_role") or ""),
        "extraction_status": str(extraction.get("status") or "not_extracted"),
        "coordinate_status": str(extraction.get("coordinate_status") or "unknown"),
        "path": str(extraction.get("output") or ""),
    }


def _source_forms(evidence_record: dict[str, Any]) -> list[str]:
    form_map = evidence_record.get("form_label_map")
    if isinstance(form_map, dict):
        return [str(item) for item in form_map.get("source_forms", [])]
    return []


def _generation_status(
    target: dict[str, Any],
    gate: dict[str, Any],
    extracted_seed_count: int,
    coordinate_bearing_seed_count: int,
    shared_backends: list[str],
) -> str:
    if target.get("autonomous_detection_status") == "single_structure_only":
        return "not_ready"
    if extracted_seed_count < 2:
        return "needs_seed_extraction"
    if coordinate_bearing_seed_count < 2:
        return "needs_coordinate_bearing_seeds"
    if not shared_backends:
        return "seed_set_extracted_measurements_needed"
    if gate.get("claim_tier") == "source_verified_autonomous_benchmark_candidate":
        return "rankable_seed_set_ready"
    return "seed_set_extracted_evidence_gate_blocked"


def _next_generation_step(generation_status: str, blockers: list[str]) -> str:
    if generation_status == "not_ready":
        return "Acquire or select a second parent-like structure before generating a form set."
    if generation_status == "needs_seed_extraction":
        return "Extract at least two local-only seed CIF blocks."
    if generation_status == "needs_coordinate_bearing_seeds":
        return "Find or import at least two coordinate-bearing seed structures before backend ranking."
    if generation_status == "seed_set_extracted_measurements_needed":
        return "Run the same backend on at least two extracted seed structures, then compare within-backend ranking."
    if generation_status == "seed_set_extracted_evidence_gate_blocked":
        return "Resolve evidence-gate blockers before using generated forms in benchmark claims."
    if generation_status == "rankable_seed_set_ready":
        return "Start CSP/FastCSP-style local generation or import generated candidates, then rank within a backend."
    return blockers[0] if blockers else "Review generation status."
