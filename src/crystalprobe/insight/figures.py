"""Small SVG figure builders for paper-ready research artifacts."""

from __future__ import annotations

import html
import math
from pathlib import Path
from typing import Any

from crystalprobe.core.io import atomic_write_text


def write_svg(path: str | Path, svg: str) -> None:
    atomic_write_text(path, svg)


def claim_gate_svg(report: dict[str, Any], *, width: int = 1050, height: int = 470) -> str:
    """Render candidate/reviewed/verified record counts and claim permission."""

    rows = list(report.get("claim_gate", {}).get("rows", []))
    max_records = max((int(row.get("records", 0)) for row in rows), default=1)
    pieces = [_svg_open(width, height), _title("CrystalProbe claim gate", width)]
    pieces.append(_text(56, 88, "Benchmark claims are allowed only from verified evidence slices.", size=16, fill="#475569"))
    chart_x = 250
    chart_y = 132
    chart_width = 520
    row_height = 78
    for index, row in enumerate(rows):
        label = str(row.get("label", "unknown"))
        records = int(row.get("records", 0))
        y = chart_y + index * row_height
        color = _claim_status_color(label)
        bar_width = records / max(max_records, 1) * chart_width
        pieces.append(_text(56, y + 24, label, size=20, weight="700", fill="#111827"))
        pieces.append(_text(56, y + 50, _claim_short_status(label), size=13, fill="#475569"))
        pieces.append(_rect(chart_x, y, chart_width, 28, fill="#e5e7eb", stroke="none", radius=4))
        pieces.append(_rect(chart_x, y, bar_width, 28, fill=color, stroke="none", radius=4))
        pieces.append(_text(chart_x + chart_width + 18, y + 21, f"{records} records", size=15, fill="#111827"))
        pieces.extend(
            _wrapped_text(
                str(row.get("public_claim_allowed", "")),
                chart_x,
                y + 54,
                max_chars=78,
                fill="#334155",
                size=13,
            )
        )
    pieces.append(_text(56, height - 48, f"Decision: {report.get('claim_gate', {}).get('decision', 'unknown')}", size=15, fill="#0f172a"))
    pieces.append("</svg>")
    return "\n".join(pieces)


def demo_pipeline_svg(*, width: int = 1180, height: int = 330) -> str:
    """Render the public demo reliability pipeline."""

    return provenance_flow_svg(
        "CrystalProbe public demo pipeline",
        [
            "Manifest and evidence labels",
            "Energy predictions and uncertainty",
            "Ranking and slice metrics",
            "Calibration and OOD checks",
            "Claim gate",
            "Reports and ledger",
        ],
        width=width,
        height=height,
    )


def backend_readiness_svg(report: dict[str, Any], *, width: int = 1100, height: int = 520) -> str:
    """Render optional scientific backend availability and smoke status."""

    rows = list(report.get("optional_scientific_backends", []))
    pieces = [_svg_open(width, height), _title("Optional backend readiness", width)]
    pieces.append(_text(56, 88, "Scientific backends are useful when installed, but the public demo does not hide missing stacks.", size=15, fill="#475569"))
    x_name = 60
    x_available = 315
    x_smoke = 485
    x_detail = 665
    y0 = 132
    row_height = 62
    pieces.append(_text(x_name, y0 - 18, "Backend", size=14, weight="700", fill="#334155"))
    pieces.append(_text(x_available, y0 - 18, "Import", size=14, weight="700", fill="#334155"))
    pieces.append(_text(x_smoke, y0 - 18, "Smoke", size=14, weight="700", fill="#334155"))
    pieces.append(_text(x_detail, y0 - 18, "Detail", size=14, weight="700", fill="#334155"))
    for index, row in enumerate(rows):
        y = y0 + index * row_height
        pieces.append(_line(50, y - 28, width - 56, y - 28, stroke="#e5e7eb", width=1))
        name = str(row.get("name", "unknown"))
        available = bool(row.get("available"))
        smoke = str(row.get("smoke_status", "unknown"))
        pieces.append(_text(x_name, y, name, size=18, weight="700", fill="#111827"))
        pieces.append(_status_pill(x_available, y - 22, "yes" if available else "no", fill="#dcfce7" if available else "#f1f5f9", stroke="#16a34a" if available else "#94a3b8", text_fill="#166534" if available else "#475569"))
        pieces.append(_status_pill(x_smoke, y - 22, smoke.replace("_", " "), fill=_smoke_fill(smoke), stroke=_smoke_stroke(smoke), text_fill=_smoke_text(smoke)))
        detail = str(row.get("detail") or row.get("blocker") or "")
        pieces.extend(_wrapped_text(detail, x_detail, y - 4, max_chars=54, fill="#475569", size=12))
    pieces.append("</svg>")
    return "\n".join(pieces)


def provenance_ledger_svg(report: dict[str, Any], *, width: int = 1100, height: int = 430) -> str:
    """Render the public demo input/output provenance path."""

    pieces = [_svg_open(width, height), _title("Demo provenance ledger", width)]
    pieces.append(_text(56, 88, "The demo records exact inputs, generated reports, and a ledger path for rebuildability.", size=15, fill="#475569"))
    boxes = [
        ("Manifest", report.get("inputs", {}).get("manifest", "manifest")),
        ("Predictions", report.get("inputs", {}).get("predictions", "predictions")),
        ("Quick benchmark", "fingerprint + calibration"),
        ("Claim gate", report.get("claim_gate", {}).get("decision", "decision")),
        ("Ledger", report.get("outputs", {}).get("ledger", "ledger")),
    ]
    box_width = 178
    box_height = 88
    gap = 28
    start_x = 56
    y = 150
    for index, (heading, detail) in enumerate(boxes):
        x = start_x + index * (box_width + gap)
        pieces.append(_rect(x, y, box_width, box_height, fill="#f8fafc", stroke="#334155", radius=6))
        pieces.append(_text(x + 14, y + 28, heading, size=17, weight="700", fill="#0f172a"))
        pieces.extend(_wrapped_text(str(detail), x + 14, y + 54, max_chars=20, fill="#475569", size=12))
        if index < len(boxes) - 1:
            arrow_y = y + box_height / 2
            start = x + box_width + 6
            end = x + box_width + gap - 8
            pieces.append(_line(start, arrow_y, end, arrow_y, stroke="#475569", width=2))
            pieces.append(_polygon([(end, arrow_y), (end - 10, arrow_y - 6), (end - 10, arrow_y + 6)], fill="#475569"))
    pieces.append(_text(56, height - 52, "Ledger entries include manifest and prediction hashes in the quick-benchmark runner.", size=14, fill="#475569"))
    pieces.append("</svg>")
    return "\n".join(pieces)


def calibration_reliability_svg(calibration: dict[str, Any], *, width: int = 850, height: int = 560) -> str:
    """Render confidence calibration; show an honest empty state when no points exist."""

    bins = list(calibration.get("reliability_bins", []))
    pieces = [_svg_open(width, height), _title("Calibration reliability", width)]
    plot = _plot_area(width=width, height=height, left=90, right=58, top=108, bottom=96)
    _append_axes(pieces, plot, x_label="Predicted confidence", y_label="Empirical accuracy")
    pieces.append(_line(plot["x"], plot["y"] + plot["height"], plot["x"] + plot["width"], plot["y"], stroke="#94a3b8", width=1.5))
    active = [row for row in bins if row.get("count", 0) and row.get("mean_confidence") is not None and row.get("empirical_accuracy") is not None]
    if not active:
        pieces.append(_rect(plot["x"] + 94, plot["y"] + 124, plot["width"] - 188, 88, fill="#f8fafc", stroke="#cbd5e1", radius=6))
        pieces.append(_text(width / 2, plot["y"] + 158, "No verified calibration points yet", size=20, weight="700", fill="#334155", anchor="middle"))
        pieces.append(_text(width / 2, plot["y"] + 186, "The module renders this state instead of fabricating reliability evidence.", size=14, fill="#64748b", anchor="middle"))
    else:
        for row in active:
            x = plot["x"] + float(row["mean_confidence"]) * plot["width"]
            y = plot["y"] + (1.0 - float(row["empirical_accuracy"])) * plot["height"]
            radius = 5 + min(int(row.get("count", 1)), 12)
            pieces.append(_circle(x, y, radius, fill="#2563eb", stroke="#1e3a8a"))
            pieces.append(_text(x + 10, y - 8, f"n={row.get('count')}", size=12, fill="#334155"))
    pieces.append(_text(56, height - 34, f"ECE: {float(calibration.get('expected_calibration_error', 0.0)):.3f}; Brier: {float(calibration.get('brier_score', 0.0)):.3f}", size=14, fill="#475569"))
    pieces.append("</svg>")
    return "\n".join(pieces)


def energy_uncertainty_svg(rows: list[dict[str, Any]], *, width: int = 1050, height: int = 640) -> str:
    """Render energy gap versus uncertainty with visible curation-status labels."""

    pieces = [_svg_open(width, height), _title("Energy gap vs uncertainty", width)]
    pieces.append(_text(56, 88, "Every point carries its curation status; unverified points are inspection evidence only.", size=15, fill="#475569"))
    plot = _plot_area(width=width, height=height, left=100, right=250, top=122, bottom=102)
    _append_axes(pieces, plot, x_label="Predicted energy gap |Ea - Eb|", y_label="Combined uncertainty")
    if not rows:
        pieces.append(_rect(plot["x"] + 94, plot["y"] + 142, plot["width"] - 188, 74, fill="#f8fafc", stroke="#cbd5e1", radius=6))
        pieces.append(_text(width / 2, plot["y"] + 176, "No predicted pair records to plot", size=20, weight="700", fill="#334155", anchor="middle"))
        pieces.append("</svg>")
        return "\n".join(pieces)

    max_gap = max(float(row.get("energy_gap", 0.0)) for row in rows) or 1.0
    max_uncertainty = max(float(row.get("combined_uncertainty", 0.0)) for row in rows) or 1.0
    for row in rows:
        gap = float(row.get("energy_gap", 0.0))
        uncertainty = float(row.get("combined_uncertainty", 0.0))
        x = plot["x"] + gap / max_gap * plot["width"]
        y = plot["y"] + (1.0 - uncertainty / max_uncertainty) * plot["height"]
        status = str(row.get("curation_status", "unknown"))
        verified = status == "verified"
        ood = bool(row.get("ood_flag", False))
        fill = "#16a34a" if verified else "#f59e0b" if not ood else "#ef4444"
        stroke = "#166534" if verified else "#92400e" if not ood else "#991b1b"
        pieces.append(_circle(x, y, 7.2, fill=fill, stroke=stroke))
        label = str(row.get("label", row.get("pair_id", "pair")))
        tag = status if verified else f"{status}/unverified"
        pieces.extend(_wrapped_text(f"{label} ({tag})", x + 12, y - 8, max_chars=30, fill="#111827", size=12))
    legend_x = width - 210
    legend_y = 146
    pieces.append(_text(legend_x, legend_y - 24, "Status", size=17, weight="700", fill="#111827"))
    for index, (label, fill, stroke) in enumerate(
        [
            ("verified", "#16a34a", "#166534"),
            ("unverified", "#f59e0b", "#92400e"),
            ("OOD flagged", "#ef4444", "#991b1b"),
        ]
    ):
        y = legend_y + index * 34
        pieces.append(_circle(legend_x + 8, y - 5, 6.2, fill=fill, stroke=stroke))
        pieces.append(_text(legend_x + 26, y, label, size=14, fill="#111827"))
    pieces.append(_text(56, height - 36, "Gaps and uncertainties come from the demo prediction file; no stability claim is inferred from unverified records.", size=14, fill="#475569"))
    pieces.append("</svg>")
    return "\n".join(pieces)


def candidate_backend_summary_svg(case: dict[str, Any], *, width: int = 1120, height: int = 560) -> str:
    """Render a backend summary for one unverified public candidate case."""

    model_outputs = list(case.get("model_outputs", []))
    max_gap = max((float(row.get("gap_kj_mol_per_formula_unit", 0.0)) for row in model_outputs), default=1.0)
    max_log = math.log10(max_gap + 1.0) if max_gap > 0 else 1.0
    pieces = [_svg_open(width, height), _title("Unverified CPOSS candidate backend summary", width)]
    pieces.append(
        _text(
            56,
            88,
            f"{case.get('common_name', case.get('family', 'candidate'))}: {case.get('candidate_id', 'unknown')} | status: candidate/unverified",
            size=15,
            fill="#475569",
        )
    )
    pieces.append(_status_pill(56, 110, "unverified", fill="#fef3c7", stroke="#d97706", text_fill="#92400e"))
    pieces.append(_text(184, 127, "Backend outputs are inspection evidence only; experimental stability ranking is blocked.", size=14, fill="#92400e"))

    chart_x = 330
    chart_y = 174
    chart_width = 520
    row_height = 74
    pieces.append(_text(56, chart_y - 26, "Backend", size=14, weight="700", fill="#334155"))
    pieces.append(_text(chart_x, chart_y - 26, "Gap, log-scaled", size=14, weight="700", fill="#334155"))
    pieces.append(_text(chart_x + chart_width + 34, chart_y - 26, "Lower structure", size=14, weight="700", fill="#334155"))
    for index, row in enumerate(model_outputs):
        y = chart_y + index * row_height
        backend = str(row.get("backend", "unknown"))
        gap = float(row.get("gap_kj_mol_per_formula_unit", 0.0))
        flags = ", ".join(row.get("diagnostic_flags", [])) or "none"
        lower = str(row.get("lower_structure", "unknown"))
        bar_width = math.log10(gap + 1.0) / max_log * chart_width if max_log else 0.0
        color = "#2563eb" if lower == case.get("model_lower_energy_structure") else "#f59e0b"
        pieces.append(_line(50, y - 30, width - 58, y - 30, stroke="#e5e7eb", width=1))
        pieces.append(_text(56, y + 5, backend, size=18, weight="700", fill="#111827"))
        pieces.append(_text(56, y + 30, f"flags: {flags}", size=12, fill="#64748b"))
        pieces.append(_rect(chart_x, y - 18, chart_width, 26, fill="#e5e7eb", stroke="none", radius=4))
        pieces.append(_rect(chart_x, y - 18, max(bar_width, 3.0), 26, fill=color, stroke="none", radius=4))
        pieces.append(_text(chart_x + 10, y + 1, f"{gap:.3f} kJ/mol/f.u.", size=12, weight="700", fill="#111827"))
        pieces.append(_text(chart_x + chart_width + 34, y + 3, lower, size=14, weight="700", fill="#111827"))
    pieces.append(_text(56, height - 72, "Blocked before promotion: source-license review, experimental stability citation, disorder annotation, curator, reviewer.", size=14, fill="#475569"))
    pieces.append(_text(56, height - 42, "No raw or coordinate-bearing CPOSS/CCDC/CSD artifact is embedded in this public figure.", size=14, fill="#475569"))
    pieces.append("</svg>")
    return "\n".join(pieces)


def provenance_flow_svg(title: str, steps: list[str], *, width: int = 1100, height: int = 260) -> str:
    """Render a simple left-to-right provenance flow diagram."""

    margin = 44
    box_width = 190
    box_height = 74
    gap = (width - 2 * margin - len(steps) * box_width) / max(len(steps) - 1, 1)
    y = 116
    pieces = [_svg_open(width, height), _title(title, width)]
    for index, step in enumerate(steps):
        x = margin + index * (box_width + gap)
        pieces.append(_rect(x, y, box_width, box_height, fill="#eef2ff", stroke="#334155"))
        pieces.extend(_wrapped_text(step, x + 16, y + 28, max_chars=20, fill="#111827"))
        if index < len(steps) - 1:
            arrow_y = y + box_height / 2
            start = x + box_width + 8
            end = x + box_width + gap - 8
            pieces.append(_line(start, arrow_y, end, arrow_y, stroke="#475569", width=2))
            pieces.append(_polygon([(end, arrow_y), (end - 10, arrow_y - 6), (end - 10, arrow_y + 6)], fill="#475569"))
    pieces.append("</svg>")
    return "\n".join(pieces)


def backend_measurement_svg(report: dict[str, Any], *, width: int = 900, height: int = 420) -> str:
    """Render backend energy and force diagnostics for one case-study report."""

    rows = report["backend_predictions"]
    bars = [
        {"label": row["backend"], "value": float(row["max_force_ev_per_ang"]), "color": "#2563eb"}
        for row in rows
    ]
    pieces = [_svg_open(width, height), _title("AMPETP backend force diagnostics", width)]
    pieces.extend(_horizontal_bars(bars, x=220, y=100, width=560, row_height=54, value_suffix=" eV/Ang"))
    pieces.append(_text(42, height - 42, "Energy values are recorded in the report; force bars compare local diagnostic intensity.", size=16, fill="#475569"))
    pieces.append("</svg>")
    return "\n".join(pieces)


def medication_case_study_svg(report: dict[str, Any], *, width: int = 1100, height: int = 520) -> str:
    """Render medication measurement coverage for the fingerprint paper."""

    rows = []
    for target in report.get("targets", []):
        measured = sum(1 for block in target.get("blocks", []) if block.get("measured_backend_count", 0) > 0)
        pending = sum(
            1
            for block in target.get("blocks", [])
            for backend in block.get("backend_measurements", [])
            if str(backend.get("status", "")).startswith("pending_")
        )
        rows.append(
            {
                "label": str(target.get("name")),
                "measured": measured,
                "pending": pending,
                "blocks": len(target.get("blocks", [])),
            }
        )
    max_value = max((row["blocks"] for row in rows), default=1)
    pieces = [_svg_open(width, height), _title("Medication local measurement case studies", width)]
    pieces.append(_text(56, 88, "Local-only CCDC/CSD-derived CIFs; measurements are backend-behaviour evidence, not stability claims.", size=15, fill="#475569"))
    chart_x = 360
    chart_y = 132
    chart_width = 560
    row_height = 84
    for index, row in enumerate(rows):
        y = chart_y + index * row_height
        measured_width = row["measured"] / max_value * chart_width
        pending_width = row["pending"] / max_value * chart_width
        pieces.append(_text(56, y + 24, row["label"], size=18, weight="700", fill="#111827"))
        pieces.append(_text(56, y + 50, f"{row['measured']} measured blocks; {row['pending']} pending backend runs", size=14, fill="#475569"))
        pieces.append(_rect(chart_x, y, chart_width, 26, fill="#e5e7eb", stroke="none", radius=3))
        pieces.append(_rect(chart_x, y, measured_width, 26, fill="#2563eb", stroke="none", radius=3))
        if pending_width:
            pieces.append(_rect(chart_x, y + 34, pending_width, 18, fill="#f59e0b", stroke="none", radius=3))
        pieces.append(_text(chart_x + chart_width + 18, y + 20, f"{row['blocks']} selected", size=14, fill="#111827"))
    legend_y = height - 70
    pieces.append(_rect(56, legend_y - 14, 22, 14, fill="#2563eb", stroke="none", radius=2))
    pieces.append(_text(88, legend_y, "Measured selected blocks", size=14, fill="#111827"))
    pieces.append(_rect(286, legend_y - 14, 22, 14, fill="#f59e0b", stroke="none", radius=2))
    pieces.append(_text(318, legend_y, "Pending backend runs", size=14, fill="#111827"))
    pieces.append("</svg>")
    return "\n".join(pieces)


def medication_stereochemistry_svg(report: dict[str, Any], *, width: int = 1100, height: int = 520) -> str:
    """Render medication stereochemistry scope as a fingerprint-paper figure."""

    rows = list(report.get("targets", []))
    max_blocks = max((int(row.get("enantiomer_labeled_block_count", 0)) for row in rows), default=1)
    pieces = [_svg_open(width, height), _title("Medication stereochemistry claim scopes", width)]
    pieces.append(_text(56, 88, "S/R evidence is separated from polymorph benchmark claims and kept behind evidence gates.", size=15, fill="#475569"))
    chart_x = 380
    chart_y = 132
    chart_width = 500
    row_height = 86
    for index, row in enumerate(rows):
        y = chart_y + index * row_height
        sr_count = int(row.get("enantiomer_labeled_block_count", 0))
        bar_width = sr_count / max(max_blocks, 1) * chart_width
        scopes = ", ".join(row.get("claim_scopes", [])) or "none"
        status = str(row.get("stereochemistry_status", "unknown"))
        color = "#7c3aed" if sr_count else "#64748b"
        pieces.append(_text(56, y + 22, str(row.get("target", "unknown")), size=18, weight="700", fill="#111827"))
        pieces.append(_text(56, y + 48, status.replace("_", " "), size=14, fill="#475569"))
        pieces.append(_rect(chart_x, y, chart_width, 26, fill="#e5e7eb", stroke="none", radius=3))
        pieces.append(_rect(chart_x, y, bar_width, 26, fill=color, stroke="none", radius=3))
        pieces.append(_text(chart_x + chart_width + 18, y + 20, f"{sr_count} S/R blocks", size=14, fill="#111827"))
        pieces.extend(_wrapped_text(scopes, chart_x, y + 52, max_chars=64, fill="#334155", size=13))
    legend_y = height - 66
    pieces.append(_rect(56, legend_y - 14, 22, 14, fill="#7c3aed", stroke="none", radius=2))
    pieces.append(_text(88, legend_y, "Enantiomer-labeled blocks", size=14, fill="#111827"))
    pieces.append(_text(330, legend_y, "Model rankings remain inspection evidence until stereochemical scope is curated.", size=14, fill="#475569"))
    pieces.append("</svg>")
    return "\n".join(pieces)


def sensitivity_delta_svg(summary: dict[str, Any], *, width: int = 1150, height: int = 620) -> str:
    """Render signed sensitivity energy deltas for all backends."""

    rows = []
    colors = {"mace": "#2563eb", "aimnet2": "#dc2626"}
    for backend, data in summary["backends"].items():
        for variant in data["variants"]:
            if variant["variant"] == summary["reference_variant"]:
                continue
            rows.append(
                {
                    "label": f"{backend}: {variant['variant']}",
                    "value": float(variant["energy_delta_ev"]),
                    "color": colors.get(backend, "#475569"),
                }
            )
    max_abs = max(abs(row["value"]) for row in rows) if rows else 1.0
    pieces = [_svg_open(width, height), _title("AMPETP perturbation sensitivity", width)]
    chart_x = 420
    chart_y = 88
    chart_width = 640
    axis_x = chart_x + chart_width / 2
    pieces.append(_line(axis_x, chart_y - 18, axis_x, chart_y + len(rows) * 42 + 8, stroke="#0f172a", width=1.5))
    for index, row in enumerate(rows):
        y = chart_y + index * 42
        half = chart_width / 2
        bar_width = abs(row["value"]) / max_abs * (half - 26)
        if row["value"] >= 0:
            x = axis_x
        else:
            x = axis_x - bar_width
        pieces.append(_text(32, y + 17, row["label"], size=13, fill="#111827"))
        pieces.append(_rect(x, y, bar_width, 22, fill=row["color"], stroke="none", radius=2))
        value_x = x + bar_width + 8 if row["value"] >= 0 else x - 72
        pieces.append(_text(value_x, y + 16, f"{row['value']:.3f}", size=12, fill="#111827"))
    pieces.append(_text(axis_x - 22, chart_y + len(rows) * 42 + 38, "0 eV", size=13, fill="#0f172a"))
    pieces.append(_text(40, height - 36, "Deltas are relative to each backend's own AMPETP reference prediction.", size=16, fill="#475569"))
    pieces.append("</svg>")
    return "\n".join(pieces)


def guardrail_svg(title: str, supported: list[str], blocked: list[str], *, width: int = 1000, height: int = 520) -> str:
    """Render supported and unsupported claim boundaries."""

    pieces = [_svg_open(width, height), _title(title, width)]
    pieces.append(_rect(52, 92, 420, 350, fill="#ecfdf5", stroke="#047857"))
    pieces.append(_rect(528, 92, 420, 350, fill="#fff7ed", stroke="#c2410c"))
    pieces.append(_text(78, 132, "Supported claims", size=24, weight="700", fill="#064e3b"))
    pieces.append(_text(554, 132, "Blocked claims", size=24, weight="700", fill="#7c2d12"))
    for index, item in enumerate(supported):
        pieces.extend(_wrapped_text(f"- {item}", 78, 174 + index * 58, max_chars=48, fill="#064e3b", size=15))
    for index, item in enumerate(blocked):
        pieces.extend(_wrapped_text(f"- {item}", 554, 174 + index * 58, max_chars=48, fill="#7c2d12", size=15))
    pieces.append("</svg>")
    return "\n".join(pieces)


def structure_projection_svg(atoms: Any, *, title: str = "AMPETP crystal projection", width: int = 900, height: int = 760) -> str:
    """Render a deterministic 2D projection of an ASE Atoms crystal."""

    symbols = list(atoms.get_chemical_symbols())
    positions = [[float(value) for value in row[:2]] for row in atoms.get_positions()]
    cell = atoms.cell.array
    cell_points = [
        (0.0, 0.0),
        (float(cell[0][0]), float(cell[0][1])),
        (float(cell[0][0] + cell[1][0]), float(cell[0][1] + cell[1][1])),
        (float(cell[1][0]), float(cell[1][1])),
    ]
    all_points = positions + [list(point) for point in cell_points]
    transform = _point_transform(all_points, width=width, height=height, top=92, bottom=112, left=70, right=250)
    pieces = [_svg_open(width, height), _title(title, width)]
    pieces.append(_text(54, 88, f"Formula: {atoms.get_chemical_formula()} | Atoms: {len(atoms)}", size=16, fill="#475569"))

    projected_cell = [transform(point[0], point[1]) for point in cell_points]
    pieces.append(_polyline(projected_cell + [projected_cell[0]], stroke="#0f172a", width=2.0, fill="none"))

    bonds = _projected_bonds(atoms)
    for left, right in bonds:
        x1, y1 = transform(positions[left][0], positions[left][1])
        x2, y2 = transform(positions[right][0], positions[right][1])
        pieces.append(_line(x1, y1, x2, y2, stroke="#cbd5e1", width=1.0))

    for index in sorted(range(len(symbols)), key=lambda item: _element_radius(symbols[item]), reverse=True):
        x, y = transform(positions[index][0], positions[index][1])
        symbol = symbols[index]
        pieces.append(_circle(x, y, _element_radius(symbol), fill=_element_color(symbol), stroke="#1f2937"))

    legend_x = width - 200
    pieces.append(_text(legend_x, 122, "Elements", size=19, weight="700", fill="#111827"))
    for offset, symbol in enumerate(sorted(set(symbols), key=lambda item: (item != "C", item))):
        y = 158 + offset * 34
        pieces.append(_circle(legend_x + 10, y - 5, _element_radius(symbol), fill=_element_color(symbol), stroke="#1f2937"))
        pieces.append(_text(legend_x + 32, y, f"{symbol} ({symbols.count(symbol)})", size=15, fill="#111827"))
    pieces.append(_text(54, height - 46, "2D x/y projection for documentation; use the CIF for quantitative crystallographic analysis.", size=15, fill="#475569"))
    pieces.append("</svg>")
    return "\n".join(pieces)


def _svg_open(width: int, height: int) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">'
        "\n<rect width=\"100%\" height=\"100%\" fill=\"#ffffff\"/>"
    )


def _title(value: str, width: int) -> str:
    return _text(width / 2, 46, value, size=28, weight="700", anchor="middle", fill="#0f172a")


def _horizontal_bars(rows: list[dict[str, Any]], *, x: int, y: int, width: int, row_height: int, value_suffix: str) -> list[str]:
    max_value = max(float(row["value"]) for row in rows) if rows else 1.0
    pieces: list[str] = []
    for index, row in enumerate(rows):
        row_y = y + index * row_height
        value = float(row["value"])
        bar_width = value / max_value * width if max_value else 0
        pieces.append(_text(52, row_y + 22, str(row["label"]), size=18, weight="700", fill="#111827"))
        pieces.append(_rect(x, row_y, width, 26, fill="#e5e7eb", stroke="none", radius=3))
        pieces.append(_rect(x, row_y, bar_width, 26, fill=row["color"], stroke="none", radius=3))
        pieces.append(_text(x + width + 18, row_y + 20, f"{value:.3f}{value_suffix}", size=15, fill="#111827"))
    return pieces


def _wrapped_text(value: str, x: float, y: float, *, max_chars: int, fill: str, size: int = 16) -> list[str]:
    words = value.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return [_text(x, y + index * (size + 6), line, size=size, fill=fill) for index, line in enumerate(lines)]


def _text(x: float, y: float, value: str, *, size: int, fill: str, weight: str = "400", anchor: str = "start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">'
        f"{html.escape(value)}</text>"
    )


def _rect(x: float, y: float, width: float, height: float, *, fill: str, stroke: str, radius: int = 8) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def _line(x1: float, y1: float, x2: float, y2: float, *, stroke: str, width: float) -> str:
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"/>'


def _polygon(points: list[tuple[float, float]], *, fill: str) -> str:
    joined = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{joined}" fill="{fill}"/>'


def _polyline(points: list[tuple[float, float]], *, stroke: str, width: float, fill: str) -> str:
    joined = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{joined}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def _circle(x: float, y: float, radius: float, *, fill: str, stroke: str) -> str:
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="0.8"/>'


def _point_transform(points: list[list[float]], *, width: int, height: int, top: int, bottom: int, left: int, right: int):
    min_x = min(point[0] for point in points)
    max_x = max(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)
    span_x = max(max_x - min_x, 1e-9)
    span_y = max(max_y - min_y, 1e-9)
    scale = min((width - left - right) / span_x, (height - top - bottom) / span_y)

    def transform(x: float, y: float) -> tuple[float, float]:
        draw_x = left + (x - min_x) * scale
        draw_y = height - bottom - (y - min_y) * scale
        return draw_x, draw_y

    return transform


def _projected_bonds(atoms: Any, *, cutoff_scale: float = 1.22) -> list[tuple[int, int]]:
    try:
        from ase.data import covalent_radii
    except Exception:
        return []
    distances = atoms.get_all_distances(mic=False)
    numbers = atoms.get_atomic_numbers()
    bonds: list[tuple[int, int]] = []
    for left in range(len(atoms)):
        for right in range(left + 1, len(atoms)):
            radius_sum = float(covalent_radii[numbers[left]] + covalent_radii[numbers[right]])
            if radius_sum <= 0:
                continue
            distance = float(distances[left][right])
            if 0 < distance / radius_sum <= cutoff_scale:
                bonds.append((left, right))
    return bonds


def _claim_status_color(label: str) -> str:
    return {
        "candidate": "#f59e0b",
        "reviewed": "#2563eb",
        "verified": "#16a34a",
    }.get(label, "#64748b")


def _claim_short_status(label: str) -> str:
    return {
        "candidate": "workflow smoke only",
        "reviewed": "internal analysis",
        "verified": "headline claims allowed",
    }.get(label, "unknown")


def _status_pill(x: float, y: float, label: str, *, fill: str, stroke: str, text_fill: str) -> str:
    width = max(54, len(label) * 7 + 22)
    return "\n".join(
        [
            _rect(x, y, width, 24, fill=fill, stroke=stroke, radius=12),
            _text(x + width / 2, y + 17, label, size=12, weight="700", fill=text_fill, anchor="middle"),
        ]
    )


def _smoke_fill(status: str) -> str:
    if status == "passed":
        return "#dcfce7"
    if status in {"failed", "timeout"}:
        return "#fee2e2"
    if status in {"not_implemented", "skipped"}:
        return "#fef3c7"
    return "#f1f5f9"


def _smoke_stroke(status: str) -> str:
    if status == "passed":
        return "#16a34a"
    if status in {"failed", "timeout"}:
        return "#dc2626"
    if status in {"not_implemented", "skipped"}:
        return "#d97706"
    return "#94a3b8"


def _smoke_text(status: str) -> str:
    if status == "passed":
        return "#166534"
    if status in {"failed", "timeout"}:
        return "#991b1b"
    if status in {"not_implemented", "skipped"}:
        return "#92400e"
    return "#475569"


def _plot_area(*, width: int, height: int, left: int, right: int, top: int, bottom: int) -> dict[str, float]:
    return {
        "x": float(left),
        "y": float(top),
        "width": float(width - left - right),
        "height": float(height - top - bottom),
    }


def _append_axes(pieces: list[str], plot: dict[str, float], *, x_label: str, y_label: str) -> None:
    x = plot["x"]
    y = plot["y"]
    width = plot["width"]
    height = plot["height"]
    pieces.append(_line(x, y + height, x + width, y + height, stroke="#0f172a", width=1.6))
    pieces.append(_line(x, y, x, y + height, stroke="#0f172a", width=1.6))
    for index in range(6):
        ratio = index / 5
        tick_x = x + ratio * width
        tick_y = y + height - ratio * height
        pieces.append(_line(tick_x, y + height, tick_x, y + height + 6, stroke="#0f172a", width=1))
        pieces.append(_line(x - 6, tick_y, x, tick_y, stroke="#0f172a", width=1))
        pieces.append(_text(tick_x, y + height + 24, f"{ratio:.1f}", size=11, fill="#475569", anchor="middle"))
        pieces.append(_text(x - 12, tick_y + 4, f"{ratio:.1f}", size=11, fill="#475569", anchor="end"))
        if index not in {0, 5}:
            pieces.append(_line(tick_x, y, tick_x, y + height, stroke="#e5e7eb", width=0.8))
            pieces.append(_line(x, tick_y, x + width, tick_y, stroke="#e5e7eb", width=0.8))
    pieces.append(_text(x + width / 2, y + height + 58, x_label, size=14, fill="#334155", anchor="middle"))
    pieces.append(_text(x - 62, y + height / 2, y_label, size=14, fill="#334155", anchor="middle"))


def _element_color(symbol: str) -> str:
    return {
        "C": "#374151",
        "H": "#f8fafc",
        "N": "#2563eb",
        "O": "#dc2626",
        "P": "#ca8a04",
        "S": "#9333ea",
    }.get(symbol, "#64748b")


def _element_radius(symbol: str) -> float:
    return {
        "H": 3.5,
        "C": 5.2,
        "N": 5.4,
        "O": 5.4,
        "P": 6.3,
        "S": 6.3,
    }.get(symbol, 5.0)
