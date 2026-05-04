"""Preliminary findings memo generation."""

from __future__ import annotations

from typing import Any


def preliminary_findings_memo(
    *,
    ampetp_readiness: dict[str, Any],
    ampetp_sensitivity: dict[str, Any],
    cposs_bridge: dict[str, Any],
    bundle_manifest: dict[str, Any],
    therapeutic_contrast: dict[str, Any] | None = None,
) -> str:
    """Render a concise preliminary findings memo from local reports."""

    lines = [
        "# CrystalProbe Preliminary Findings Memo",
        "",
        "## Purpose",
        "",
        (
            "This memo summarizes the current local CrystalProbe evidence package. "
            "It is intended as a collaborator-facing and preprint-planning artifact, "
            "not as a final paper."
        ),
        "",
        "## Current Claim",
        "",
        (
            "CrystalProbe now has a paper-ready pilot on AMPETP, CCDC 1102740, "
            "showing a reproducible path from local CCDC source handling through "
            "two-backend MLIP measurement, local bond/force diagnostics, perturbation "
            "sensitivity, generated figures, and hashed artifact manifests."
        ),
        "",
        "## AMPETP Pilot Readiness",
        "",
        f"- Status: `{ampetp_readiness['status']}`.",
        f"- Checks passed: `{ampetp_readiness['passed']}`.",
        f"- Checks failed: `{ampetp_readiness['failed']}`.",
        f"- Bundle artifacts: `{len(bundle_manifest['artifacts'])}`.",
        f"- Bundle manifest SHA-256: `{bundle_manifest['manifest_sha256']}`.",
        "",
        "## AMPETP Sensitivity Finding",
        "",
    ]
    lines.extend(_sensitivity_lines(ampetp_sensitivity))
    lines.extend(
        [
            "",
            "## CPOSS Bridge Finding",
            "",
            f"- Families summarized: `{cposs_bridge['family_count']}`.",
            f"- Structures summarized: `{cposs_bridge['structure_count']}`.",
            "",
            "| Family | Structures | Lowest | Second gap (kJ/mol) | Span (kJ/mol) | Flagged fraction |",
            "|---|---:|---|---:|---:|---:|",
        ]
    )
    for family, data in sorted(cposs_bridge["families"].items()):
        lines.append(
            f"| {family} | {data['structure_count']} | {data['lowest_structure']} | "
            f"{_fmt(data['second_gap_kj_mol'])} | {_fmt(data['energy_span_kj_mol'])} | {_fmt(data['flagged_fraction'])} |"
        )
    if therapeutic_contrast:
        lines.extend(["", "## Therapeutic Sensitivity Contrast", ""])
        lines.extend(_contrast_lines(therapeutic_contrast))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The AMPETP result is a single-crystal workflow proof, not a polymorph ranking. "
                "The CPOSS bridge shows how the same diagnostics begin to scale into within-family "
                "relative-energy summaries, but those summaries still require curated experimental "
                "stability labels before they become headline benchmark claims."
            ),
            "",
            "## Immediate Next Work",
            "",
            "1. Promote CPOSS bridge structures into curated pair records with experimental stability evidence.",
            "2. Add UMA measurements once model access is approved.",
            "3. Run AIMNet2 on the ibuprofen sensitivity grid in Linux/Docker.",
            "4. Convert this memo into the first ChemRxiv-style preliminary findings draft.",
            "",
            "## Guardrails",
            "",
            "- Raw CCDC/CSD source coordinates remain local and are not redistributed.",
            "- Generated perturbation CIFs are probes, not experimentally observed crystal forms.",
            "- Cross-backend absolute energy differences are provenance diagnostics, not calibrated thermodynamic uncertainty.",
            "- CPOSS bridge values are local MACE summaries, not verified experimental stability rankings.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _sensitivity_lines(summary: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for backend, data in sorted(summary["backends"].items()):
        variants = [row for row in data["variants"] if row["variant"] != summary["reference_variant"]]
        largest = max(variants, key=lambda row: abs(float(row["energy_delta_ev"])))
        lines.extend(
            [
                f"- `{backend}` max absolute energy delta: `{float(data['max_abs_energy_delta_ev']):.6f} eV`.",
                f"- `{backend}` mean absolute energy delta: `{float(data['mean_abs_energy_delta_ev']):.6f} eV`.",
                (
                    f"- `{backend}` largest-response variant: `{largest['variant']}` "
                    f"with flags `{', '.join(largest.get('diagnostic_flags', [])) or 'none'}`."
                ),
            ]
        )
    return lines


def _contrast_lines(report: dict[str, Any]) -> list[str]:
    lines = [
        f"- Backend: `{report['backend']}`.",
        f"- Targets compared: `{report['target_count']}`.",
        "",
        "| Target | Max abs delta (eV) | Largest-response variant | Flags |",
        "|---|---:|---|---|",
    ]
    for row in report["targets"]:
        lines.append(
            f"| {row['target']} | {float(row['max_abs_energy_delta_ev']):.6f} | "
            f"{row['largest_response_variant']} | {', '.join(row['largest_response_flags']) or 'none'} |"
        )
    return lines


def _fmt(value: Any) -> str:
    return "n/a" if value is None else f"{float(value):.3f}"
