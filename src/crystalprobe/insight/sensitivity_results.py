"""Summaries for perturbation sensitivity inference outputs."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import fmean
from typing import Any

EV_TO_KJ_PER_MOL = 96.48533212331002


def load_sensitivity_rows(paths: list[str | Path]) -> list[dict[str, Any]]:
    """Load JSONL sensitivity prediction rows from one or more files."""

    rows: list[dict[str, Any]] = []
    for path in paths:
        with Path(path).open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                row = json.loads(stripped)
                missing = {"backend", "variant", "energy_ev"} - set(row)
                if missing:
                    raise ValueError(f"{path}:{line_number}: missing required fields {sorted(missing)}")
                rows.append(row)
    return rows


def summarize_sensitivity(rows: list[dict[str, Any]], *, reference_variant: str = "reference") -> dict[str, Any]:
    """Summarize energy and force sensitivity relative to a reference variant."""

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["backend"]), []).append(row)

    backends: dict[str, Any] = {}
    for backend, backend_rows in sorted(grouped.items()):
        reference = _find_variant(backend_rows, reference_variant)
        variants = []
        for row in sorted(backend_rows, key=lambda item: str(item["variant"])):
            energy_delta_ev = float(row["energy_ev"]) - float(reference["energy_ev"])
            variants.append(
                {
                    "variant": row["variant"],
                    "energy_ev": row["energy_ev"],
                    "energy_delta_ev": energy_delta_ev,
                    "energy_delta_kj_per_mol": energy_delta_ev * EV_TO_KJ_PER_MOL,
                    "max_force_ev_per_ang": row.get("force_summary", {}).get("max_force_ev_per_ang"),
                    "mean_force_ev_per_ang": row.get("force_summary", {}).get("mean_force_ev_per_ang"),
                    "rms_position_delta_ang": row.get("perturbation", {}).get("rms_position_delta_ang"),
                    "cell_frobenius_delta_ang": row.get("perturbation", {}).get("cell_frobenius_delta_ang"),
                    "diagnostic_flags": row.get("local_geometry", {}).get("diagnostic_flags", []),
                }
            )
        deltas = [abs(float(item["energy_delta_ev"])) for item in variants if item["variant"] != reference_variant]
        backends[backend] = {
            "reference_energy_ev": reference["energy_ev"],
            "variant_count": len(variants),
            "max_abs_energy_delta_ev": max(deltas, default=0.0),
            "mean_abs_energy_delta_ev": fmean(deltas) if deltas else 0.0,
            "variants": variants,
        }
    return {
        "schema_version": "0.1.0",
        "reference_variant": reference_variant,
        "backend_count": len(backends),
        "backends": backends,
        "interpretation": [
            "Energy deltas are relative to each backend's own reference prediction.",
            "Perturbation structures are generated sensitivity probes, not experimentally observed forms.",
        ],
    }


def sensitivity_markdown(summary: dict[str, Any], *, title: str = "CrystalProbe Sensitivity Summary") -> str:
    """Render a sensitivity summary as Markdown."""

    lines = [f"# {title}", ""]
    for backend, data in summary["backends"].items():
        lines.extend(
            [
                f"## {backend}",
                "",
                f"- Reference energy: `{float(data['reference_energy_ev']):.6f} eV`.",
                f"- Max absolute energy delta: `{float(data['max_abs_energy_delta_ev']):.6f} eV`.",
                f"- Mean absolute energy delta: `{float(data['mean_abs_energy_delta_ev']):.6f} eV`.",
                "",
                "| Variant | Energy delta (eV) | Energy delta (kJ/mol) | Max force (eV/Ang) | RMS position delta (Ang) | Cell delta (Ang) | Flags |",
                "|---|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in data["variants"]:
            flags = ", ".join(row.get("diagnostic_flags", [])) or "none"
            lines.append(
                f"| {row['variant']} | {float(row['energy_delta_ev']):.6f} | "
                f"{float(row['energy_delta_kj_per_mol']):.3f} | "
                f"{float(row['max_force_ev_per_ang']):.6f} | "
                f"{float(row['rms_position_delta_ang'] or 0.0):.6f} | "
                f"{float(row['cell_frobenius_delta_ang'] or 0.0):.6f} | {flags} |"
            )
        lines.append("")
    lines.extend(["## Guardrails", ""])
    lines.extend(f"- {note}" for note in summary["interpretation"])
    return "\n".join(lines).rstrip() + "\n"


def _find_variant(rows: list[dict[str, Any]], variant: str) -> dict[str, Any]:
    for row in rows:
        if row["variant"] == variant:
            return row
    raise ValueError(f"reference variant not found: {variant}")
