"""Small backend smoke benchmarks over generated-conformer inputs."""

from __future__ import annotations

import json
import math
import sqlite3
import time
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from crystalprobe.foundry.adapters import AdapterNotAvailable


BACKEND_SMOKE_CLAIM_BOUNDARY = "backend_smoke_generated_conformer_not_scientific_evidence"

BACKEND_SMOKE_ROW_COLUMNS = [
    "row_id",
    "molecule_id",
    "common_name",
    "backend",
    "status",
    "issue_signature",
    "detail",
    "xyz_path",
    "input_sha256",
    "review_status",
    "energy_ev",
    "max_force_ev_per_ang",
    "mean_force_ev_per_ang",
    "runtime_seconds",
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

PredictionExecutor = Callable[[dict[str, Any], str, dict[str, Any]], dict[str, Any]]


def backend_smoke_report(
    input_manifest: dict[str, Any],
    *,
    backends: list[str] | tuple[str, ...] = ("mace", "aimnet2"),
    limit: int = 1,
    execute: bool = True,
    device: str | None = "cpu",
    executor: PredictionExecutor | None = None,
    backend_options: dict[str, Any] | None = None,
    cache_environment_blockers: bool = True,
) -> dict[str, Any]:
    """Run or record a tiny backend smoke benchmark over generated conformers."""

    options = dict(backend_options or {})
    options["device"] = device
    ready_inputs = [
        row for row in input_manifest.get("rows", []) if row.get("status") in {"ready", "warning"}
    ]
    selected_inputs = ready_inputs if limit <= 0 else ready_inputs[:limit]
    runner = executor or _run_backend_prediction
    rows: list[dict[str, Any]] = []
    backend_blockers: dict[str, dict[str, Any]] = {}
    for input_row in selected_inputs:
        for backend in backends:
            if cache_environment_blockers and backend in backend_blockers:
                rows.append(_cached_backend_blocker_row(input_row, backend, backend_blockers[backend]))
                continue
            row = _backend_row(
                    input_row,
                    backend,
                    execute=execute,
                    executor=runner,
                    options=options,
                )
            rows.append(row)
            if cache_environment_blockers and row["status"] == "blocked" and _is_environment_blocker(row["issue_signature"]):
                backend_blockers[backend] = row

    counts = Counter(row["status"] for row in rows)
    signatures = _bug_signatures(rows)
    status = "backend_smoke_recorded"
    if counts.get("failed", 0):
        status = "backend_smoke_found_failures"
    elif counts.get("blocked", 0):
        status = "backend_smoke_recorded_with_blockers"
    return {
        "schema_version": "0.1.0",
        "status": status,
        "purpose": (
            "Run a small backend smoke benchmark over hashed generated-conformer inputs to expose execution "
            "readiness and backend-specific blockers."
        ),
        "claim_boundary": BACKEND_SMOKE_CLAIM_BOUNDARY,
        "input_manifest_claim_boundary": input_manifest.get("claim_boundary", ""),
        "parameters": {
            "backends": list(backends),
            "limit": limit,
            "execute": execute,
            "device": device,
            "cache_environment_blockers": cache_environment_blockers,
        },
        "counts": {
            "input_rows_available": len(ready_inputs),
            "input_rows_selected": len(selected_inputs),
            "backend_row_count": len(rows),
            "passed_count": counts.get("passed", 0),
            "blocked_count": counts.get("blocked", 0),
            "failed_count": counts.get("failed", 0),
            "skipped_count": counts.get("skipped", 0),
            "warning_count": counts.get("warning", 0),
            "claim_ready_count": 0,
            "bug_signature_count": len(signatures),
            "cached_environment_blocker_count": sum(
                1 for row in rows if row.get("metrics", {}).get("cached_environment_blocker") is True
            ),
        },
        "benchmark_rows": rows,
        "bug_signatures": signatures,
        "policy": [
            "Backend smoke rows prove only that a backend can execute on a generated local input.",
            "Absolute energies from different backends are not commensurate benchmark claims.",
            "Generated conformer smoke results must stay below verified drug-discovery or stability claims.",
            "Blocked backend rows are useful engineering evidence and should be fixed before larger benchmarks.",
            "Repeated environment-level backend blockers may be cached after the first concrete failure to keep all-molecule runs smooth.",
        ],
    }


def backend_smoke_markdown(report: dict[str, Any]) -> str:
    """Render backend-smoke results as Markdown."""

    lines = [
        "# CrystalProbe Backend Smoke Benchmark",
        "",
        f"- Status: `{report['status']}`",
        f"- Backends: `{', '.join(report['parameters']['backends'])}`",
        f"- Selected inputs: `{report['counts']['input_rows_selected']}`",
        f"- Backend rows: `{report['counts']['backend_row_count']}`",
        f"- Passed rows: `{report['counts']['passed_count']}`",
        f"- Blocked rows: `{report['counts']['blocked_count']}`",
        f"- Failed rows: `{report['counts']['failed_count']}`",
        f"- Skipped rows: `{report['counts']['skipped_count']}`",
        f"- Cached environment blockers: `{report['counts'].get('cached_environment_blocker_count', 0)}`",
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
        lines.append("| `none` | `none` | `0` |  | No backend blockers, failures, or warnings recorded. |")

    lines.extend(
        [
            "",
            "## Backend Rows",
            "",
            "| Molecule | Backend | Status | Energy eV | Max force | Runtime s | Signature | Detail |",
            "|---|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in report["benchmark_rows"][:80]:
        energy = _format_float(row["energy_ev"])
        max_force = _format_float(row["max_force_ev_per_ang"])
        runtime = _format_float(row["runtime_seconds"])
        lines.append(
            f"| `{row['molecule_id']}` | `{row['backend']}` | `{row['status']}` | `{energy}` | "
            f"`{max_force}` | `{runtime}` | `{row['issue_signature']}` | {row['detail']} |"
        )

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def write_backend_smoke_sqlite(report: dict[str, Any], path: str | Path) -> None:
    """Write backend-smoke rows and bug signatures to SQLite."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with sqlite3.connect(output) as connection:
        row_columns = ", ".join(f"{column} TEXT" for column in BACKEND_SMOKE_ROW_COLUMNS)
        sig_columns = ", ".join(f"{column} TEXT" for column in BUG_SIGNATURE_COLUMNS)
        connection.execute(f"CREATE TABLE backend_smoke_rows ({row_columns})")
        connection.execute(f"CREATE TABLE bug_signatures ({sig_columns})")
        row_placeholders = ", ".join("?" for _ in BACKEND_SMOKE_ROW_COLUMNS)
        sig_placeholders = ", ".join("?" for _ in BUG_SIGNATURE_COLUMNS)
        connection.executemany(
            f"INSERT INTO backend_smoke_rows ({', '.join(BACKEND_SMOKE_ROW_COLUMNS)}) VALUES ({row_placeholders})",
            [_sqlite_row(row, BACKEND_SMOKE_ROW_COLUMNS) for row in report["benchmark_rows"]],
        )
        connection.executemany(
            f"INSERT INTO bug_signatures ({', '.join(BUG_SIGNATURE_COLUMNS)}) VALUES ({sig_placeholders})",
            [_sqlite_row(row, BUG_SIGNATURE_COLUMNS) for row in report["bug_signatures"]],
        )
        connection.execute("CREATE INDEX idx_backend_smoke_backend ON backend_smoke_rows(backend)")
        connection.execute("CREATE INDEX idx_backend_smoke_status ON backend_smoke_rows(status)")
        connection.execute("CREATE INDEX idx_backend_smoke_input_hash ON backend_smoke_rows(input_sha256)")


def _backend_row(
    input_row: dict[str, Any],
    backend: str,
    *,
    execute: bool,
    executor: PredictionExecutor,
    options: dict[str, Any],
) -> dict[str, Any]:
    started = time.perf_counter()
    if not execute:
        return _row(
            input_row,
            backend,
            status="skipped",
            issue_signature="backend_execution_not_requested",
            detail="Backend execution was not requested; row records selected input/backend pairing only.",
            runtime_seconds=0.0,
        )
    try:
        prediction = executor(input_row, backend, options)
        runtime = time.perf_counter() - started
        energy = float(prediction.get("energy_ev", float("nan")))
        force_summary = prediction.get("force_summary", {}) or {}
        max_force = float(force_summary.get("max_force_ev_per_ang", float("nan")))
        mean_force = float(force_summary.get("mean_force_ev_per_ang", float("nan")))
        metrics = {
            "formula": prediction.get("formula", ""),
            "natoms": prediction.get("natoms", input_row.get("atom_count", 0)),
            "pbc": prediction.get("pbc", []),
            "model_metadata": prediction.get("model_metadata", {}),
        }
        if not all(math.isfinite(value) for value in (energy, max_force, mean_force)):
            return _row(
                input_row,
                backend,
                status="failed",
                issue_signature="backend_prediction_nonfinite",
                detail="Backend returned a non-finite energy or force summary.",
                energy_ev=energy,
                max_force_ev_per_ang=max_force,
                mean_force_ev_per_ang=mean_force,
                runtime_seconds=runtime,
                metrics=metrics,
            )
        return _row(
            input_row,
            backend,
            status="passed",
            issue_signature="none",
            detail="Backend smoke prediction completed on generated conformer input.",
            energy_ev=energy,
            max_force_ev_per_ang=max_force,
            mean_force_ev_per_ang=mean_force,
            runtime_seconds=runtime,
            metrics=metrics,
        )
    except Exception as exc:  # pragma: no cover - exact optional backend failures vary by environment
        runtime = time.perf_counter() - started
        issue_signature, status = _classify_exception(exc)
        return _row(
            input_row,
            backend,
            status=status,
            issue_signature=issue_signature,
            detail=f"{type(exc).__name__}: {_compact_detail(str(exc))}",
            runtime_seconds=runtime,
        )


def _cached_backend_blocker_row(input_row: dict[str, Any], backend: str, cached: dict[str, Any]) -> dict[str, Any]:
    return _row(
        input_row,
        backend,
        status="blocked",
        issue_signature=str(cached["issue_signature"]),
        detail=(
            "Backend execution not retried because this backend already hit an environment-level blocker "
            f"on `{cached['molecule_id']}`: {cached['detail']}"
        ),
        runtime_seconds=0.0,
        metrics={
            "cached_environment_blocker": True,
            "cached_from_row_id": cached["row_id"],
        },
    )


def _run_backend_prediction(input_row: dict[str, Any], backend: str, options: dict[str, Any]) -> dict[str, Any]:
    from ase.io import read

    from crystalprobe.foundry.optional_adapters import AIMNet2Adapter, MACEOffAdapter, UMAAdapter

    atoms = read(str(input_row["xyz_path"]), index=0)
    device = options.get("device")
    adapter_cache = options.setdefault("_adapter_cache", {})
    if backend == "mace":
        key = (backend, str(options.get("mace_model", "small")), device)
        model = adapter_cache.get(key)
        if model is None:
            model = MACEOffAdapter(model=str(options.get("mace_model", "small")), device=device)
            adapter_cache[key] = model
    elif backend == "aimnet2":
        key = (
            backend,
            str(options.get("aimnet_model", "aimnet2")),
            device,
            bool(options.get("aimnet_dispersion", False)),
        )
        model = adapter_cache.get(key)
        if model is None:
            model = AIMNet2Adapter(
                model=str(options.get("aimnet_model", "aimnet2")),
                device=device,
                needs_dispersion=bool(options.get("aimnet_dispersion", False)),
            )
            adapter_cache[key] = model
    elif backend == "uma":
        key = (
            backend,
            str(options.get("uma_checkpoint", "uma-s-1p2")),
            str(options.get("uma_task_name", "omc")),
            device,
        )
        model = adapter_cache.get(key)
        if model is None:
            model = UMAAdapter(
                checkpoint=str(options.get("uma_checkpoint", "uma-s-1p2")),
                task_name=str(options.get("uma_task_name", "omc")),
                device=device,
            )
            adapter_cache[key] = model
    else:
        raise ValueError(f"unsupported backend: {backend}")
    prediction = model.predict(atoms)
    force_norms = [sum(float(component) ** 2 for component in force) ** 0.5 for force in prediction.forces]
    return {
        "formula": atoms.get_chemical_formula(),
        "natoms": len(atoms),
        "pbc": [bool(value) for value in atoms.pbc],
        "energy_ev": prediction.energy,
        "force_summary": {
            "max_force_ev_per_ang": max(force_norms, default=0.0),
            "mean_force_ev_per_ang": sum(force_norms) / len(force_norms) if force_norms else 0.0,
        },
        "model_metadata": prediction.metadata,
    }


def _row(
    input_row: dict[str, Any],
    backend: str,
    *,
    status: str,
    issue_signature: str,
    detail: str,
    energy_ev: float | None = None,
    max_force_ev_per_ang: float | None = None,
    mean_force_ev_per_ang: float | None = None,
    runtime_seconds: float = 0.0,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metrics_payload = dict(metrics or {})
    metrics_payload.update(
        {
            "input_status": input_row.get("status", ""),
            "input_review_status": input_row.get("review_status", ""),
            "input_release_category": input_row.get("release_category", ""),
        }
    )
    return {
        "row_id": f"{backend}:{input_row.get('molecule_id', '')}",
        "molecule_id": str(input_row.get("molecule_id", "")),
        "common_name": str(input_row.get("common_name", "")),
        "backend": backend,
        "status": status,
        "issue_signature": issue_signature,
        "detail": detail,
        "xyz_path": str(input_row.get("xyz_path", "")),
        "input_sha256": str(input_row.get("sha256", "")),
        "review_status": "candidate_unverified",
        "energy_ev": energy_ev,
        "max_force_ev_per_ang": max_force_ev_per_ang,
        "mean_force_ev_per_ang": mean_force_ev_per_ang,
        "runtime_seconds": runtime_seconds,
        "claim_boundary": BACKEND_SMOKE_CLAIM_BOUNDARY,
        "metrics": metrics_payload,
        "metrics_json": json.dumps(metrics_payload, sort_keys=True),
    }


def _classify_exception(exc: Exception) -> tuple[str, str]:
    detail = str(exc).lower()
    if isinstance(exc, AdapterNotAvailable) or isinstance(exc, ModuleNotFoundError):
        return "optional_backend_missing_dependency", "blocked"
    if "compiler: cl is not found" in detail or "cl is not found" in detail:
        return "backend_missing_windows_cpp_compiler", "blocked"
    if "out of memory" in detail or "cuda" in detail and "memory" in detail:
        return "backend_resource_exhausted", "blocked"
    return "backend_execution_exception", "failed"


def _is_environment_blocker(issue_signature: str) -> bool:
    return issue_signature in {
        "backend_missing_windows_cpp_compiler",
        "optional_backend_missing_dependency",
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
        severity = "failure"
        if "blocked" in statuses:
            severity = "blocked"
        elif "skipped" in statuses:
            severity = "skipped"
        elif "warning" in statuses:
            severity = "warning"
        signatures.append(
            {
                "issue_signature": signature,
                "severity": severity,
                "count": len(group),
                "example_ids": [f"{row['backend']}:{row['molecule_id']}" for row in group[:5]],
                "detail": group[0]["detail"],
            }
        )
    return signatures


def _format_float(value: Any) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return ""


def _compact_detail(value: str, *, max_length: int = 260) -> str:
    one_line = " ".join(value.split())
    if len(one_line) <= max_length:
        return one_line
    return one_line[: max_length - 3] + "..."


def _sqlite_row(row: dict[str, Any], columns: list[str]) -> tuple[str, ...]:
    values = []
    for column in columns:
        value = row[column]
        if isinstance(value, (dict, list)):
            values.append(json.dumps(value, sort_keys=True))
        else:
            values.append("" if value is None else str(value))
    return tuple(values)
