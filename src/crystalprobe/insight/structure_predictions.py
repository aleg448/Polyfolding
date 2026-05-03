"""Analysis helpers for source-level structure prediction JSONL files."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

FORMULA_TOKEN = re.compile(r"([A-Z][a-z]?)(\d*)")
EV_TO_KJ_MOL = 96.48533212331002


def parse_formula_counts(formula: str) -> dict[str, int]:
    """Parse a compact chemical formula such as C52H72O8."""

    counts: dict[str, int] = {}
    consumed = ""
    for match in FORMULA_TOKEN.finditer(formula):
        element = match.group(1)
        count = int(match.group(2) or "1")
        counts[element] = counts.get(element, 0) + count
        consumed += match.group(0)
    if consumed != formula:
        raise ValueError(f"unsupported formula format: {formula}")
    return counts


def formula_from_counts(counts: dict[str, int]) -> str:
    """Serialize formula counts in Hill-style order for organic molecules."""

    keys = list(counts)
    if "C" in counts:
        order = ["C"]
        if "H" in counts:
            order.append("H")
        order.extend(sorted(key for key in keys if key not in {"C", "H"}))
    else:
        order = sorted(keys)
    return "".join(f"{element}{'' if counts[element] == 1 else counts[element]}" for element in order)


def infer_common_formula_unit(formulas: Iterable[str]) -> dict[str, int]:
    """Infer a common formula unit from a family of same-molecule structures."""

    parsed = [parse_formula_counts(formula) for formula in formulas]
    if not parsed:
        raise ValueError("cannot infer formula unit from no formulas")
    elements = set(parsed[0])
    if any(set(row) != elements for row in parsed):
        raise ValueError("cannot infer formula unit across different element sets")

    unit: dict[str, int] = {}
    for element in sorted(elements):
        unit[element] = math.gcd(*(row[element] for row in parsed))
    return unit


def formula_unit_count(formula: str, formula_unit: dict[str, int]) -> int:
    """Return how many common formula units are present in a structure formula."""

    counts = parse_formula_counts(formula)
    ratios = []
    for element, unit_count in formula_unit.items():
        if unit_count <= 0 or counts[element] % unit_count != 0:
            raise ValueError(f"{formula} is not an integer multiple of {formula_from_counts(formula_unit)}")
        ratios.append(counts[element] // unit_count)
    if len(set(ratios)) != 1:
        raise ValueError(f"{formula} has inconsistent formula-unit ratios")
    return ratios[0]


def load_structure_prediction_rows(path: str | Path) -> list[dict[str, Any]]:
    """Load source-level structure prediction JSONL rows."""

    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            row = json.loads(stripped)
            required = {"block_id", "family_code", "formula", "energy_ev"}
            missing = required - set(row)
            if missing:
                raise ValueError(f"{path}:{line_number}: missing required fields {sorted(missing)}")
            rows.append(row)
    return rows


def summarize_relative_structure_energies(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Normalize structure energies by inferred formula unit and rank by family."""

    input_rows = list(rows)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in input_rows:
        grouped.setdefault(str(row["family_code"]), []).append(row)

    families: dict[str, Any] = {}
    for family, family_rows in sorted(grouped.items()):
        formula_unit = infer_common_formula_unit(str(row["formula"]) for row in family_rows)
        normalized_rows = []
        for row in family_rows:
            unit_count = formula_unit_count(str(row["formula"]), formula_unit)
            energy_per_unit = float(row["energy_ev"]) / unit_count
            normalized_rows.append((row, unit_count, energy_per_unit))
        baseline = min(energy_per_unit for _, _, energy_per_unit in normalized_rows)
        families[family] = {
            "formula_unit": formula_from_counts(formula_unit),
            "structures": [
                {
                    "block_id": row["block_id"],
                    "formula": row["formula"],
                    "formula_unit_count": unit_count,
                    "energy_ev_per_formula_unit": energy_per_unit,
                    "relative_kj_mol_per_formula_unit": (energy_per_unit - baseline) * EV_TO_KJ_MOL,
                    "max_force_ev_per_ang": row.get("force_summary", {}).get("max_force_ev_per_ang"),
                    "local_diagnostic_flags": row.get("local_geometry", {}).get("diagnostic_flags", []),
                    "top_force_hotspot": (row.get("local_geometry", {}).get("force_hotspots") or [None])[0],
                    "top_bond_geometry_outlier": (row.get("local_geometry", {}).get("bond_geometry_outliers") or [None])[0],
                    "top_short_contact": (row.get("local_geometry", {}).get("short_contacts") or [None])[0],
                }
                for row, unit_count, energy_per_unit in sorted(normalized_rows, key=lambda item: item[2])
            ],
        }
    return {
        "families": families,
        "rows": len(input_rows),
    }
