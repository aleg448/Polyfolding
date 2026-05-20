"""Software stress database for molecule-level bug hunting."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


BUG_HUNT_TABLE_COLUMNS = [
    "molecule_id",
    "common_name",
    "smiles",
    "stress_tags",
    "expected_bug_surfaces",
    "component_count",
    "has_charge",
    "has_stereochemistry",
    "has_aromatic_tokens",
    "has_ring_digits",
    "is_large_string",
    "duplicate_smiles_group",
    "claim_boundary",
]


def molecule_bug_hunt_report(catalog: dict[str, Any]) -> dict[str, Any]:
    """Summarize a molecule stress catalog for parser/database QA."""

    molecules = [_molecule_row(row) for row in catalog.get("molecules", [])]
    duplicate_groups = _duplicate_groups(molecules)
    for row in molecules:
        group = duplicate_groups.get(row["smiles"])
        row["duplicate_smiles_group"] = "; ".join(group) if group and len(group) > 1 else ""

    tag_counts = Counter(tag for row in catalog.get("molecules", []) for tag in row.get("stress_tags", []))
    surface_counts = Counter(
        surface for row in catalog.get("molecules", []) for surface in row.get("expected_bug_surfaces", [])
    )
    coverage_checks = _coverage_checks(tag_counts, surface_counts, molecules)
    blocked = [check for check in coverage_checks if check["status"] == "blocked"]
    return {
        "schema_version": "0.1.0",
        "status": "molecule_bug_hunt_ready" if not blocked else "molecule_bug_hunt_needs_more_coverage",
        "purpose": catalog.get("purpose"),
        "molecule_count": len(molecules),
        "tag_counts": dict(sorted(tag_counts.items())),
        "bug_surface_counts": dict(sorted(surface_counts.items())),
        "coverage_checks": coverage_checks,
        "molecules": molecules,
        "policy": list(catalog.get("policy", [])),
    }


def molecule_bug_hunt_markdown(report: dict[str, Any]) -> str:
    """Render the molecule bug-hunt database summary."""

    lines = [
        "# CrystalProbe Molecule Bug-Hunt Database",
        "",
        f"- Status: `{report['status']}`",
        f"- Molecules: `{report['molecule_count']}`",
        "",
        "## Coverage Checks",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for check in report["coverage_checks"]:
        lines.append(f"| `{check['check']}` | `{check['status']}` | {check['detail']} |")
    lines.extend(
        [
            "",
            "## Molecules",
            "",
            "| Molecule | SMILES | Tags | Bug Surfaces | Flags | Claim Boundary |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in report["molecules"]:
        flags = _flag_summary(row)
        lines.append(
            f"| {row['common_name']} | `{row['smiles']}` | {row['stress_tags']} | "
            f"{row['expected_bug_surfaces']} | {flags} | `{row['claim_boundary']}` |"
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report.get("policy", []))
    return "\n".join(lines).rstrip() + "\n"


def write_molecule_bug_hunt_sqlite(report: dict[str, Any], path: str | Path) -> None:
    """Write molecule bug-hunt rows to SQLite."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with sqlite3.connect(output) as connection:
        columns = ", ".join(f"{column} TEXT" for column in BUG_HUNT_TABLE_COLUMNS)
        connection.execute(f"CREATE TABLE molecule_stress_cases ({columns})")
        placeholders = ", ".join("?" for _ in BUG_HUNT_TABLE_COLUMNS)
        connection.executemany(
            f"INSERT INTO molecule_stress_cases ({', '.join(BUG_HUNT_TABLE_COLUMNS)}) VALUES ({placeholders})",
            [_sqlite_row(row) for row in report["molecules"]],
        )
        connection.execute("CREATE INDEX idx_molecule_stress_tags ON molecule_stress_cases(stress_tags)")
        connection.execute("CREATE INDEX idx_molecule_stress_smiles ON molecule_stress_cases(smiles)")


def _molecule_row(row: dict[str, Any]) -> dict[str, Any]:
    smiles = str(row["smiles"])
    return {
        "molecule_id": row["molecule_id"],
        "common_name": row["common_name"],
        "smiles": smiles,
        "stress_tags": "; ".join(row.get("stress_tags", [])),
        "expected_bug_surfaces": "; ".join(row.get("expected_bug_surfaces", [])),
        "component_count": smiles.count(".") + 1,
        "has_charge": "+" in smiles or "-" in smiles,
        "has_stereochemistry": "@" in smiles or "/" in smiles or "\\" in smiles,
        "has_aromatic_tokens": any(token in smiles for token in ("c", "n", "o", "s")),
        "has_ring_digits": any(character.isdigit() for character in smiles),
        "is_large_string": len(smiles) >= 55,
        "duplicate_smiles_group": "",
        "claim_boundary": "software_stress_fixture_not_scientific_evidence",
    }


def _duplicate_groups(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[row["smiles"]].append(row["molecule_id"])
    return dict(grouped)


def _coverage_checks(
    tag_counts: Counter[str],
    surface_counts: Counter[str],
    molecules: list[dict[str, Any]],
) -> list[dict[str, str]]:
    checks = [
        _check("charged_molecules", tag_counts.get("charged", 0) >= 4, f"{tag_counts.get('charged', 0)} charged rows"),
        _check("salt_or_dot_components", any(row["component_count"] > 1 for row in molecules), "dot components present"),
        _check("stereochemistry", tag_counts.get("chiral", 0) >= 3, f"{tag_counts.get('chiral', 0)} chiral rows"),
        _check("tautomer_cases", tag_counts.get("tautomer", 0) >= 2, f"{tag_counts.get('tautomer', 0)} tautomer rows"),
        _check("large_or_fused_cases", tag_counts.get("fused_ring", 0) >= 4, f"{tag_counts.get('fused_ring', 0)} fused-ring rows"),
        _check(
            "duplicate_connectivity_cases",
            any(row["duplicate_smiles_group"] for row in molecules),
            "duplicate SMILES group present",
        ),
        _check(
            "expected_bug_surface_diversity",
            len(surface_counts) >= 20,
            f"{len(surface_counts)} expected bug-surface labels",
        ),
    ]
    return checks


def _check(name: str, passed: bool, detail: str) -> dict[str, str]:
    return {"check": name, "status": "passed" if passed else "blocked", "detail": detail}


def _flag_summary(row: dict[str, Any]) -> str:
    flags = []
    if row["component_count"] > 1:
        flags.append("dot-components")
    if row["has_charge"]:
        flags.append("charged")
    if row["has_stereochemistry"]:
        flags.append("stereo")
    if row["is_large_string"]:
        flags.append("large")
    if row["duplicate_smiles_group"]:
        flags.append("duplicate-connectivity")
    return ", ".join(flags) or "baseline"


def _sqlite_row(row: dict[str, Any]) -> tuple[Any, ...]:
    values = []
    for column in BUG_HUNT_TABLE_COLUMNS:
        value = row[column]
        if isinstance(value, bool):
            values.append("true" if value else "false")
        else:
            values.append(str(value))
    return tuple(values)
