from crystalprobe.uncertainty.calibrated_abstention import (
    bootstrap_mean_interval,
    calibrated_abstention_decision,
    conformal_abs_error_threshold,
)


def test_bootstrap_mean_interval_is_deterministic_and_contains_mean():
    interval = bootstrap_mean_interval([1.0, 2.0, 3.0, 4.0], rounds=200, seed=7)

    assert interval["sample_count"] == 4
    assert interval["lower"] <= interval["mean"] <= interval["upper"]


def test_conformal_threshold_records_finite_sample_status():
    threshold = conformal_abs_error_threshold([0.1, 0.4, 0.2], coverage=0.8)

    assert threshold["status"] == "finite_sample_max_threshold"
    assert threshold["threshold"] == 0.4


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

    assert decision["decision"] == "claim_direction_allowed"
    assert decision["predicted_winner"] == "B"
