import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from crystalprobe.benchmark.predictions import PairEnergyPredictionRecord
from crystalprobe.insight.energy_verification import (
    _claim_decision,
    energy_verification_markdown,
    energy_verification_report,
)
from crystalprobe.insight.molecule_bug_hunt import molecule_bug_hunt_report


ROOT = Path(__file__).resolve().parents[1]


def _verified_pair():
    return SimpleNamespace(curation_status=SimpleNamespace(value="verified"))


def _record(**overrides):
    base = dict(pair_id="p1", energy_a=0.0, energy_b=1.0, model_name="demo")
    base.update(overrides)
    return PairEnergyPredictionRecord(**base)


def _stress_report():
    catalog = json.loads((ROOT / "data" / "curation" / "molecule_bug_hunt_stress_v0.1.json").read_text(encoding="utf-8"))
    return molecule_bug_hunt_report(catalog)


def test_energy_verification_blocks_claims_without_verified_calibration():
    report = energy_verification_report(
        manifest_path=ROOT / "data" / "benchmark" / "v0.1" / "manifest.jsonl",
        predictions_path=ROOT / "examples" / "demo_predictions.jsonl",
        molecule_bug_hunt=_stress_report(),
    )

    assert report["status"] == "energy_verification_blocked_until_verified_calibration"
    assert report["counts"]["prediction_rows"] == 2
    assert report["counts"]["verified_pairs"] == 0
    assert report["counts"]["stress_molecule_count"] >= 35
    assert report["counts"]["ood_prediction_count"] == 1
    assert report["counts"]["non_verified_prediction_count"] == 2
    checks = {issue["check"] for issue in report["issues"]}
    assert "verified_calibration_absent" in checks
    assert "ood_energy_row" in checks
    assert "missing_demo_prediction" in checks
    assert {row["claim_decision"] for row in report["energy_rows"]} == {"abstain_non_verified_record"}


def test_claim_decision_eligible_when_gap_clears_uncertainty():
    record = _record(energy_a=0.0, energy_b=1.0, energy_uncertainty_a=0.1, energy_uncertainty_b=0.1)
    assert _claim_decision(_verified_pair(), record) == "eligible_for_verified_slice_scoring"


def test_claim_decision_abstains_when_gap_inside_uncertainty():
    record = _record(energy_a=0.0, energy_b=0.05, energy_uncertainty_a=0.5, energy_uncertainty_b=0.5)
    assert _claim_decision(_verified_pair(), record) == "abstain_uncertain_ranking"


def test_claim_decision_abstains_when_uncertainty_missing():
    record = _record(energy_a=0.0, energy_b=1.0)  # uncertainties default to None
    assert _claim_decision(_verified_pair(), record) == "abstain_missing_uncertainty"


def test_claim_decision_conformal_threshold_can_block_marginal_gap():
    record = _record(energy_a=0.0, energy_b=0.3, energy_uncertainty_a=0.1, energy_uncertainty_b=0.1)
    # Gap 0.3 clears the 0.141 combined uncertainty alone...
    assert _claim_decision(_verified_pair(), record) == "eligible_for_verified_slice_scoring"
    # ...but not once a 0.25 conformal margin is added.
    assert _claim_decision(_verified_pair(), record, conformal_threshold=0.25) == "abstain_uncertain_ranking"


@pytest.mark.parametrize("overrides", [
    {"energy_uncertainty_a": float("nan")},
    {"energy_uncertainty_b": float("inf")},
    {"energy_uncertainty_a": -0.1},
    {"energy_b": float("inf")},
    {"energy_unit": "kJ/mol"},
])
def test_claim_gate_blocks_invalid_measurements(overrides):
    values = {"energy_uncertainty_a": 0.1, "energy_uncertainty_b": 0.1, **overrides}
    assert _claim_decision(_verified_pair(), _record(**values)).startswith("blocked_")


@pytest.mark.parametrize("threshold", [float("nan"), float("inf"), -0.1])
def test_report_rejects_invalid_threshold_even_without_verified_pairs(threshold):
    with pytest.raises(ValueError, match="threshold"):
        energy_verification_report(
            manifest_path=ROOT / "data/benchmark/v0.1/manifest.jsonl",
            predictions_path=ROOT / "examples/demo_predictions.jsonl",
            conformal_threshold=threshold,
        )


def test_missing_conformal_threshold_propagates_as_abstention():
    record = _record(energy_uncertainty_a=0.1, energy_uncertainty_b=0.1)
    assert _claim_decision(_verified_pair(), record, conformal_threshold=None) == "abstain_missing_calibration_threshold"


def test_energy_verification_markdown_keeps_energy_policy_visible():
    report = energy_verification_report(
        manifest_path=ROOT / "data" / "benchmark" / "v0.1" / "manifest.jsonl",
        predictions_path=ROOT / "examples" / "demo_predictions.jsonl",
        molecule_bug_hunt=_stress_report(),
    )
    markdown = energy_verification_markdown(report)

    assert markdown.startswith("# CrystalProbe Energy Verification")
    assert "verified_calibration_absent" in markdown
    assert "abstain_non_verified_record" in markdown
    assert "Absolute energies across MACE, AIMNet2, UMA, and demo backends must not be compared directly." in markdown
