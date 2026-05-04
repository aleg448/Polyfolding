"""Single-structure case-study reports for measured crystal targets."""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import fmean
from typing import Any


EV_TO_KJ_PER_MOL = 96.48533212331002


def load_prediction(path: str | Path) -> dict[str, Any]:
    """Load one structure-inference JSON prediction."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_single_structure_case_study(
    predictions: list[dict[str, Any]],
    *,
    title: str,
    source_record: dict[str, Any] | None = None,
    top_n: int = 5,
) -> dict[str, Any]:
    """Build a model-agreement report for one measured crystal structure.

    The report is intended for early research dossiers where there is one
    structure and multiple backend predictions. Cross-backend absolute energies
    are recorded as a diagnostic spread, not as a physical stability gap.
    """

    if len(predictions) < 2:
        raise ValueError("at least two predictions are required for a case-study comparison")

    formulas = sorted({str(prediction.get("formula")) for prediction in predictions})
    natoms = sorted({int(prediction.get("natoms", 0)) for prediction in predictions})
    pbc = sorted({_pbc_key(prediction.get("pbc", [])) for prediction in predictions})
    energies = [float(prediction["energy_ev"]) for prediction in predictions]
    top_force_sets = [_top_force_atom_set(prediction, top_n=top_n) for prediction in predictions]
    top_bond_sets = [_top_bond_pair_set(prediction, top_n=top_n) for prediction in predictions]

    return {
        "title": title,
        "structure": {
            "structure_id": predictions[0].get("structure_id"),
            "formula": formulas[0] if len(formulas) == 1 else formulas,
            "natoms": natoms[0] if len(natoms) == 1 else natoms,
            "pbc": pbc[0] if len(pbc) == 1 else pbc,
            "source_record": source_record,
        },
        "backend_predictions": [_prediction_summary(prediction) for prediction in predictions],
        "agreement": {
            "backend_count": len(predictions),
            "energy_mean_ev": fmean(energies),
            "energy_sample_std_ev": _sample_std(energies),
            "energy_range_ev": max(energies) - min(energies),
            "energy_range_kj_per_mol": (max(energies) - min(energies)) * EV_TO_KJ_PER_MOL,
            "top_force_atom_jaccard": _mean_pairwise_jaccard(top_force_sets),
            "top_bond_outlier_jaccard": _mean_pairwise_jaccard(top_bond_sets),
            "shared_diagnostic_flags": sorted(set.intersection(*[_diagnostic_flags(prediction) for prediction in predictions])),
            "any_short_contacts": any(_short_contacts(prediction) for prediction in predictions),
            "notes": [
                "Cross-backend absolute energy spread is a reproducibility diagnostic, not a calibrated physical stability gap.",
                "Bond diagnostics are geometric and force-based; they are not a unique per-bond energy decomposition.",
            ],
        },
    }


def case_study_markdown(report: dict[str, Any]) -> str:
    """Render a case-study report as Markdown."""

    lines = [
        f"# {report['title']}",
        "",
        "## Structure",
        "",
        f"- Structure ID: `{report['structure']['structure_id']}`",
        f"- Formula: `{report['structure']['formula']}`",
        f"- Atoms: `{report['structure']['natoms']}`",
        f"- PBC: `{report['structure']['pbc']}`",
        "",
    ]
    source_record = report["structure"].get("source_record")
    if source_record:
        lines.extend(
            [
                "## Source Record",
                "",
                f"- Selected block: `{source_record.get('selected_block_id')}`",
                f"- CCDC deposition: `{source_record.get('ccdc_deposition')}`",
                f"- Name: `{source_record.get('name')}`",
                f"- Local source path: `{source_record.get('local_source_path')}`",
                "",
            ]
        )

    lines.extend(["## Backend Measurements", "", _backend_table(report["backend_predictions"]), ""])
    agreement = report["agreement"]
    lines.extend(
        [
            "## Agreement Diagnostics",
            "",
            f"- Energy range: `{agreement['energy_range_ev']:.6f} eV` (`{agreement['energy_range_kj_per_mol']:.3f} kJ/mol`).",
            f"- Energy sample standard deviation: `{agreement['energy_sample_std_ev']:.6f} eV`.",
            f"- Top-force atom Jaccard agreement: `{agreement['top_force_atom_jaccard']:.3f}`.",
            f"- Top bond-outlier Jaccard agreement: `{agreement['top_bond_outlier_jaccard']:.3f}`.",
            f"- Shared diagnostic flags: `{', '.join(agreement['shared_diagnostic_flags']) or 'none'}`.",
            f"- Any severe short contacts: `{agreement['any_short_contacts']}`.",
            "",
            "## Interpretation Guardrails",
            "",
        ]
    )
    lines.extend(f"- {note}" for note in agreement["notes"])
    return "\n".join(lines).rstrip() + "\n"


def _prediction_summary(prediction: dict[str, Any]) -> dict[str, Any]:
    local_geometry = prediction.get("local_geometry", {})
    force_summary = prediction.get("force_summary", {})
    return {
        "backend": prediction.get("backend"),
        "energy_ev": prediction.get("energy_ev"),
        "max_force_ev_per_ang": force_summary.get("max_force_ev_per_ang"),
        "mean_force_ev_per_ang": force_summary.get("mean_force_ev_per_ang"),
        "bond_count": local_geometry.get("bond_count"),
        "diagnostic_flags": local_geometry.get("diagnostic_flags", []),
        "top_force_hotspots": local_geometry.get("force_hotspots", [])[:5],
        "top_bond_outliers": local_geometry.get("bond_geometry_outliers", [])[:5],
        "short_contacts": local_geometry.get("short_contacts", [])[:5],
        "model_metadata": prediction.get("model_metadata", {}),
    }


def _backend_table(rows: list[dict[str, Any]]) -> str:
    table = [
        "| Backend | Energy (eV) | Max force (eV/Ang) | Mean force (eV/Ang) | Bonds | Flags |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        flags = ", ".join(row.get("diagnostic_flags", [])) or "none"
        table.append(
            f"| {row['backend']} | {float(row['energy_ev']):.6f} | "
            f"{float(row['max_force_ev_per_ang']):.6f} | {float(row['mean_force_ev_per_ang']):.6f} | "
            f"{row['bond_count']} | {flags} |"
        )
    return "\n".join(table)


def _pbc_key(values: Any) -> str:
    return ",".join("true" if value else "false" for value in values)


def _diagnostic_flags(prediction: dict[str, Any]) -> set[str]:
    return set(prediction.get("local_geometry", {}).get("diagnostic_flags", []))


def _short_contacts(prediction: dict[str, Any]) -> list[dict[str, Any]]:
    return list(prediction.get("local_geometry", {}).get("short_contacts", []))


def _top_force_atom_set(prediction: dict[str, Any], *, top_n: int) -> set[int]:
    hotspots = prediction.get("local_geometry", {}).get("force_hotspots", [])
    return {int(item["atom_index"]) for item in hotspots[:top_n]}


def _top_bond_pair_set(prediction: dict[str, Any], *, top_n: int) -> set[tuple[int, int]]:
    outliers = prediction.get("local_geometry", {}).get("bond_geometry_outliers", [])
    pairs = set()
    for item in outliers[:top_n]:
        left = int(item["atom_i"])
        right = int(item["atom_j"])
        pairs.add((min(left, right), max(left, right)))
    return pairs


def _mean_pairwise_jaccard(sets: list[set[Any]]) -> float:
    scores: list[float] = []
    for left_index, left in enumerate(sets):
        for right in sets[left_index + 1 :]:
            union = left | right
            scores.append(len(left & right) / len(union) if union else 1.0)
    return fmean(scores) if scores else math.nan


def _sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = fmean(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(variance)
