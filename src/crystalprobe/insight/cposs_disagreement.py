"""Backend disagreement reports for CPOSS candidate-pair measurements."""

from __future__ import annotations

from statistics import fmean
from typing import Any

from crystalprobe.insight.structure_predictions import EV_TO_KJ_MOL, formula_unit_count, infer_common_formula_unit


def cposs_backend_disagreement_report(
    rows_by_backend: dict[str, list[dict[str, Any]]],
    *,
    title: str = "CPOSS backend disagreement report",
) -> dict[str, Any]:
    """Compare backend ordering and diagnostics for CPOSS candidate pairs."""

    backend_families = {
        backend: _summarize_backend(rows)
        for backend, rows in sorted(rows_by_backend.items())
    }
    families = sorted(set().union(*(set(data) for data in backend_families.values())) if backend_families else set())
    family_reports = [
        _family_report(family, backend_families)
        for family in families
    ]
    return {
        "schema_version": "0.1.0",
        "title": title,
        "status": "cposs_backend_disagreement_recorded",
        "backend_count": len(rows_by_backend),
        "family_count": len(family_reports),
        "families": family_reports,
        "overall": _overall(family_reports),
        "interpretation": [
            "Backend ordering is compared only within each backend after formula-unit normalization.",
            "Agreement on the lower-energy structure is behavioural evidence, not experimental stability evidence.",
            "Diagnostic-flag disagreement is useful for inspection and uncertainty triage.",
        ],
    }


def cposs_backend_disagreement_markdown(report: dict[str, Any]) -> str:
    """Render CPOSS backend disagreement as Markdown."""

    lines = [
        f"# {report['title']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Backends: `{report['backend_count']}`",
        f"- Families: `{report['family_count']}`",
        f"- Ranking consensus fraction: `{float(report['overall']['ranking_consensus_fraction']):.3f}`",
        f"- Mean diagnostic flag Jaccard: `{float(report['overall']['mean_flag_jaccard']):.3f}`",
        "",
        "## Families",
        "",
        "| Family | Ranking consensus | Lower structures | Gap range (kJ/mol/f.u.) | Mean flag Jaccard |",
        "|---|---|---|---:|---:|",
    ]
    for family in report["families"]:
        lower = ", ".join(f"{backend}:{row['lower_structure']}" for backend, row in family["backends"].items())
        lines.append(
            f"| {family['family']} | `{family['ranking_consensus']}` | {lower} | "
            f"{float(family['gap_range_kj_mol_per_formula_unit']):.3f} | "
            f"{float(family['mean_flag_jaccard']):.3f} |"
        )
    for family in report["families"]:
        lines.extend(["", f"## {family['family']} Backend Details", ""])
        lines.extend(
            [
                "| Backend | Lower | Higher | Gap (kJ/mol/f.u.) | Lower flags | Higher flags |",
                "|---|---|---|---:|---|---|",
            ]
        )
        for backend, row in family["backends"].items():
            lines.append(
                f"| {backend} | {row['lower_structure']} | {row['higher_structure']} | "
                f"{float(row['gap_kj_mol_per_formula_unit']):.3f} | "
                f"{', '.join(row['lower_diagnostic_flags']) or 'none'} | "
                f"{', '.join(row['higher_diagnostic_flags']) or 'none'} |"
            )
    lines.extend(["", "## Guardrails", ""])
    lines.extend(f"- {note}" for note in report["interpretation"])
    return "\n".join(lines).rstrip() + "\n"


def _summarize_backend(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["family_code"]), []).append(row)

    summaries: dict[str, dict[str, Any]] = {}
    for family, family_rows in grouped.items():
        formula_unit = infer_common_formula_unit(str(row["formula"]) for row in family_rows)
        normalized = []
        for row in family_rows:
            units = formula_unit_count(str(row["formula"]), formula_unit)
            normalized.append(
                {
                    "block_id": row["block_id"],
                    "energy_ev_per_formula_unit": float(row["energy_ev"]) / units,
                    "diagnostic_flags": row.get("local_geometry", {}).get("diagnostic_flags", []),
                    "max_force_ev_per_ang": row.get("force_summary", {}).get("max_force_ev_per_ang"),
                }
            )
        ordered = sorted(normalized, key=lambda row: row["energy_ev_per_formula_unit"])
        lower = ordered[0]
        higher = ordered[-1]
        summaries[family] = {
            "lower_structure": lower["block_id"],
            "higher_structure": higher["block_id"],
            "gap_kj_mol_per_formula_unit": (higher["energy_ev_per_formula_unit"] - lower["energy_ev_per_formula_unit"]) * EV_TO_KJ_MOL,
            "lower_diagnostic_flags": lower["diagnostic_flags"],
            "higher_diagnostic_flags": higher["diagnostic_flags"],
            "lower_max_force_ev_per_ang": lower.get("max_force_ev_per_ang"),
            "higher_max_force_ev_per_ang": higher.get("max_force_ev_per_ang"),
        }
    return summaries


def _family_report(family: str, backend_families: dict[str, dict[str, dict[str, Any]]]) -> dict[str, Any]:
    backends = {
        backend: families[family]
        for backend, families in backend_families.items()
        if family in families
    }
    lower_structures = {row["lower_structure"] for row in backends.values()}
    gaps = [float(row["gap_kj_mol_per_formula_unit"]) for row in backends.values()]
    flag_scores = [
        _family_flag_jaccard(left, right)
        for left_index, left in enumerate(backends.values())
        for right_index, right in enumerate(backends.values())
        if left_index < right_index
    ]
    return {
        "family": family,
        "ranking_consensus": len(lower_structures) == 1,
        "backend_count": len(backends),
        "backends": backends,
        "gap_range_kj_mol_per_formula_unit": max(gaps) - min(gaps) if gaps else 0.0,
        "mean_flag_jaccard": fmean(flag_scores) if flag_scores else 1.0,
    }


def _family_flag_jaccard(left: dict[str, Any], right: dict[str, Any]) -> float:
    left_flags = set(left.get("lower_diagnostic_flags", [])) | set(left.get("higher_diagnostic_flags", []))
    right_flags = set(right.get("lower_diagnostic_flags", [])) | set(right.get("higher_diagnostic_flags", []))
    if not left_flags and not right_flags:
        return 1.0
    return len(left_flags & right_flags) / len(left_flags | right_flags)


def _overall(families: list[dict[str, Any]]) -> dict[str, Any]:
    if not families:
        return {"ranking_consensus_fraction": 0.0, "mean_flag_jaccard": 0.0}
    return {
        "ranking_consensus_fraction": fmean(1.0 if family["ranking_consensus"] else 0.0 for family in families),
        "mean_flag_jaccard": fmean(float(family["mean_flag_jaccard"]) for family in families),
    }
