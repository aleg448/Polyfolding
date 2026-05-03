"""Quick-mode benchmark runner."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from crystalprobe.benchmark.dataset import load_manifest
from crystalprobe.benchmark.predictions import load_pair_energy_prediction_records, load_pair_energy_predictions
from crystalprobe.core.ledger import LedgerEntry, file_sha256, record_ledger_entry
from crystalprobe.insight.calibration import build_calibration_report
from crystalprobe.insight.fingerprint import build_fingerprint_report
from crystalprobe.insight.reporting import fingerprint_markdown


@dataclass(frozen=True)
class QuickBenchmarkResult:
    report_json: Path
    report_markdown: Path
    calibration_json: Path
    ledger_path: Path | None


def run_quick_benchmark(
    *,
    manifest: str | Path,
    predictions: str | Path,
    output_dir: str | Path,
    ledger: str | Path | None = None,
    verified_only: bool = False,
) -> QuickBenchmarkResult:
    """Run the dependency-light benchmark analysis path."""

    manifest_path = Path(manifest)
    prediction_path = Path(predictions)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    dataset = load_manifest(manifest_path)
    if verified_only:
        dataset = dataset.verified()
    prediction_map = load_pair_energy_predictions(prediction_path)
    prediction_records = load_pair_energy_prediction_records(prediction_path)
    pairs = list(dataset)
    report = build_fingerprint_report(pairs, prediction_map)
    calibration = build_calibration_report(pairs, prediction_records)

    report_json = output_path / "fingerprint_report.json"
    report_markdown = output_path / "fingerprint_report.md"
    calibration_json = output_path / "calibration_report.json"
    with report_json.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report.as_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")
    report_markdown.write_text(fingerprint_markdown(report), encoding="utf-8", newline="\n")
    with calibration_json.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(calibration.as_dict(), handle, indent=2, sort_keys=True)
        handle.write("\n")

    ledger_path = Path(ledger) if ledger else None
    if ledger_path:
        entry = LedgerEntry(
            action="openbench.quick",
            inputs={
                "manifest": str(manifest_path),
                "manifest_sha256": file_sha256(manifest_path),
                "predictions": str(prediction_path),
                "predictions_sha256": file_sha256(prediction_path),
            },
            outputs={
                "report_json": str(report_json),
                "report_markdown": str(report_markdown),
                "calibration_json": str(calibration_json),
            },
            parameters={"verified_only": verified_only},
            metrics={
                "fingerprint_overall": report.as_dict()["overall"],
                "calibration": {
                    "brier_score": calibration.brier_score,
                    "expected_calibration_error": calibration.expected_calibration_error,
                    "points": len(calibration.points),
                },
            },
        )
        record_ledger_entry(entry, ledger_path)

    return QuickBenchmarkResult(
        report_json=report_json,
        report_markdown=report_markdown,
        calibration_json=calibration_json,
        ledger_path=ledger_path,
    )
