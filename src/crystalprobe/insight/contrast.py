"""Contrast reports across sensitivity summaries."""

from __future__ import annotations

from typing import Any


def build_sensitivity_contrast_report(
    *,
    title: str,
    targets: list[dict[str, Any]],
    backend: str,
) -> dict[str, Any]:
    """Compare one backend's perturbation sensitivity across targets."""

    rows = []
    for target in targets:
        summary = target["summary"]
        backend_summary = summary["backends"][backend]
        variants = [row for row in backend_summary["variants"] if row["variant"] != summary["reference_variant"]]
        largest = max(variants, key=lambda row: abs(float(row["energy_delta_ev"])))
        rows.append(
            {
                "target": target["name"],
                "backend": backend,
                "variant_count": backend_summary["variant_count"],
                "max_abs_energy_delta_ev": backend_summary["max_abs_energy_delta_ev"],
                "mean_abs_energy_delta_ev": backend_summary["mean_abs_energy_delta_ev"],
                "largest_response_variant": largest["variant"],
                "largest_response_energy_delta_ev": largest["energy_delta_ev"],
                "largest_response_flags": largest.get("diagnostic_flags", []),
                "largest_response_rms_position_delta_ang": largest.get("rms_position_delta_ang"),
                "largest_response_cell_delta_ang": largest.get("cell_frobenius_delta_ang"),
            }
        )
    return {
        "schema_version": "0.1.0",
        "title": title,
        "backend": backend,
        "target_count": len(rows),
        "targets": rows,
        "interpretation": [
            "Sensitivity deltas are compared qualitatively; each target is referenced to its own backend baseline.",
            "Generated perturbation structures are probes, not experimentally observed forms.",
            "Differences in diagnostic flags are useful failure-mode signals, not direct stability claims.",
        ],
    }


def sensitivity_contrast_markdown(report: dict[str, Any]) -> str:
    """Render a sensitivity contrast report as Markdown."""

    lines = [
        f"# {report['title']}",
        "",
        f"- Backend: `{report['backend']}`",
        f"- Targets: `{report['target_count']}`",
        "",
        "| Target | Variants | Max abs delta (eV) | Mean abs delta (eV) | Largest-response variant | Largest delta (eV) | Flags |",
        "|---|---:|---:|---:|---|---:|---|",
    ]
    for row in report["targets"]:
        lines.append(
            f"| {row['target']} | {row['variant_count']} | "
            f"{float(row['max_abs_energy_delta_ev']):.6f} | {float(row['mean_abs_energy_delta_ev']):.6f} | "
            f"{row['largest_response_variant']} | {float(row['largest_response_energy_delta_ev']):.6f} | "
            f"{', '.join(row['largest_response_flags']) or 'none'} |"
        )
    lines.extend(["", "## Interpretation Guardrails", ""])
    lines.extend(f"- {note}" for note in report["interpretation"])
    return "\n".join(lines).rstrip() + "\n"
