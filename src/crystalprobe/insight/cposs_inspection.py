"""Inspection reports for CPOSS backend-disagreement cases."""

from __future__ import annotations

from typing import Any


def cposs_disagreement_inspection_report(
    disagreement_report: dict[str, Any],
    *,
    family: str = "CBZ",
    mace_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a focused inspection report for one CPOSS family."""

    family_record = _find_family(disagreement_report, family)
    mace_family_screen = _mace_family_screen(mace_summary or {}, family, family_record)
    backends = family_record.get("backends", {})
    lower_structures = {
        backend: row.get("lower_structure")
        for backend, row in backends.items()
    }
    gaps = {
        backend: float(row.get("gap_kj_mol_per_formula_unit", 0.0))
        for backend, row in backends.items()
    }
    flag_sets = {
        backend: sorted(set(row.get("lower_diagnostic_flags", [])) | set(row.get("higher_diagnostic_flags", [])))
        for backend, row in backends.items()
    }
    return {
        "schema_version": "0.1.0",
        "status": "cposs_disagreement_inspection_recorded",
        "family": family_record.get("family"),
        "backend_count": family_record.get("backend_count"),
        "ranking_consensus": family_record.get("ranking_consensus"),
        "lower_structures": lower_structures,
        "gap_kj_mol_per_formula_unit": gaps,
        "gap_range_kj_mol_per_formula_unit": family_record.get("gap_range_kj_mol_per_formula_unit"),
        "diagnostic_flags": flag_sets,
        "mean_flag_jaccard": family_record.get("mean_flag_jaccard"),
        "mace_family_screen": mace_family_screen,
        "findings": _findings(family_record, lower_structures, gaps, flag_sets, mace_family_screen),
        "recommended_next_actions": [
            "Run the same three backends on additional adjacent CBZ pairs before selecting a publication example.",
            "Inspect atom-level force hotspots for CBZ01_PsiCrys and CBZ03_PsiCrys in MACE and AIMNet2.",
            "Treat AIMNet2's large normalized gap as backend-behaviour evidence until input scaling and formula-unit normalization are independently checked.",
            "Do not turn this CPOSS disagreement into an experimental stability claim without curated form labels and stability citations.",
        ],
        "claim_boundary": "backend_behaviour_inspection_only",
    }


def cposs_disagreement_inspection_markdown(report: dict[str, Any]) -> str:
    """Render CPOSS disagreement inspection as Markdown."""

    lines = [
        f"# CPOSS {report['family']} Backend-Disagreement Inspection",
        "",
        f"- Status: `{report['status']}`",
        f"- Ranking consensus: `{report['ranking_consensus']}`",
        f"- Mean diagnostic flag Jaccard: `{float(report['mean_flag_jaccard']):.3f}`",
        f"- Claim boundary: `{report['claim_boundary']}`",
        "",
        "## Backend Ordering",
        "",
        "| Backend | Lower structure | Gap (kJ/mol/f.u.) | Diagnostic flags |",
        "|---|---|---:|---|",
    ]
    for backend, lower in report["lower_structures"].items():
        flags = ", ".join(report["diagnostic_flags"].get(backend, [])) or "none"
        lines.append(
            f"| {backend} | {lower} | {float(report['gap_kj_mol_per_formula_unit'][backend]):.3f} | {flags} |"
        )
    if report.get("mace_family_screen"):
        screen = report["mace_family_screen"]
        lines.extend(
            [
                "",
                "## MACE Family Screen",
                "",
                f"- Structures screened: `{screen['structure_count']}`",
                f"- MACE low-energy order: {', '.join(screen['energy_order'])}",
                f"- Next unmeasured adjacent pairs: {', '.join(screen['recommended_adjacent_pairs']) or 'none'}",
                "",
                "| Structure | Relative MACE energy (kJ/mol/f.u.) | Max force (eV/A) | Top force atom | Top bond outlier |",
                "|---|---:|---:|---|---|",
            ]
        )
        for row in screen["top_structures"]:
            lines.append(
                f"| {row['block_id']} | {float(row['relative_kj_mol_per_formula_unit']):.3f} | "
                f"{float(row['max_force_ev_per_ang']):.3f} | {row['top_force_atom']} | {row['top_bond_outlier']} |"
            )
    lines.extend(["", "## Findings", ""])
    lines.extend(f"- {finding}" for finding in report["findings"])
    lines.extend(["", "## Recommended Next Actions", ""])
    lines.extend(f"- {action}" for action in report["recommended_next_actions"])
    return "\n".join(lines).rstrip() + "\n"


def _find_family(report: dict[str, Any], family: str) -> dict[str, Any]:
    for family_record in report.get("families", []):
        if str(family_record.get("family")).casefold() == family.casefold():
            return family_record
    raise ValueError(f"Family {family!r} not found in CPOSS disagreement report")


def _findings(
    family_record: dict[str, Any],
    lower_structures: dict[str, str],
    gaps: dict[str, float],
    flag_sets: dict[str, list[str]],
    mace_family_screen: dict[str, Any] | None = None,
) -> list[str]:
    findings = []
    if not family_record.get("ranking_consensus"):
        findings.append(
            "Backend ordering disagreement is present: "
            + ", ".join(f"{backend} selects {structure}" for backend, structure in lower_structures.items())
            + "."
        )
    max_backend = max(gaps, key=lambda backend: gaps[backend]) if gaps else None
    min_backend = min(gaps, key=lambda backend: gaps[backend]) if gaps else None
    if max_backend and min_backend and gaps[min_backend] > 0:
        ratio = gaps[max_backend] / gaps[min_backend]
        findings.append(
            f"Gap magnitude is highly backend-dependent: {max_backend} is {ratio:.1f}x {min_backend} for this pair."
        )
    if len({tuple(flags) for flags in flag_sets.values()}) > 1:
        findings.append(
            "Diagnostic flag disagreement is present: "
            + ", ".join(f"{backend}={flags or ['none']}" for backend, flags in flag_sets.items())
            + "."
        )
    if mace_family_screen:
        next_pairs = mace_family_screen.get("recommended_adjacent_pairs", [])
        if next_pairs:
            findings.append(
                "The MACE family screen identifies additional close CBZ adjacent pairs for disagreement follow-up: "
                + ", ".join(next_pairs)
                + "."
            )
        if mace_family_screen.get("all_top_structures_flagged"):
            findings.append(
                "All top-ranked MACE CBZ structures carry local high-force diagnostics, so force-hotspot review should precede any paper-facing stability language."
            )
    findings.append(
        "This inspection supports uncertainty-wrapper development and case selection, not polymorph stability ranking."
    )
    return findings


def _mace_family_screen(
    mace_summary: dict[str, Any],
    family: str,
    family_record: dict[str, Any],
) -> dict[str, Any] | None:
    family_summary = mace_summary.get("families", {}).get(family)
    if not family_summary:
        return None
    structures = list(family_summary.get("structures", []))
    if not structures:
        return None
    ordered = sorted(structures, key=lambda row: float(row.get("relative_kj_mol_per_formula_unit", 0.0)))
    measured_pair = {
        structure
        for row in family_record.get("backends", {}).values()
        for structure in (row.get("lower_structure"), row.get("higher_structure"))
        if structure
    }
    adjacent_pairs = []
    for left, right in zip(ordered, ordered[1:]):
        left_id = str(left.get("block_id"))
        right_id = str(right.get("block_id"))
        if {left_id, right_id} == measured_pair:
            continue
        gap = abs(
            float(right.get("relative_kj_mol_per_formula_unit", 0.0))
            - float(left.get("relative_kj_mol_per_formula_unit", 0.0))
        )
        adjacent_pairs.append((gap, f"{left_id}-{right_id} ({gap:.3f} kJ/mol/f.u.)"))
    top_structures = [_screen_row(row) for row in ordered[:5]]
    return {
        "structure_count": len(ordered),
        "formula_unit": family_summary.get("formula_unit"),
        "energy_order": [str(row.get("block_id")) for row in ordered],
        "top_structures": top_structures,
        "recommended_adjacent_pairs": [
            label for _, label in sorted(adjacent_pairs, key=lambda item: item[0])[:3]
        ],
        "all_top_structures_flagged": all(row["local_diagnostic_flags"] for row in top_structures),
    }


def _screen_row(row: dict[str, Any]) -> dict[str, Any]:
    force_hotspot = row.get("top_force_hotspot") or {}
    bond_outlier = row.get("top_bond_geometry_outlier") or {}
    return {
        "block_id": row.get("block_id"),
        "relative_kj_mol_per_formula_unit": row.get("relative_kj_mol_per_formula_unit"),
        "max_force_ev_per_ang": row.get("max_force_ev_per_ang"),
        "local_diagnostic_flags": list(row.get("local_diagnostic_flags", [])),
        "top_force_atom": _force_atom_label(force_hotspot),
        "top_bond_outlier": _bond_outlier_label(bond_outlier),
    }


def _force_atom_label(force_hotspot: dict[str, Any]) -> str:
    if not force_hotspot:
        return "none"
    return f"{force_hotspot.get('symbol')}#{force_hotspot.get('atom_index')}"


def _bond_outlier_label(bond_outlier: dict[str, Any]) -> str:
    if not bond_outlier:
        return "none"
    return (
        f"{bond_outlier.get('symbols')} "
        f"{float(bond_outlier.get('distance_ang', 0.0)):.3f} A"
    )
