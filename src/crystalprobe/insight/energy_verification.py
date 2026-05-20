"""Energy-layer verification and claim-gate checks."""

from __future__ import annotations

import math
from collections import Counter
from pathlib import Path
from typing import Any

from crystalprobe.benchmark.dataset import load_manifest
from crystalprobe.benchmark.predictions import PairEnergyPredictionRecord, load_pair_energy_prediction_records
from crystalprobe.benchmark.schema import PolymorphPair


ALLOWED_ENERGY_UNITS = {"eV"}


def energy_verification_report(
    *,
    manifest_path: str | Path,
    predictions_path: str | Path,
    molecule_bug_hunt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Audit pair-energy predictions without turning them into benchmark claims."""

    dataset = load_manifest(manifest_path)
    predictions = load_pair_energy_prediction_records(predictions_path)
    pair_by_id = {pair.pair_id: pair for pair in dataset.pairs}
    rows = [_energy_row(record, pair_by_id.get(record.pair_id)) for record in predictions]
    issues = _energy_issues(rows, dataset.pairs, predictions)
    stress = _stress_coverage(molecule_bug_hunt or {})
    issues.extend(stress["issues"])
    counts = Counter(issue["severity"] for issue in issues)
    verified_pairs = sum(1 for pair in dataset.pairs if pair.curation_status.value == "verified")
    status = "energy_verification_passed"
    if counts.get("blocker", 0) or verified_pairs == 0:
        status = "energy_verification_blocked_until_verified_calibration"
    return {
        "schema_version": "0.1.0",
        "status": status,
        "inputs": {
            "manifest": str(manifest_path),
            "predictions": str(predictions_path),
        },
        "counts": {
            "manifest_pairs": len(dataset.pairs),
            "verified_pairs": verified_pairs,
            "prediction_rows": len(predictions),
            "energy_rows": len(rows),
            "issue_count": len(issues),
            "blocker_count": counts.get("blocker", 0),
            "warning_count": counts.get("warning", 0),
            "info_count": counts.get("info", 0),
            "ood_prediction_count": sum(1 for row in rows if row["ood_flag_a"] or row["ood_flag_b"]),
            "non_verified_prediction_count": sum(1 for row in rows if row["curation_status"] != "verified"),
            "stress_molecule_count": stress["molecule_count"],
        },
        "energy_rows": rows,
        "issues": issues,
        "stress_coverage": stress["coverage"],
        "policy": [
            "Lower predicted energy wins only within the same model/backend and comparable input scope.",
            "Pair-energy rows on draft or reviewed records are demo or inspection signals, not benchmark evidence.",
            "OOD flags and missing uncertainty force abstention until verified calibration evidence exists.",
            "Absolute energies across MACE, AIMNet2, UMA, and demo backends must not be compared directly.",
            "The molecule bug-hunt database is software QA coverage, not scientific validation data.",
        ],
    }


def energy_verification_markdown(report: dict[str, Any]) -> str:
    """Render the energy verification report."""

    lines = [
        "# CrystalProbe Energy Verification",
        "",
        f"- Status: `{report['status']}`",
        f"- Prediction rows: `{report['counts']['prediction_rows']}`",
        f"- Verified pairs: `{report['counts']['verified_pairs']}`",
        f"- Blockers: `{report['counts']['blocker_count']}`",
        f"- Warnings: `{report['counts']['warning_count']}`",
        "",
        "## Energy Rows",
        "",
        "| Pair | Model | Status | Winner | Gap B-A | Combined Uncertainty | OOD | Claim Decision |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for row in report["energy_rows"]:
        lines.append(
            f"| `{row['pair_id']}` | `{row['model_name']}` | `{row['curation_status']}` | "
            f"`{row['predicted_winner']}` | `{row['energy_gap_b_minus_a']:.6f}` | "
            f"`{row['combined_uncertainty']:.6f}` | `{row['ood_flag_a'] or row['ood_flag_b']}` | "
            f"`{row['claim_decision']}` |"
        )
    lines.extend(
        [
            "",
            "## Issues",
            "",
            "| Severity | Check | Pair | Detail |",
            "|---|---|---|---|",
        ]
    )
    for issue in report["issues"]:
        lines.append(
            f"| `{issue['severity']}` | `{issue['check']}` | `{issue.get('pair_id', '')}` | {issue['detail']} |"
        )
    lines.extend(
        [
            "",
            "## Stress-Catalog Coverage",
            "",
            "| Check | Status | Detail |",
            "|---|---|---|",
        ]
    )
    for check in report["stress_coverage"]:
        lines.append(f"| `{check['check']}` | `{check['status']}` | {check['detail']} |")
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _energy_row(record: PairEnergyPredictionRecord, pair: PolymorphPair | None) -> dict[str, Any]:
    predicted_winner = record.as_metric_prediction().predicted_winner
    combined_uncertainty = _combined_uncertainty(record.energy_uncertainty_a, record.energy_uncertainty_b)
    curation_status = pair.curation_status.value if pair else "missing_manifest_pair"
    experimental_winner = pair.experimental_winner if pair else None
    return {
        "pair_id": record.pair_id,
        "model_name": record.model_name,
        "model_version": record.model_version,
        "energy_a": float(record.energy_a),
        "energy_b": float(record.energy_b),
        "energy_unit": record.energy_unit,
        "energy_gap_b_minus_a": float(record.energy_b) - float(record.energy_a),
        "predicted_winner": predicted_winner,
        "experimental_winner": experimental_winner,
        "prediction_matches_experiment": predicted_winner == experimental_winner if experimental_winner else None,
        "energy_uncertainty_a": record.energy_uncertainty_a,
        "energy_uncertainty_b": record.energy_uncertainty_b,
        "combined_uncertainty": combined_uncertainty,
        "ood_flag_a": bool(record.ood_flag_a),
        "ood_flag_b": bool(record.ood_flag_b),
        "curation_status": curation_status,
        "claim_decision": _claim_decision(pair, record),
        "notes": record.notes,
    }


def _energy_issues(
    rows: list[dict[str, Any]],
    pairs: list[PolymorphPair],
    predictions: list[PairEnergyPredictionRecord],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    pair_ids = {pair.pair_id for pair in pairs}
    predicted_ids = {record.pair_id for record in predictions}
    verified_count = sum(1 for pair in pairs if pair.curation_status.value == "verified")
    if verified_count == 0:
        issues.append(
            {
                "severity": "blocker",
                "check": "verified_calibration_absent",
                "detail": "No verified pairs exist, so energy rows cannot calibrate headline ranking claims.",
            }
        )
    for missing in sorted(pair_ids - predicted_ids):
        issues.append(
            {
                "severity": "info",
                "check": "missing_demo_prediction",
                "pair_id": missing,
                "detail": "No demo prediction row exists for this manifest pair.",
            }
        )
    for row in rows:
        pair_id = row["pair_id"]
        if pair_id not in pair_ids:
            issues.append(_issue("blocker", "prediction_without_manifest_pair", pair_id, "Prediction row has no manifest pair."))
        if row["energy_unit"] not in ALLOWED_ENERGY_UNITS:
            issues.append(_issue("blocker", "unsupported_energy_unit", pair_id, f"Unsupported unit {row['energy_unit']}."))
        if not math.isfinite(row["energy_a"]) or not math.isfinite(row["energy_b"]):
            issues.append(_issue("blocker", "nonfinite_energy", pair_id, "Energy values must be finite."))
        if row["energy_uncertainty_a"] is None or row["energy_uncertainty_b"] is None:
            issues.append(_issue("warning", "missing_uncertainty", pair_id, "Both sides should carry uncertainty for abstention."))
        elif row["energy_uncertainty_a"] < 0 or row["energy_uncertainty_b"] < 0:
            issues.append(_issue("blocker", "negative_uncertainty", pair_id, "Energy uncertainties must be non-negative."))
        if row["predicted_winner"] == "tie":
            issues.append(_issue("warning", "tie_prediction", pair_id, "Tie predictions are not rankable."))
        if row["curation_status"] != "verified":
            issues.append(
                _issue(
                    "info",
                    "non_verified_energy_row_abstained",
                    pair_id,
                    f"Record status is {row['curation_status']}; energy row is an inspection signal only.",
                )
            )
        if row["ood_flag_a"] or row["ood_flag_b"]:
            issues.append(_issue("warning", "ood_energy_row", pair_id, "At least one side is marked OOD."))
    return issues


def _stress_coverage(report: dict[str, Any]) -> dict[str, Any]:
    coverage = list(report.get("coverage_checks", []))
    issues = [
        {
            "severity": "warning",
            "check": "stress_catalog_coverage_gap",
            "detail": f"{check['check']}: {check['detail']}",
        }
        for check in coverage
        if check.get("status") == "blocked"
    ]
    return {
        "molecule_count": int(report.get("molecule_count", 0)),
        "coverage": coverage,
        "issues": issues,
    }


def _combined_uncertainty(a: float | None, b: float | None) -> float:
    total = 0.0
    if a is not None:
        total += float(a) * float(a)
    if b is not None:
        total += float(b) * float(b)
    return math.sqrt(total)


def _claim_decision(pair: PolymorphPair | None, record: PairEnergyPredictionRecord) -> str:
    if pair is None:
        return "blocked_missing_manifest_pair"
    if pair.curation_status.value != "verified":
        return "abstain_non_verified_record"
    if record.ood_flag_a or record.ood_flag_b:
        return "abstain_ood_flag"
    return "eligible_for_verified_slice_scoring"


def _issue(severity: str, check: str, pair_id: str, detail: str) -> dict[str, str]:
    return {"severity": severity, "check": check, "pair_id": pair_id, "detail": detail}
