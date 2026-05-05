"""Inspection reports for CPOSS backend-disagreement cases."""

from __future__ import annotations

from typing import Any


def cposs_disagreement_inspection_report(
    disagreement_report: dict[str, Any],
    *,
    family: str = "CBZ",
) -> dict[str, Any]:
    """Build a focused inspection report for one CPOSS family."""

    family_record = _find_family(disagreement_report, family)
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
        "findings": _findings(family_record, lower_structures, gaps, flag_sets),
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
    findings.append(
        "This inspection supports uncertainty-wrapper development and case selection, not polymorph stability ranking."
    )
    return findings
