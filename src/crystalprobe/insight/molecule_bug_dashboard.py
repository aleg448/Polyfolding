"""Joined molecule-level QA dashboard for parser, conformer, and backend status."""

from __future__ import annotations

import json
import math
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


MOLECULE_BUG_DASHBOARD_CLAIM_BOUNDARY = "molecule_bug_dashboard_software_qa_not_scientific_evidence"

DASHBOARD_ROW_COLUMNS = [
    "molecule_id",
    "common_name",
    "source_set",
    "parser_status",
    "conformer_status",
    "backend_status",
    "energy_force_sanity",
    "issue_signature",
    "backend_passed_count",
    "backend_blocked_count",
    "backend_failed_count",
    "energy_ev",
    "max_force_ev_per_ang",
    "review_status",
    "claim_boundary",
    "details_json",
]

ISSUE_SIGNATURE_COLUMNS = [
    "issue_signature",
    "severity",
    "count",
    "example_ids",
    "detail",
]


def molecule_bug_dashboard_report(
    *,
    tentative_benchmark: dict[str, Any],
    backend_ready_inputs: dict[str, Any],
    backend_smoke: dict[str, Any],
    max_force_warning_threshold: float = 50.0,
) -> dict[str, Any]:
    """Join molecule-level software QA state across current reports."""

    molecules = _molecules(tentative_benchmark, backend_ready_inputs)
    benchmark_rows = _rows_by_molecule(tentative_benchmark.get("benchmark_rows", []))
    ready_rows = {row.get("molecule_id", ""): row for row in backend_ready_inputs.get("rows", [])}
    backend_rows = _rows_by_molecule(backend_smoke.get("benchmark_rows", []))
    rows = [
        _dashboard_row(
            molecule,
            benchmark_rows=benchmark_rows.get(molecule["molecule_id"], []),
            ready_row=ready_rows.get(molecule["molecule_id"]),
            backend_rows=backend_rows.get(molecule["molecule_id"], []),
            max_force_warning_threshold=max_force_warning_threshold,
        )
        for molecule in molecules
    ]
    row_issue_counts = Counter(row["issue_signature"] for row in rows)
    parser_counts = Counter(row["parser_status"] for row in rows)
    conformer_counts = Counter(row["conformer_status"] for row in rows)
    backend_counts = Counter(row["backend_status"] for row in rows)
    sanity_counts = Counter(row["energy_force_sanity"] for row in rows)
    signatures = _issue_signatures(rows)
    return {
        "schema_version": "0.1.0",
        "status": "molecule_bug_dashboard_recorded",
        "purpose": (
            "Join molecule parser, conformer, backend execution, and energy/force sanity status into one "
            "software QA dashboard."
        ),
        "claim_boundary": MOLECULE_BUG_DASHBOARD_CLAIM_BOUNDARY,
        "parameters": {
            "max_force_warning_threshold": max_force_warning_threshold,
        },
        "counts": {
            "molecule_count": len(rows),
            "parser_counts": dict(sorted(parser_counts.items())),
            "conformer_counts": dict(sorted(conformer_counts.items())),
            "backend_counts": dict(sorted(backend_counts.items())),
            "energy_force_sanity_counts": dict(sorted(sanity_counts.items())),
            "row_issue_signature_counts": dict(sorted(row_issue_counts.items())),
            "issue_signature_counts": {
                signature["issue_signature"]: signature["count"] for signature in signatures
            },
            "claim_ready_count": 0,
            "issue_signature_count": len(signatures),
        },
        "rows": rows,
        "issue_signatures": signatures,
        "policy": [
            "This dashboard is a software QA artifact for parser, conformer, and backend readiness.",
            "A passed parser or backend smoke row does not make a molecule scientifically verified.",
            "Backend-not-run rows are explicit coverage gaps, not failed chemistry.",
            "Energy/force sanity checks only test finite outputs and coarse force thresholds on generated inputs.",
        ],
    }


def molecule_bug_dashboard_markdown(report: dict[str, Any]) -> str:
    """Render the molecule bug dashboard as Markdown."""

    lines = [
        "# CrystalProbe Molecule Bug Dashboard",
        "",
        f"- Status: `{report['status']}`",
        f"- Molecules: `{report['counts']['molecule_count']}`",
        f"- Claim-ready rows: `{report['counts']['claim_ready_count']}`",
        f"- Claim boundary: `{report['claim_boundary']}`",
        "",
        "## Status Counts",
        "",
        "| Surface | Counts |",
        "|---|---|",
        f"| Parser | {_format_counts(report['counts']['parser_counts'])} |",
        f"| Conformer | {_format_counts(report['counts']['conformer_counts'])} |",
        f"| Backend | {_format_counts(report['counts']['backend_counts'])} |",
        f"| Energy/force sanity | {_format_counts(report['counts']['energy_force_sanity_counts'])} |",
        "",
        "## Issue Signatures",
        "",
        "| Signature | Severity | Count | Examples | Detail |",
        "|---|---|---:|---|---|",
    ]
    for signature in report["issue_signatures"]:
        examples = ", ".join(signature["example_ids"])
        lines.append(
            f"| `{signature['issue_signature']}` | `{signature['severity']}` | "
            f"`{signature['count']}` | {examples} | {signature['detail']} |"
        )
    if not report["issue_signatures"]:
        lines.append("| `none` | `none` | `0` |  | No issue signatures recorded. |")

    lines.extend(
        [
            "",
            "## Molecule Rows",
            "",
            "| Molecule | Parser | Conformer | Backend | Energy/Force | Issue |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in report["rows"][:100]:
        lines.append(
            f"| `{row['molecule_id']}` | `{row['parser_status']}` | `{row['conformer_status']}` | "
            f"`{row['backend_status']}` | `{row['energy_force_sanity']}` | `{row['issue_signature']}` |"
        )

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def write_molecule_bug_dashboard_sqlite(report: dict[str, Any], path: str | Path) -> None:
    """Write molecule dashboard rows and issue signatures to SQLite."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with sqlite3.connect(output) as connection:
        row_columns = ", ".join(f"{column} TEXT" for column in DASHBOARD_ROW_COLUMNS)
        sig_columns = ", ".join(f"{column} TEXT" for column in ISSUE_SIGNATURE_COLUMNS)
        connection.execute(f"CREATE TABLE molecule_bug_dashboard ({row_columns})")
        connection.execute(f"CREATE TABLE issue_signatures ({sig_columns})")
        row_placeholders = ", ".join("?" for _ in DASHBOARD_ROW_COLUMNS)
        sig_placeholders = ", ".join("?" for _ in ISSUE_SIGNATURE_COLUMNS)
        connection.executemany(
            f"INSERT INTO molecule_bug_dashboard ({', '.join(DASHBOARD_ROW_COLUMNS)}) VALUES ({row_placeholders})",
            [_sqlite_row(row, DASHBOARD_ROW_COLUMNS) for row in report["rows"]],
        )
        connection.executemany(
            f"INSERT INTO issue_signatures ({', '.join(ISSUE_SIGNATURE_COLUMNS)}) VALUES ({sig_placeholders})",
            [_sqlite_row(row, ISSUE_SIGNATURE_COLUMNS) for row in report["issue_signatures"]],
        )
        connection.execute("CREATE INDEX idx_molecule_bug_dashboard_molecule ON molecule_bug_dashboard(molecule_id)")
        connection.execute("CREATE INDEX idx_molecule_bug_dashboard_issue ON molecule_bug_dashboard(issue_signature)")
        connection.execute("CREATE INDEX idx_molecule_bug_dashboard_backend ON molecule_bug_dashboard(backend_status)")


def _dashboard_row(
    molecule: dict[str, Any],
    *,
    benchmark_rows: list[dict[str, Any]],
    ready_row: dict[str, Any] | None,
    backend_rows: list[dict[str, Any]],
    max_force_warning_threshold: float,
) -> dict[str, Any]:
    parser_status, parser_signatures = _parser_status(benchmark_rows)
    conformer_status, conformer_signatures = _conformer_status(ready_row)
    backend_status, backend_signatures = _backend_status(backend_rows)
    sanity, sanity_signatures = _energy_force_sanity(
        backend_rows,
        max_force_warning_threshold=max_force_warning_threshold,
    )
    signatures = parser_signatures + conformer_signatures + backend_signatures + sanity_signatures
    issue_signature = ";".join(dict.fromkeys(signature for signature in signatures if signature != "none")) or "none"
    passed_backend_rows = [row for row in backend_rows if row.get("status") == "passed"]
    representative = passed_backend_rows[0] if passed_backend_rows else {}
    details = {
        "parser_rows": _compact_rows(benchmark_rows, {"smiles_lexical", "rdkit_smiles"}),
        "conformer": ready_row or {},
        "backend_rows": backend_rows,
    }
    return {
        "molecule_id": molecule["molecule_id"],
        "common_name": molecule.get("common_name", ""),
        "source_set": molecule.get("source_set", ""),
        "stress_tags": molecule.get("stress_tags", []),
        "parser_status": parser_status,
        "conformer_status": conformer_status,
        "backend_status": backend_status,
        "energy_force_sanity": sanity,
        "issue_signature": issue_signature,
        "backend_passed_count": sum(1 for row in backend_rows if row.get("status") == "passed"),
        "backend_blocked_count": sum(1 for row in backend_rows if row.get("status") == "blocked"),
        "backend_failed_count": sum(1 for row in backend_rows if row.get("status") == "failed"),
        "energy_ev": representative.get("energy_ev"),
        "max_force_ev_per_ang": representative.get("max_force_ev_per_ang"),
        "review_status": "candidate_unverified",
        "claim_boundary": MOLECULE_BUG_DASHBOARD_CLAIM_BOUNDARY,
        "details": details,
        "details_json": json.dumps(details, sort_keys=True),
    }


def _molecules(tentative_benchmark: dict[str, Any], backend_ready_inputs: dict[str, Any]) -> list[dict[str, Any]]:
    molecules = [
        {
            "molecule_id": row.get("molecule_id", ""),
            "common_name": row.get("common_name", ""),
            "source_set": row.get("source_set", ""),
            "stress_tags": row.get("stress_tags", []),
        }
        for row in tentative_benchmark.get("molecules", [])
    ]
    seen = {row["molecule_id"] for row in molecules}
    for row in backend_ready_inputs.get("rows", []):
        molecule_id = row.get("molecule_id", "")
        if molecule_id and molecule_id not in seen:
            seen.add(molecule_id)
            molecules.append(
                {
                    "molecule_id": molecule_id,
                    "common_name": row.get("common_name", ""),
                    "source_set": "backend_ready_inputs",
                    "stress_tags": [],
                }
            )
    return sorted(molecules, key=lambda row: row["molecule_id"])


def _rows_by_molecule(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("molecule_id", "")), []).append(row)
    return grouped


def _parser_status(rows: list[dict[str, Any]]) -> tuple[str, list[str]]:
    parser_rows = [row for row in rows if row.get("tool") in {"smiles_lexical", "rdkit_smiles"}]
    return _status_from_rows(parser_rows, not_recorded_signature="parser_not_recorded")


def _conformer_status(row: dict[str, Any] | None) -> tuple[str, list[str]]:
    if row is None:
        return "not_recorded", ["conformer_not_recorded"]
    status = str(row.get("status", "not_recorded"))
    issue = str(row.get("issue_signature", "none"))
    return status, [issue if issue != "none" else "none"]


def _backend_status(rows: list[dict[str, Any]]) -> tuple[str, list[str]]:
    if not rows:
        return "not_run", ["backend_not_run"]
    statuses = [row.get("status", "") for row in rows]
    signatures = [str(row.get("issue_signature", "none")) for row in rows]
    if "failed" in statuses:
        return "failed", signatures
    if "blocked" in statuses and "passed" in statuses:
        return "partial_backend_blocker", signatures
    if "blocked" in statuses:
        return "blocked", signatures
    if statuses and all(status == "passed" for status in statuses):
        return "passed", signatures
    if "skipped" in statuses:
        return "skipped", signatures
    return "unknown", signatures or ["backend_unknown_status"]


def _energy_force_sanity(
    rows: list[dict[str, Any]],
    *,
    max_force_warning_threshold: float,
) -> tuple[str, list[str]]:
    passed = [row for row in rows if row.get("status") == "passed"]
    if not rows:
        return "not_run", ["energy_force_not_run"]
    if not passed:
        return "blocked" if any(row.get("status") == "blocked" for row in rows) else "not_available", ["none"]
    signatures = []
    for row in passed:
        energy = row.get("energy_ev")
        max_force = row.get("max_force_ev_per_ang")
        mean_force = row.get("mean_force_ev_per_ang")
        if not all(_finite(value) for value in (energy, max_force, mean_force)):
            signatures.append("energy_force_nonfinite")
        elif float(max_force) > max_force_warning_threshold:
            signatures.append("max_force_above_smoke_threshold")
    if signatures:
        return "warning", signatures
    return "passed", ["none"]


def _status_from_rows(rows: list[dict[str, Any]], *, not_recorded_signature: str) -> tuple[str, list[str]]:
    if not rows:
        return "not_recorded", [not_recorded_signature]
    statuses = [row.get("status", "") for row in rows]
    signatures = [str(row.get("issue_signature", "none")) for row in rows]
    if "failed" in statuses:
        return "failed", signatures
    if "blocked" in statuses:
        return "blocked", signatures
    if "warning" in statuses:
        return "warning", signatures
    if statuses and all(status == "passed" for status in statuses):
        return "passed", signatures
    return "unknown", signatures


def _issue_signatures(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for signature in row["issue_signature"].split(";"):
            if signature and signature != "none":
                grouped.setdefault(signature, []).append(row)
    signatures = []
    for signature, group in sorted(grouped.items()):
        signatures.append(
            {
                "issue_signature": signature,
                "severity": _signature_severity(signature),
                "count": len(group),
                "example_ids": [row["molecule_id"] for row in group[:8]],
                "detail": _signature_detail(signature),
            }
        )
    return signatures


def _signature_severity(signature: str) -> str:
    if signature.endswith("_not_run") or signature.endswith("_not_recorded"):
        return "coverage_gap"
    if "blocked" in signature or "missing" in signature or "compiler" in signature:
        return "blocked"
    if "warning" in signature or "not_converged" in signature or "threshold" in signature:
        return "warning"
    if "failed" in signature or "nonfinite" in signature or "exception" in signature:
        return "failure"
    return "info"


def _signature_detail(signature: str) -> str:
    details = {
        "backend_not_run": "No backend smoke row exists for this molecule in the current tiny execution slice.",
        "energy_force_not_run": "No energy/force sanity check exists because no backend row was run.",
        "parser_not_recorded": "Parser rows were not found in the tentative benchmark report.",
        "conformer_not_recorded": "Backend-ready conformer input row was not found for this molecule.",
        "backend_missing_windows_cpp_compiler": (
            "Backend execution reached AIMNet2/PyTorch Inductor, but the Windows C++ compiler `cl` was unavailable."
        ),
        "rdkit_uff_not_converged": "RDKit generated a conformer, but UFF optimization did not converge.",
        "backend_execution_exception": "A backend raised an execution exception on this generated input.",
        "max_force_above_smoke_threshold": "A passed backend row returned a maximum force above the smoke sanity threshold.",
    }
    return details.get(signature, "Issue propagated from parser, conformer, backend, or sanity report.")


def _compact_rows(rows: list[dict[str, Any]], tools: set[str]) -> list[dict[str, Any]]:
    compact = []
    for row in rows:
        if row.get("tool") not in tools:
            continue
        compact.append(
            {
                "tool": row.get("tool", ""),
                "status": row.get("status", ""),
                "issue_signature": row.get("issue_signature", ""),
                "detail": row.get("detail", ""),
            }
        )
    return compact


def _format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"`{key}`: `{value}`" for key, value in sorted(counts.items())) or "`none`"


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
