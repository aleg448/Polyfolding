"""Backend-ready generated-conformer input manifests."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


BACKEND_READY_CLAIM_BOUNDARY = "backend_ready_generated_conformer_input_not_scientific_evidence"

BACKEND_READY_ROW_COLUMNS = [
    "molecule_id",
    "common_name",
    "smiles",
    "status",
    "source_status",
    "issue_signature",
    "detail",
    "generator",
    "atom_count",
    "heavy_atom_count",
    "xyz_path",
    "sha256",
    "byte_count",
    "review_status",
    "release_category",
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


def backend_ready_inputs_report(
    conformer_report: dict[str, Any],
    *,
    source_report_path: str | Path | None = None,
    base_dir: str | Path = ".",
) -> dict[str, Any]:
    """Build a hashed manifest for generated conformers that can feed backends."""

    root = Path(base_dir)
    rows = [_input_row(row, root=root) for row in conformer_report.get("rows", [])]
    counts = Counter(row["status"] for row in rows)
    signatures = _bug_signatures(rows)
    return {
        "schema_version": "0.1.0",
        "status": "backend_ready_inputs_recorded",
        "purpose": (
            "Prepare local generated-conformer coordinate files as hashed software-test inputs for optional "
            "scientific backend smoke runs."
        ),
        "source_report": str(source_report_path) if source_report_path is not None else "",
        "source_generator": conformer_report.get("generator", ""),
        "source_claim_boundary": conformer_report.get("claim_boundary", ""),
        "claim_boundary": BACKEND_READY_CLAIM_BOUNDARY,
        "counts": {
            "row_count": len(rows),
            "ready_count": counts.get("ready", 0),
            "warning_count": counts.get("warning", 0),
            "blocked_count": counts.get("blocked", 0),
            "claim_ready_count": 0,
            "bug_signature_count": len(signatures),
        },
        "rows": rows,
        "bug_signatures": signatures,
        "policy": [
            "Generated conformer XYZ files are backend inputs for software smoke tests, not experimental structures.",
            "SHA-256 hashes identify exact local inputs without making them verified scientific evidence.",
            "Warning rows may still be useful for backend robustness checks, but they remain unverified inputs.",
            "No backend-ready input row can support a drug-discovery, stability, or benchmark claim by itself.",
        ],
    }


def backend_ready_inputs_markdown(report: dict[str, Any]) -> str:
    """Render a backend-ready input manifest as Markdown."""

    lines = [
        "# CrystalProbe Backend-Ready Inputs",
        "",
        f"- Status: `{report['status']}`",
        f"- Source report: `{report['source_report'] or 'not_recorded'}`",
        f"- Rows: `{report['counts']['row_count']}`",
        f"- Ready rows: `{report['counts']['ready_count']}`",
        f"- Warning rows: `{report['counts']['warning_count']}`",
        f"- Blocked rows: `{report['counts']['blocked_count']}`",
        f"- Claim-ready rows: `{report['counts']['claim_ready_count']}`",
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
        lines.append("| `none` | `none` | `0` |  | No blocked or warning backend input rows recorded. |")

    lines.extend(
        [
            "",
            "## Input Rows",
            "",
            "| Molecule | Status | Review | Atoms | XYZ | SHA-256 | Detail |",
            "|---|---|---|---:|---|---|---|",
        ]
    )
    for row in report["rows"][:80]:
        digest = row["sha256"][:12] if row["sha256"] else ""
        lines.append(
            f"| `{row['molecule_id']}` | `{row['status']}` | `{row['review_status']}` | "
            f"`{row['atom_count']}` | `{row['xyz_path']}` | `{digest}` | {row['detail']} |"
        )

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def write_backend_ready_inputs_sqlite(report: dict[str, Any], path: str | Path) -> None:
    """Write backend-ready input rows and bug signatures to SQLite."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with sqlite3.connect(output) as connection:
        row_columns = ", ".join(f"{column} TEXT" for column in BACKEND_READY_ROW_COLUMNS)
        sig_columns = ", ".join(f"{column} TEXT" for column in BUG_SIGNATURE_COLUMNS)
        connection.execute(f"CREATE TABLE backend_ready_inputs ({row_columns})")
        connection.execute(f"CREATE TABLE bug_signatures ({sig_columns})")
        row_placeholders = ", ".join("?" for _ in BACKEND_READY_ROW_COLUMNS)
        sig_placeholders = ", ".join("?" for _ in BUG_SIGNATURE_COLUMNS)
        connection.executemany(
            f"INSERT INTO backend_ready_inputs ({', '.join(BACKEND_READY_ROW_COLUMNS)}) VALUES ({row_placeholders})",
            [_sqlite_row(row, BACKEND_READY_ROW_COLUMNS) for row in report["rows"]],
        )
        connection.executemany(
            f"INSERT INTO bug_signatures ({', '.join(BUG_SIGNATURE_COLUMNS)}) VALUES ({sig_placeholders})",
            [_sqlite_row(row, BUG_SIGNATURE_COLUMNS) for row in report["bug_signatures"]],
        )
        connection.execute("CREATE INDEX idx_backend_ready_status ON backend_ready_inputs(status)")
        connection.execute("CREATE INDEX idx_backend_ready_molecule ON backend_ready_inputs(molecule_id)")
        connection.execute("CREATE INDEX idx_backend_ready_hash ON backend_ready_inputs(sha256)")


def _input_row(source: dict[str, Any], *, root: Path) -> dict[str, Any]:
    xyz_path = str(source.get("xyz_path", ""))
    resolved = _resolve_path(xyz_path, root=root)
    source_status = str(source.get("status", ""))
    payload = str(source.get("coordinate_payload", ""))
    status = "blocked"
    issue_signature = str(source.get("issue_signature", "none"))
    detail = str(source.get("detail", ""))
    sha256 = ""
    byte_count = 0

    if source_status not in {"generated", "warning"}:
        issue_signature = issue_signature if issue_signature != "none" else "conformer_not_generated"
        detail = detail or "Source conformer row was not generated."
    elif payload != "written_local_generated_xyz" or not xyz_path:
        issue_signature = "generated_coordinate_payload_missing"
        detail = "Source conformer row exists, but no local XYZ coordinate payload was written."
    elif not resolved.is_file():
        issue_signature = "generated_xyz_file_missing"
        detail = f"Expected local generated XYZ file was not found: {xyz_path}"
    else:
        sha256 = _sha256(resolved)
        byte_count = resolved.stat().st_size
        status = "warning" if source_status == "warning" else "ready"
        if status == "ready":
            issue_signature = "none"
            detail = "Generated conformer XYZ is present and hashable for backend smoke execution."
        else:
            detail = (
                detail
                or "Generated conformer XYZ is present, but the source conformer generator recorded a warning."
            )

    return {
        "molecule_id": str(source.get("molecule_id", "")),
        "common_name": str(source.get("common_name", "")),
        "smiles": str(source.get("smiles", "")),
        "status": status,
        "source_status": source_status,
        "issue_signature": issue_signature,
        "detail": detail,
        "generator": str(source.get("generator", "")),
        "atom_count": int(source.get("atom_count", 0) or 0),
        "heavy_atom_count": int(source.get("heavy_atom_count", 0) or 0),
        "xyz_path": _normalize_path(xyz_path),
        "sha256": sha256,
        "byte_count": byte_count,
        "review_status": "candidate_unverified",
        "release_category": "local_generated_coordinate_input_metadata",
        "claim_boundary": BACKEND_READY_CLAIM_BOUNDARY,
        "metrics": dict(source.get("metrics", {}) or {}),
        "metrics_json": json.dumps(source.get("metrics", {}) or {}, sort_keys=True),
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
        statuses = {row["status"] for row in group}
        severity = "warning" if "warning" in statuses else "blocked"
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


def _resolve_path(value: str, *, root: Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return root / path


def _normalize_path(value: str) -> str:
    return value.replace("\\", "/")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sqlite_row(row: dict[str, Any], columns: list[str]) -> tuple[str, ...]:
    values = []
    for column in columns:
        value = row[column]
        if isinstance(value, (dict, list)):
            values.append(json.dumps(value, sort_keys=True))
        else:
            values.append(str(value))
    return tuple(values)
