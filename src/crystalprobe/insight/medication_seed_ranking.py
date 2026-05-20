"""Within-backend ranking summaries for medication polymorph seed sets."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any


def medication_seed_ranking_report(
    autonomy_report: dict[str, Any],
    measurement_summary: dict[str, Any],
) -> dict[str, Any]:
    """Rank medication seed structures only within shared measured backends."""

    measurement_lookup = _measurement_lookup(measurement_summary)
    targets = [
        _target_ranking(target, measurement_lookup)
        for target in autonomy_report.get("targets", [])
    ]
    rankable = [target for target in targets if target["ranking_status"] == "ranked_within_backend"]
    return {
        "schema_version": "0.1.0",
        "status": "medication_seed_ranking_recorded",
        "target_count": len(targets),
        "rankable_target_count": len(rankable),
        "targets": targets,
        "policy": [
            "Rankings compare structures only within the same backend.",
            "Energies are normalized to the selected candidate formula unit when formula counts are divisible.",
            "Seed rankings are model inspection evidence, not experimental polymorph stability truth.",
            "Do not compare absolute energies across MACE, AIMNet2, and UMA.",
        ],
    }


def medication_seed_ranking_markdown(report: dict[str, Any]) -> str:
    """Render medication seed ranking as Markdown."""

    lines = [
        "# Medication Seed Ranking",
        "",
        f"- Status: `{report['status']}`",
        f"- Targets: `{report['target_count']}`",
        f"- Rankable targets: `{report['rankable_target_count']}`",
        "",
        "## Target Summary",
        "",
        "| Target | Status | Backends | Blockers |",
        "|---|---|---|---|",
    ]
    for target in report["targets"]:
        lines.append(
            f"| {target['target']} | `{target['ranking_status']}` | "
            f"{', '.join(target['ranked_backends']) or 'none'} | {'; '.join(target['blockers']) or 'none'} |"
        )
    for target in report["targets"]:
        lines.extend(["", f"## {target['target']}", ""])
        for backend in target["backend_rankings"]:
            lines.extend(
                [
                    f"### {backend['backend']}",
                    "",
                    "| Rank | Structure | Block | eV / formula unit | Delta | Diagnostic Flags |",
                    "|---:|---|---|---:|---:|---|",
                ]
            )
            for row in backend["rows"]:
                lines.append(
                    f"| `{row['rank']}` | `{row['structure_id']}` | `{row['block_id']}` | "
                    f"{float(row['energy_ev_per_formula_unit']):.6f} | "
                    f"{float(row['delta_ev_per_formula_unit']):.6f} | "
                    f"{', '.join(row['diagnostic_flags']) or 'none'} |"
                )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _target_ranking(target: dict[str, Any], measurement_lookup: dict[str, dict[str, Any]]) -> dict[str, Any]:
    formula_key = str(target.get("best_formula_key") or "")
    measured_by_backend: dict[str, list[dict[str, Any]]] = {}
    for block in target.get("candidate_blocks", []):
        measurement = measurement_lookup.get(str(block.get("structure_id")), {})
        for row in measurement.get("backend_measurements", []):
            if row.get("status") != "measured":
                continue
            normalized = _normalized_row(block, row, formula_key)
            if normalized:
                measured_by_backend.setdefault(str(row["backend"]), []).append(normalized)
    backend_rankings = [_backend_ranking(backend, rows) for backend, rows in sorted(measured_by_backend.items()) if len(rows) >= 2]
    blockers = []
    if not backend_rankings:
        blockers.append("at least two normalized measurements from the same backend are required")
    blockers.extend(str(blocker) for blocker in target.get("blockers", []))
    return {
        "target": target.get("target"),
        "ranking_status": "ranked_within_backend" if backend_rankings else "not_rankable",
        "ranked_backends": [backend["backend"] for backend in backend_rankings],
        "backend_rankings": backend_rankings,
        "blockers": blockers,
    }


def _backend_ranking(backend: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = sorted(rows, key=lambda row: (float(row["energy_ev_per_formula_unit"]), row["structure_id"]))
    best = float(ranked[0]["energy_ev_per_formula_unit"])
    for index, row in enumerate(ranked, start=1):
        row["rank"] = index
        row["delta_ev_per_formula_unit"] = float(row["energy_ev_per_formula_unit"]) - best
    return {"backend": backend, "rows": ranked}


def _normalized_row(block: dict[str, Any], measurement: dict[str, Any], formula_key: str) -> dict[str, Any] | None:
    energy = measurement.get("energy_ev")
    formula = str(measurement.get("formula") or "")
    if energy is None or not formula_key or not formula:
        return None
    factor = _formula_unit_factor(_formula_counts(formula), _formula_counts(formula_key))
    if factor <= 0:
        return None
    return {
        "structure_id": str(block.get("structure_id") or ""),
        "block_id": str(block.get("block_id") or ""),
        "backend": str(measurement.get("backend") or ""),
        "formula": formula,
        "formula_unit_factor": factor,
        "energy_ev": float(energy),
        "energy_ev_per_formula_unit": float(energy) / factor,
        "diagnostic_flags": list(measurement.get("diagnostic_flags", [])),
    }


def _measurement_lookup(measurement_summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(block.get("structure_id")): dict(block)
        for target in measurement_summary.get("targets", [])
        for block in target.get("blocks", [])
        if block.get("structure_id")
    }


def _formula_unit_factor(measured: Counter[str], unit: Counter[str]) -> int:
    if not measured or not unit:
        return 0
    factors = []
    for element, count in unit.items():
        measured_count = measured.get(element, 0)
        if count <= 0 or measured_count % count != 0:
            return 0
        factors.append(measured_count // count)
    if any(measured.get(element, 0) != unit.get(element, 0) * factors[0] for element in measured):
        return 0
    return int(factors[0]) if len(set(factors)) == 1 else 0


def _formula_counts(formula: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for element, count in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
        counts[element] += int(count or "1")
    return counts
