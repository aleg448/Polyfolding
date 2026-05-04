"""Mini-benchmark reports that bridge pilots to polymorph ranking."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import fmean
from typing import Any


def load_summary(path: str | Path) -> dict[str, Any]:
    """Load one structure-prediction summary JSON file."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_cposs_mini_benchmark_report(summaries: list[dict[str, Any]], *, title: str) -> dict[str, Any]:
    """Build a compact report from CPOSS relative-energy summaries."""

    families: dict[str, Any] = {}
    for summary in summaries:
        for family, data in summary.get("families", {}).items():
            structures = data.get("structures", [])
            relatives = [float(row["relative_kj_mol_per_formula_unit"]) for row in structures]
            flagged = [row for row in structures if row.get("local_diagnostic_flags")]
            families[family] = {
                "formula_unit": data.get("formula_unit"),
                "structure_count": len(structures),
                "lowest_structure": structures[0]["block_id"] if structures else None,
                "second_structure": structures[1]["block_id"] if len(structures) > 1 else None,
                "second_gap_kj_mol": relatives[1] if len(relatives) > 1 else None,
                "energy_span_kj_mol": max(relatives) - min(relatives) if relatives else None,
                "mean_relative_kj_mol": fmean(relatives) if relatives else None,
                "flagged_structure_count": len(flagged),
                "flagged_fraction": len(flagged) / len(structures) if structures else None,
                "top_force_hotspot": (structures[0].get("top_force_hotspot") if structures else None),
                "top_bond_geometry_outlier": (structures[0].get("top_bond_geometry_outlier") if structures else None),
                "structures": structures,
            }

    total_structures = sum(family["structure_count"] for family in families.values())
    return {
        "schema_version": "0.1.0",
        "title": title,
        "family_count": len(families),
        "structure_count": total_structures,
        "families": families,
        "interpretation": [
            "This mini-benchmark is a local CPOSS measurement bridge, not a curated experimental stability benchmark.",
            "Relative energies are normalized by inferred formula unit within each family.",
            "Local diagnostic flags should be reviewed before using ranking gaps as scientific claims.",
        ],
    }


def mini_benchmark_markdown(report: dict[str, Any]) -> str:
    """Render a mini-benchmark report as Markdown."""

    lines = [
        f"# {report['title']}",
        "",
        f"- Families: `{report['family_count']}`",
        f"- Structures: `{report['structure_count']}`",
        "",
        "## Family Summary",
        "",
        "| Family | Formula unit | Structures | Lowest | Second | Second gap (kJ/mol) | Span (kJ/mol) | Flagged fraction |",
        "|---|---|---:|---|---|---:|---:|---:|",
    ]
    for family, data in sorted(report["families"].items()):
        lines.append(
            f"| {family} | `{data['formula_unit']}` | {data['structure_count']} | "
            f"{data['lowest_structure']} | {data['second_structure']} | "
            f"{_fmt(data['second_gap_kj_mol'])} | {_fmt(data['energy_span_kj_mol'])} | "
            f"{_fmt(data['flagged_fraction'])} |"
        )
    lines.extend(["", "## Guardrails", ""])
    lines.extend(f"- {note}" for note in report["interpretation"])
    return "\n".join(lines).rstrip() + "\n"


def _fmt(value: Any) -> str:
    return "n/a" if value is None else f"{float(value):.3f}"
