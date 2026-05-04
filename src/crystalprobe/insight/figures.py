"""Small SVG figure builders for paper-ready research artifacts."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any


def write_svg(path: str | Path, svg: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8", newline="\n")


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
