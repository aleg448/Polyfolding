"""Optional conformer generation bridge for molecule-panel stress tests."""

from __future__ import annotations

import importlib.util
import json
import math
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from crystalprobe.core.io import atomic_write_text


CONFORMER_CLAIM_BOUNDARY = "generated_conformer_software_fixture_not_scientific_evidence"

CONFORMER_ROW_COLUMNS = [
    "molecule_id",
    "common_name",
    "smiles",
    "status",
    "generator",
    "issue_signature",
    "detail",
    "atom_count",
    "heavy_atom_count",
    "coordinate_payload",
    "xyz_path",
    "claim_boundary",
    "metrics_json",
]

BUG_SIGNATURE_COLUMNS = [
    "issue_signature",
    "severity",
    "count",
    "example_ids",
    "detail",
]


def conformer_generation_report(
    records: Iterable[Any],
    *,
    random_seed: int = 61453,
    max_molecules: int | None = None,
    optimize: bool = True,
    write_xyz_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Generate or preflight conformers for a molecule panel."""

    molecules = list(records)
    if max_molecules is not None:
        molecules = molecules[:max_molecules]

    if importlib.util.find_spec("rdkit") is None:
        rows = [_blocked_row(molecule, "RDKit is not importable in the active Python environment.") for molecule in molecules]
    else:
        rows = _rdkit_conformer_rows(
            molecules,
            random_seed=random_seed,
            optimize=optimize,
            write_xyz_dir=Path(write_xyz_dir) if write_xyz_dir else None,
        )

    counts = Counter(row["status"] for row in rows)
    signatures = _bug_signatures(rows)
    coordinate_payload_enabled = write_xyz_dir is not None
    status = "conformer_generation_recorded"
    if counts.get("generated", 0) == 0 and counts.get("blocked", 0) == len(rows):
        status = "conformer_generation_blocked_missing_dependency"
    if counts.get("failed", 0):
        status = "conformer_generation_found_issues"
    return {
        "schema_version": "0.1.0",
        "status": status,
        "generator": "rdkit_etkdg_v3",
        "claim_boundary": CONFORMER_CLAIM_BOUNDARY,
        "coordinate_payload_enabled": coordinate_payload_enabled,
        "counts": {
            "molecule_count": len(molecules),
            "row_count": len(rows),
            "generated_count": counts.get("generated", 0),
            "blocked_count": counts.get("blocked", 0),
            "failed_count": counts.get("failed", 0),
            "warning_count": counts.get("warning", 0),
            "coordinate_payload_count": sum(
                1 for row in rows if row["coordinate_payload"] == "written_local_generated_xyz"
            ),
            "claim_ready_count": 0,
            "bug_signature_count": len(signatures),
        },
        "parameters": {
            "random_seed": random_seed,
            "max_molecules": max_molecules,
            "optimize": optimize,
            "write_xyz_dir": str(write_xyz_dir) if write_xyz_dir else None,
        },
        "rows": rows,
        "bug_signatures": signatures,
        "policy": [
            "RDKit ETKDG conformers are generated inputs for software testing, not experimental structures.",
            "Generated conformers do not promote candidate molecules to benchmark evidence.",
            "Coordinate payloads are disabled by default and must be explicitly requested for local backend work.",
            "Backend-ready generated conformers still need model, source, and claim-scope validation before scientific use.",
        ],
    }


def conformer_generation_markdown(report: dict[str, Any]) -> str:
    """Render the conformer-generation report."""

    lines = [
        "# CrystalProbe Conformer Generation",
        "",
        f"- Status: `{report['status']}`",
        f"- Molecules: `{report['counts']['molecule_count']}`",
        f"- Generated: `{report['counts']['generated_count']}`",
        f"- Blocked: `{report['counts']['blocked_count']}`",
        f"- Failed: `{report['counts']['failed_count']}`",
        f"- Warnings: `{report['counts']['warning_count']}`",
        f"- Coordinate payload rows: `{report['counts']['coordinate_payload_count']}`",
        f"- Claim-ready rows: `{report['counts']['claim_ready_count']}`",
        f"- Coordinate payload enabled: `{report['coordinate_payload_enabled']}`",
        f"- Claim boundary: `{report['claim_boundary']}`",
        "",
        "## Bug Signatures",
        "",
        "| Signature | Severity | Count | Examples | Detail |",
        "|---|---|---:|---|---|",
    ]
    for signature in report["bug_signatures"]:
        examples = ", ".join(signature["example_ids"])
        lines.append(
            f"| `{signature['issue_signature']}` | `{signature['severity']}` | "
            f"`{signature['count']}` | {examples} | {signature['detail']} |"
        )
    if not report["bug_signatures"]:
        lines.append("| `none` | `none` | `0` |  | No conformer-generation blockers or failures recorded. |")

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Molecule | Status | Atoms | Payload | Signature | Detail |",
            "|---|---|---:|---|---|---|",
        ]
    )
    for row in report["rows"][:60]:
        lines.append(
            f"| `{row['molecule_id']}` | `{row['status']}` | `{row['atom_count']}` | "
            f"`{row['coordinate_payload']}` | `{row['issue_signature']}` | {row['detail']} |"
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def write_conformer_generation_sqlite(report: dict[str, Any], path: str | Path) -> None:
    """Write conformer-generation rows and bug signatures to SQLite."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with sqlite3.connect(output) as connection:
        row_columns = ", ".join(f"{column} TEXT" for column in CONFORMER_ROW_COLUMNS)
        sig_columns = ", ".join(f"{column} TEXT" for column in BUG_SIGNATURE_COLUMNS)
        connection.execute(f"CREATE TABLE conformer_generation_rows ({row_columns})")
        connection.execute(f"CREATE TABLE bug_signatures ({sig_columns})")
        row_placeholders = ", ".join("?" for _ in CONFORMER_ROW_COLUMNS)
        sig_placeholders = ", ".join("?" for _ in BUG_SIGNATURE_COLUMNS)
        connection.executemany(
            f"INSERT INTO conformer_generation_rows ({', '.join(CONFORMER_ROW_COLUMNS)}) VALUES ({row_placeholders})",
            [_sqlite_row(row, CONFORMER_ROW_COLUMNS) for row in report["rows"]],
        )
        connection.executemany(
            f"INSERT INTO bug_signatures ({', '.join(BUG_SIGNATURE_COLUMNS)}) VALUES ({sig_placeholders})",
            [_sqlite_row(row, BUG_SIGNATURE_COLUMNS) for row in report["bug_signatures"]],
        )
        connection.execute("CREATE INDEX idx_conformer_generation_status ON conformer_generation_rows(status)")
        connection.execute("CREATE INDEX idx_conformer_generation_signature ON conformer_generation_rows(issue_signature)")


def xyz_text(symbols: list[str], coordinates: list[tuple[float, float, float]], *, comment: str) -> str:
    """Render one generated conformer as XYZ text."""

    lines = [str(len(symbols)), comment]
    for symbol, coordinate in zip(symbols, coordinates):
        x, y, z = coordinate
        lines.append(f"{symbol} {x:.6f} {y:.6f} {z:.6f}")
    return "\n".join(lines) + "\n"


def _rdkit_conformer_rows(
    molecules: list[Any],
    *,
    random_seed: int,
    optimize: bool,
    write_xyz_dir: Path | None,
) -> list[dict[str, Any]]:
    from rdkit import Chem
    from rdkit.Chem import AllChem

    rows = []
    for index, molecule in enumerate(molecules):
        try:
            mol = Chem.MolFromSmiles(molecule.smiles)
            if mol is None:
                rows.append(_failed_row(molecule, "rdkit_parse_failure", "RDKit returned no molecule for the SMILES string."))
                continue
            mol = Chem.AddHs(mol)
            params = AllChem.ETKDGv3()
            params.randomSeed = int(random_seed + index)
            params.useRandomCoords = True
            embed_code = AllChem.EmbedMolecule(mol, params)
            if embed_code != 0:
                rows.append(
                    _failed_row(
                        molecule,
                        "rdkit_embed_failure",
                        f"RDKit EmbedMolecule returned code {embed_code}.",
                    )
                )
                continue
            optimize_code = None
            if optimize:
                optimize_code = AllChem.UFFOptimizeMolecule(mol, maxIters=200)
            symbols, coordinates = _rdkit_symbols_and_coordinates(mol)
            xyz_path = ""
            coordinate_payload = "not_written"
            if write_xyz_dir is not None:
                write_xyz_dir.mkdir(parents=True, exist_ok=True)
                xyz_path = str(write_xyz_dir / f"{_safe_id(molecule.molecule_id)}.xyz")
                atomic_write_text(
                    xyz_path,
                    xyz_text(symbols, coordinates, comment=f"{molecule.molecule_id} generated by RDKit ETKDGv3"),
                )
                coordinate_payload = "written_local_generated_xyz"
            status = "generated"
            issue_signature = "none"
            detail = "RDKit ETKDGv3 conformer generated."
            if optimize_code not in (None, 0):
                status = "warning"
                issue_signature = "rdkit_uff_not_converged"
                detail = f"Conformer generated, but UFFOptimizeMolecule returned code {optimize_code}."
            rows.append(
                _row(
                    molecule=molecule,
                    status=status,
                    issue_signature=issue_signature,
                    detail=detail,
                    atom_count=len(symbols),
                    heavy_atom_count=sum(1 for symbol in symbols if symbol != "H"),
                    coordinate_payload=coordinate_payload,
                    xyz_path=xyz_path,
                    metrics=_coordinate_metrics(coordinates),
                )
            )
        except Exception as exc:  # pragma: no cover - defensive for optional dependency internals
            rows.append(_failed_row(molecule, "rdkit_conformer_exception", f"{type(exc).__name__}: {exc}"))
    return rows


def _rdkit_symbols_and_coordinates(mol: Any) -> tuple[list[str], list[tuple[float, float, float]]]:
    conformer = mol.GetConformer()
    symbols = []
    coordinates = []
    for atom in mol.GetAtoms():
        position = conformer.GetAtomPosition(atom.GetIdx())
        symbols.append(atom.GetSymbol())
        coordinates.append((float(position.x), float(position.y), float(position.z)))
    return symbols, coordinates


def _coordinate_metrics(coordinates: list[tuple[float, float, float]]) -> dict[str, float]:
    if not coordinates:
        return {"span_x": 0.0, "span_y": 0.0, "span_z": 0.0, "max_radius": 0.0}
    xs, ys, zs = zip(*coordinates)
    return {
        "span_x": max(xs) - min(xs),
        "span_y": max(ys) - min(ys),
        "span_z": max(zs) - min(zs),
        "max_radius": max(math.sqrt(x * x + y * y + z * z) for x, y, z in coordinates),
    }


def _blocked_row(molecule: Any, detail: str) -> dict[str, Any]:
    return _row(
        molecule=molecule,
        status="blocked",
        issue_signature="optional_conformer_generator_missing_dependency",
        detail=detail,
        atom_count=0,
        heavy_atom_count=0,
        coordinate_payload="not_generated",
        xyz_path="",
        metrics={},
    )


def _failed_row(molecule: Any, issue_signature: str, detail: str) -> dict[str, Any]:
    return _row(
        molecule=molecule,
        status="failed",
        issue_signature=issue_signature,
        detail=detail,
        atom_count=0,
        heavy_atom_count=0,
        coordinate_payload="not_generated",
        xyz_path="",
        metrics={},
    )


def _row(
    *,
    molecule: Any,
    status: str,
    issue_signature: str,
    detail: str,
    atom_count: int,
    heavy_atom_count: int,
    coordinate_payload: str,
    xyz_path: str,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "molecule_id": molecule.molecule_id,
        "common_name": molecule.common_name,
        "smiles": molecule.smiles,
        "status": status,
        "generator": "rdkit_etkdg_v3",
        "issue_signature": issue_signature,
        "detail": detail,
        "atom_count": atom_count,
        "heavy_atom_count": heavy_atom_count,
        "coordinate_payload": coordinate_payload,
        "xyz_path": xyz_path,
        "claim_boundary": CONFORMER_CLAIM_BOUNDARY,
        "metrics": metrics,
        "metrics_json": json.dumps(metrics, sort_keys=True),
    }


def _bug_signatures(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        signature = row["issue_signature"]
        if signature == "none":
            continue
        grouped.setdefault(signature, []).append(row)
    signatures = []
    for signature, group in sorted(grouped.items()):
        severity = "failure" if any(row["status"] == "failed" for row in group) else "blocked"
        if any(row["status"] == "warning" for row in group):
            severity = "warning"
        signatures.append(
            {
                "issue_signature": signature,
                "severity": severity,
                "count": len(group),
                "example_ids": [row["molecule_id"] for row in group[:5]],
                "detail": group[0]["detail"],
            }
        )
    return signatures


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "molecule"


def _sqlite_row(row: dict[str, Any], columns: list[str]) -> tuple[str, ...]:
    values = []
    for column in columns:
        value = row[column]
        if isinstance(value, (dict, list)):
            values.append(json.dumps(value, sort_keys=True))
        else:
            values.append(str(value))
    return tuple(values)
