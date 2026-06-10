"""First backend-result table for executed generated-conformer smoke rows."""

from __future__ import annotations

import json
import math
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


BACKEND_RESULT_TABLE_CLAIM_BOUNDARY = "first_backend_result_table_execution_evidence_not_scientific_claim"

RESULT_ROW_COLUMNS = [
    "molecule_id",
    "common_name",
    "backend",
    "status",
    "formula",
    "natoms",
    "energy_ev",
    "max_force_ev_per_ang",
    "mean_force_ev_per_ang",
    "runtime_seconds",
    "model_label",
    "device",
    "input_sha256",
    "issue_signature",
    "interpretation",
    "review_status",
    "claim_boundary",
    "metadata_json",
]


def backend_result_table_report(backend_smoke: dict[str, Any]) -> dict[str, Any]:
    """Extract actual backend execution rows into a small result table."""

    rows = [_result_row(row) for row in backend_smoke.get("benchmark_rows", []) if row.get("status") != "skipped"]
    counts = Counter(row["status"] for row in rows)
    passed = [row for row in rows if row["status"] == "passed"]
    return {
        "schema_version": "0.1.0",
        "status": "first_backend_result_table_recorded",
        "purpose": "Present the first actual generated-conformer backend results with energy/force sanity and claim boundaries.",
        "claim_boundary": BACKEND_RESULT_TABLE_CLAIM_BOUNDARY,
        "source_backend_smoke_status": backend_smoke.get("status", ""),
        "counts": {
            "row_count": len(rows),
            "passed_count": counts.get("passed", 0),
            "blocked_count": counts.get("blocked", 0),
            "failed_count": counts.get("failed", 0),
            "claim_ready_count": 0,
            "finite_result_count": sum(1 for row in passed if _finite(row["energy_ev"]) and _finite(row["max_force_ev_per_ang"])),
        },
        "rows": rows,
        "policy": [
            "This table contains execution evidence on generated conformer inputs, not verified molecular science.",
            "Within-row energy and force values are useful for smoke sanity checks only.",
            "Do not compare absolute energies across backend families as a stability or ranking claim.",
            "Rows stay candidate_unverified until source, calibration, and benchmark-evidence gates are satisfied.",
        ],
    }


def backend_result_table_markdown(report: dict[str, Any]) -> str:
    """Render the backend result table as Markdown."""

    lines = [
        "# CrystalProbe First Backend Result Table",
        "",
        f"- Status: `{report['status']}`",
        f"- Rows: `{report['counts']['row_count']}`",
        f"- Passed rows: `{report['counts']['passed_count']}`",
        f"- Blocked rows: `{report['counts']['blocked_count']}`",
        f"- Failed rows: `{report['counts']['failed_count']}`",
        f"- Claim-ready rows: `{report['counts']['claim_ready_count']}`",
        f"- Claim boundary: `{report['claim_boundary']}`",
        "",
        "## Results",
        "",
        "| Molecule | Backend | Status | Formula | Energy eV | Max force | Mean force | Runtime s | Model | Issue |",
        "|---|---|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| `{row['molecule_id']}` | `{row['backend']}` | `{row['status']}` | `{row['formula']}` | "
            f"`{_format_float(row['energy_ev'])}` | `{_format_float(row['max_force_ev_per_ang'])}` | "
            f"`{_format_float(row['mean_force_ev_per_ang'])}` | `{_format_float(row['runtime_seconds'])}` | "
            f"`{row['model_label']}` | `{row['issue_signature']}` |"
        )

    lines.extend(["", "## Interpretation", ""])
    for row in report["rows"]:
        lines.append(f"- `{row['backend']}:{row['molecule_id']}`: {row['interpretation']}")

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def write_backend_result_table_sqlite(report: dict[str, Any], path: str | Path) -> None:
    """Write backend result rows to SQLite."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with sqlite3.connect(output) as connection:
        row_columns = ", ".join(f"{column} TEXT" for column in RESULT_ROW_COLUMNS)
        connection.execute(f"CREATE TABLE backend_result_rows ({row_columns})")
        placeholders = ", ".join("?" for _ in RESULT_ROW_COLUMNS)
        connection.executemany(
            f"INSERT INTO backend_result_rows ({', '.join(RESULT_ROW_COLUMNS)}) VALUES ({placeholders})",
            [_sqlite_row(row, RESULT_ROW_COLUMNS) for row in report["rows"]],
        )
        connection.execute("CREATE INDEX idx_backend_result_backend ON backend_result_rows(backend)")
        connection.execute("CREATE INDEX idx_backend_result_status ON backend_result_rows(status)")
        connection.execute("CREATE INDEX idx_backend_result_hash ON backend_result_rows(input_sha256)")


def _result_row(row: dict[str, Any]) -> dict[str, Any]:
    metadata = row.get("metrics", {}).get("model_metadata", {}) or {}
    model_label = _model_label(row.get("backend", ""), metadata)
    status = str(row.get("status", ""))
    issue = str(row.get("issue_signature", "none"))
    interpretation = _interpretation(status, row.get("backend", ""), issue)
    return {
        "molecule_id": str(row.get("molecule_id", "")),
        "common_name": str(row.get("common_name", "")),
        "backend": str(row.get("backend", "")),
        "status": status,
        "formula": str(row.get("metrics", {}).get("formula", "")),
        "natoms": row.get("metrics", {}).get("natoms", ""),
        "energy_ev": row.get("energy_ev"),
        "max_force_ev_per_ang": row.get("max_force_ev_per_ang"),
        "mean_force_ev_per_ang": row.get("mean_force_ev_per_ang"),
        "runtime_seconds": row.get("runtime_seconds"),
        "model_label": model_label,
        "device": str(metadata.get("device", "")),
        "input_sha256": str(row.get("input_sha256", "")),
        "issue_signature": issue,
        "interpretation": interpretation,
        "review_status": "candidate_unverified",
        "claim_boundary": BACKEND_RESULT_TABLE_CLAIM_BOUNDARY,
        "metadata": metadata,
        "metadata_json": json.dumps(metadata, sort_keys=True),
    }


def _model_label(backend: str, metadata: dict[str, Any]) -> str:
    if backend == "mace":
        return f"{metadata.get('adapter', 'mace_off')}:{metadata.get('model', '')}".rstrip(":")
    if backend == "aimnet2":
        return f"{metadata.get('adapter', 'aimnet2')}:{metadata.get('model', '')}".rstrip(":")
    if backend == "uma":
        return f"{metadata.get('adapter', 'uma')}:{metadata.get('checkpoint', '')}".rstrip(":")
    return str(metadata.get("adapter", backend))


def _interpretation(status: str, backend: str, issue: str) -> str:
    if status == "passed":
        return (
            f"{backend} executed on a generated conformer and returned finite smoke-test values; "
            "this is execution evidence only."
        )
    if status == "blocked":
        return f"{backend} did not produce a result because `{issue}` blocked execution."
    if status == "failed":
        return f"{backend} execution failed with `{issue}` and needs debugging before larger runs."
    return f"{backend} row has status `{status}` and is not interpretable as a benchmark result."


def _format_float(value: Any) -> str:
    if value in (None, ""):
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _sqlite_row(row: dict[str, Any], columns: list[str]) -> tuple[str, ...]:
    values = []
    for column in columns:
        value = row[column]
        if isinstance(value, (dict, list)):
            values.append(json.dumps(value, sort_keys=True))
        else:
            values.append("" if value is None else str(value))
    return tuple(values)
