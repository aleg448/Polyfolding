import pytest

from crystalprobe.uncertainty.calibrated_abstention import (
    bootstrap_mean_interval,
    calibrated_abstention_decision,
    conformal_abs_error_threshold,
)


@pytest.mark.parametrize("field", ["predicted_gap", "combined_uncertainty", "conformal_threshold"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_abstention_rejects_nonfinite_inputs(field, value):
    values = {"predicted_gap": 1.0, "combined_uncertainty": 0.1, "conformal_threshold": 0.1}
    values[field] = value
    with pytest.raises(ValueError, match="finite"):
        calibrated_abstention_decision(**values, evidence_status="verified")


def test_bootstrap_mean_interval_is_deterministic_and_contains_mean():
    interval = bootstrap_mean_interval([1.0, 2.0, 3.0, 4.0], rounds=200, seed=7)

    assert interval["sample_count"] == 4
    assert interval["lower"] <= interval["mean"] <= interval["upper"]


def test_conformal_threshold_records_finite_sample_status():
    threshold = conformal_abs_error_threshold([0.1, 0.4, 0.2], coverage=0.8)

    assert threshold["status"] == "insufficient_calibration_samples"
    assert threshold["threshold"] is None
    assert threshold["rank"] == 4
    decision = calibrated_abstention_decision(
        predicted_gap=100, combined_uncertainty=0, conformal_threshold=threshold["threshold"],
        evidence_status="verified",
    )
    assert decision["decision"] == "abstain_missing_calibration_threshold"


def test_conformal_order_statistic_without_interpolation():
    result = conformal_abs_error_threshold([0.1, 0.4, 0.2, 0.3], coverage=0.8)
    assert result["threshold"] == 0.4
    assert result["rank"] == 4


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_calibration_and_bootstrap_reject_nonfinite_samples(value):
    with pytest.raises(ValueError, match="finite"):
        conformal_abs_error_threshold([0.1, value])
    with pytest.raises(ValueError, match="finite"):
        bootstrap_mean_interval([0.1, value])


def test_calibrated_abstention_blocks_unverified_records():
    decision = calibrated_abstention_decision(
        predicted_gap=2.0,
        combined_uncertainty=0.2,
        conformal_threshold=0.2,
        evidence_status="candidate_unverified",
    )

    assert decision["decision"] == "abstain_needs_verified_evidence"
    assert decision["predicted_winner"] == "A"


def test_calibrated_abstention_allows_verified_clear_margin():
    decision = calibrated_abstention_decision(
        predicted_gap=-2.0,
        combined_uncertainty=0.2,
        conformal_threshold=0.2,
        evidence_status="verified",
    )

    assert decision["decision"] == "margin_clear_not_calibrated"
    assert decision["calibration_validated"] is False
    assert decision["predicted_winner"] == "B"
