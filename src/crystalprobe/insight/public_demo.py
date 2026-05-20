"""Public demo report generation for CrystalProbe."""

from __future__ import annotations

import json
import math
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Literal

from crystalprobe.benchmark.dataset import load_manifest
from crystalprobe.benchmark.metrics import ranking_accuracy
from crystalprobe.benchmark.predictions import load_pair_energy_prediction_records, load_pair_energy_predictions
from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.foundry.adapters import all_adapter_availability, check_adapter_availability
from crystalprobe.insight.figures import (
    backend_readiness_svg,
    calibration_reliability_svg,
    claim_gate_svg,
    demo_pipeline_svg,
    energy_uncertainty_svg,
    provenance_ledger_svg,
    write_svg,
)
from crystalprobe.openbench.quick import run_quick_benchmark


BackendSmokeMode = Literal["auto", "always", "never"]

DEFAULT_MANIFEST = Path("data/benchmark/v0.1/manifest.jsonl")
DEFAULT_PREDICTIONS = Path("examples/demo_predictions.jsonl")
DEFAULT_OUTPUT_DIR = Path("outputs/public_demo")
PUBLIC_DEMO_COMMAND = "python scripts/run_public_demo.py --backend-smoke auto"


def run_public_demo(
    *,
    manifest: str | Path = DEFAULT_MANIFEST,
    predictions: str | Path = DEFAULT_PREDICTIONS,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    backend_smoke: BackendSmokeMode = "auto",
    backend_timeout_seconds: int = 90,
    python_executable: str | None = None,
) -> dict[str, Any]:
    """Run the public CrystalProbe demo and write a compact report."""

    started = time.perf_counter()
    manifest_path = Path(manifest)
    prediction_path = Path(predictions)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    quick = run_quick_benchmark(
        manifest=manifest_path,
        predictions=prediction_path,
        output_dir=output_path,
        ledger=output_path / "public_demo_ledger.jsonl",
        verified_only=False,
    )
    dataset = load_manifest(manifest_path)
    prediction_map = load_pair_energy_predictions(prediction_path)
    prediction_records = load_pair_energy_prediction_records(prediction_path)
    ranking = ranking_accuracy(list(dataset), prediction_map)
    adapter_rows = _adapter_rows(
        backend_smoke=backend_smoke,
        timeout_seconds=backend_timeout_seconds,
        python_executable=python_executable or sys.executable,
    )
    calibration_payload = json.loads(quick.calibration_json.read_text(encoding="utf-8"))

    report = {
        "schema_version": "0.1.0",
        "demo_command": PUBLIC_DEMO_COMMAND,
        "scope": {
            "mission": "Reliable open research tooling for molecular prediction workflows.",
            "public_claim_boundary": (
                "This demo validates the workflow contract. It does not make a headline "
                "polymorph benchmark claim because the seed records are not verified."
            ),
            "backend_policy": (
                "The demo uses dependency-light sample predictions and opportunistically "
                "runs installed scientific backend smoke checks without making them required."
            ),
        },
        "inputs": {
            "manifest": str(manifest_path),
            "predictions": str(prediction_path),
        },
        "outputs": {
            "report_json": str(output_path / "public_demo_report.json"),
            "report_markdown": str(output_path / "public_demo_report.md"),
            "fingerprint_report_json": str(quick.report_json),
            "fingerprint_report_markdown": str(quick.report_markdown),
            "calibration_report_json": str(quick.calibration_json),
            "ledger": str(quick.ledger_path) if quick.ledger_path else None,
        },
        "dataset": dataset.summary(),
        "claim_gate": _claim_gate(dataset.summary()["statuses"], ranking),
        "quick_benchmark": {
            "accuracy": ranking.accuracy,
            "correct": ranking.correct,
            "evaluated": ranking.evaluated,
            "skipped": ranking.skipped,
            "interpretation": (
                "All seed manifest records are skipped when their experimental stability "
                "ordering is ambiguous or when no prediction exists for the pair."
            ),
        },
        "optional_scientific_backends": adapter_rows,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }
    report["outputs"]["figures"] = _write_demo_figures(
        report=report,
        calibration=calibration_payload,
        energy_rows=_energy_uncertainty_rows(list(dataset), prediction_records),
        output_dir=output_path / "figures",
    )
    atomic_write_json(output_path / "public_demo_report.json", report)
    atomic_write_text(output_path / "public_demo_report.md", public_demo_markdown(report))
    return report


def public_demo_markdown(report: dict[str, Any]) -> str:
    """Render the public demo report as Markdown."""

    lines = [
        "# CrystalProbe Public Demo Report",
        "",
        "## Demo Contract",
        "",
        f"- Command: `{report['demo_command']}`",
        f"- Mission: {report['scope']['mission']}",
        f"- Claim boundary: {report['scope']['public_claim_boundary']}",
        f"- Backend policy: {report['scope']['backend_policy']}",
        "",
        "## Curation And Claim Gate",
        "",
        "| Evidence label | Records | Evaluated | Accuracy | Public claim allowed |",
        "|---|---:|---:|---:|---|",
    ]
    for row in report["claim_gate"]["rows"]:
        accuracy = "n/a" if row["accuracy"] is None else f"{row['accuracy']:.3f}"
        lines.append(
            f"| {row['label']} | {row['records']} | {row['evaluated']} | "
            f"{accuracy} | {row['public_claim_allowed']} |"
        )
    lines.extend(
        [
            "",
            f"Gate decision: `{report['claim_gate']['decision']}`",
            "",
            "## Quick Benchmark Result",
            "",
            "| Correct | Evaluated | Skipped | Accuracy |",
            "|---:|---:|---:|---:|",
        ]
    )
    benchmark = report["quick_benchmark"]
    accuracy = "n/a" if benchmark["accuracy"] is None else f"{benchmark['accuracy']:.3f}"
    lines.extend(
        [
            f"| {benchmark['correct']} | {benchmark['evaluated']} | {benchmark['skipped']} | {accuracy} |",
            "",
            benchmark["interpretation"],
            "",
            "## Optional Scientific Backends",
            "",
            "| Backend | Available | Smoke status | Detail |",
            "|---|---:|---|---|",
        ]
    )
    for row in report["optional_scientific_backends"]:
        detail = row.get("detail") or row.get("blocker") or ""
        lines.append(f"| {row['name']} | {row['available']} | {row['smoke_status']} | {detail} |")
    lines.extend(
        [
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    for key, value in report["outputs"].items():
        if key == "figures":
            continue
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Visualizations", ""])
    for key, value in report["outputs"].get("figures", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", f"Elapsed seconds: `{report['elapsed_seconds']}`"])
    return "\n".join(lines).rstrip() + "\n"


def _claim_gate(statuses: dict[str, int], ranking: Any) -> dict[str, Any]:
    candidate_count = statuses.get("draft", 0)
    reviewed_count = statuses.get("reviewed", 0)
    verified_count = statuses.get("verified", 0)
    rows = [
        {
            "label": "candidate",
            "records": candidate_count,
            "evaluated": ranking.evaluated if verified_count == 0 else 0,
            "accuracy": ranking.accuracy if verified_count == 0 else None,
            "public_claim_allowed": "No. Candidate records support workflow smoke tests only.",
        },
        {
            "label": "reviewed",
            "records": reviewed_count,
            "evaluated": 0,
            "accuracy": None,
            "public_claim_allowed": "Limited. Reviewed records can support internal analysis, not headline claims.",
        },
        {
            "label": "verified",
            "records": verified_count,
            "evaluated": 0 if verified_count == 0 else ranking.evaluated,
            "accuracy": None if verified_count == 0 else ranking.accuracy,
            "public_claim_allowed": "Yes, but only for verified-only benchmark slices.",
        },
    ]
    if verified_count == 0:
        decision = "blocked_headline_benchmark_claims_until_verified_records_exist"
    else:
        decision = "allow_verified_only_claims_with_manifest_and_prediction_hashes"
    return {"decision": decision, "rows": rows}


def _adapter_rows(
    *,
    backend_smoke: BackendSmokeMode,
    timeout_seconds: int,
    python_executable: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    availability = {row.name: row for row in all_adapter_availability()}
    ase_available = check_adapter_availability("ase_cif").available
    smoke_by_adapter: dict[str, dict[str, Any]] = {}
    if backend_smoke != "never":
        for adapter_name, smoke_backend in (("mace_off", "mace"), ("aimnet2", "aimnet")):
            available = availability[adapter_name].available and ase_available
            if backend_smoke == "always" or available:
                smoke_by_adapter[adapter_name] = _run_backend_smoke(
                    smoke_backend,
                    timeout_seconds=timeout_seconds,
                    python_executable=python_executable,
                )

    for name in sorted(availability):
        row = availability[name]
        smoke = smoke_by_adapter.get(name)
        if smoke:
            smoke_status = smoke["status"]
            detail = smoke["detail"]
        elif name in {"mace_off", "aimnet2"} and backend_smoke == "never":
            smoke_status = "not_requested"
            detail = "Backend smoke checks were disabled for this run."
        elif name in {"mace_off", "aimnet2"} and not (row.available and ase_available):
            smoke_status = "skipped"
            detail = "Required backend modules or ASE are not importable."
        elif name == "uma":
            smoke_status = "not_implemented"
            detail = "UMA availability is reported; public H2O smoke is not wired yet."
        else:
            smoke_status = "not_applicable"
            detail = ""
        rows.append(
            {
                "name": name,
                "available": row.available,
                "required_modules": list(row.required_modules),
                "blocker": row.blocker,
                "smoke_status": smoke_status,
                "detail": detail,
            }
        )
    return rows


def _write_demo_figures(
    *,
    report: dict[str, Any],
    calibration: dict[str, Any],
    energy_rows: list[dict[str, Any]],
    output_dir: Path,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    figures = {
        "claim_gate": output_dir / "claim_gate.svg",
        "pipeline": output_dir / "pipeline.svg",
        "backend_readiness": output_dir / "backend_readiness.svg",
        "provenance_ledger": output_dir / "provenance_ledger.svg",
        "calibration_reliability": output_dir / "calibration_reliability.svg",
        "energy_uncertainty": output_dir / "energy_uncertainty.svg",
    }
    write_svg(figures["claim_gate"], claim_gate_svg(report))
    write_svg(figures["pipeline"], demo_pipeline_svg())
    write_svg(figures["backend_readiness"], backend_readiness_svg(report))
    write_svg(figures["provenance_ledger"], provenance_ledger_svg(report))
    write_svg(figures["calibration_reliability"], calibration_reliability_svg(calibration))
    write_svg(figures["energy_uncertainty"], energy_uncertainty_svg(energy_rows))
    return {key: str(path) for key, path in figures.items()}


def _energy_uncertainty_rows(pairs: list[Any], records: list[Any]) -> list[dict[str, Any]]:
    pair_by_id = {pair.pair_id: pair for pair in pairs}
    rows: list[dict[str, Any]] = []
    for record in records:
        pair = pair_by_id.get(record.pair_id)
        if pair is None:
            continue
        label = pair.molecule.common_name or pair.pair_id
        rows.append(
            {
                "pair_id": record.pair_id,
                "label": label,
                "curation_status": pair.curation_status.value,
                "energy_gap": abs(float(record.energy_a) - float(record.energy_b)),
                "combined_uncertainty": _combined_uncertainty(
                    record.energy_uncertainty_a,
                    record.energy_uncertainty_b,
                ),
                "ood_flag": bool(record.ood_flag_a or record.ood_flag_b),
            }
        )
    return rows


def _combined_uncertainty(a: float | None, b: float | None) -> float:
    if a is not None and b is not None:
        return math.sqrt(float(a) * float(a) + float(b) * float(b))
    if a is not None:
        return float(a)
    if b is not None:
        return float(b)
    return 0.0


def _run_backend_smoke(
    backend: str,
    *,
    timeout_seconds: int,
    python_executable: str,
) -> dict[str, str]:
    command = [python_executable, "scripts/smoke_backends.py", "--backend", backend]
    try:
        completed = subprocess.run(
            command,
            cwd=_repo_root(),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "detail": f"Exceeded {timeout_seconds} seconds."}
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip().splitlines()
        return {"status": "failed", "detail": detail[-1] if detail else f"Exit code {completed.returncode}."}
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"status": "passed", "detail": "Backend command completed."}
    backend_payload = payload.get(backend, {})
    energy = backend_payload.get("energy")
    metadata = backend_payload.get("metadata", {})
    return {
        "status": "passed",
        "detail": f"H2O smoke energy={energy}; metadata={metadata}",
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
