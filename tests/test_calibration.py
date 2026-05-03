from tests.test_schema import _record

from crystalprobe.benchmark.predictions import PairEnergyPredictionRecord
from crystalprobe.benchmark.schema import PolymorphPair
from crystalprobe.insight.calibration import build_calibration_report
from crystalprobe.uncertainty.calibration import brier_score, expected_calibration_error


def test_binary_calibration_helpers():
    assert brier_score([0.9, 0.2], [True, False]) < 0.05
    assert expected_calibration_error([0.9, 0.2], [True, False], bins=2) >= 0.0


def test_pair_calibration_report_scores_defined_pairs():
    record = _record()
    record["pair_id"] = "fixture"
    record["evidence"]["stability_ordering"] = "A>B"
    record["evidence"]["citation_doi"] = "10.0000/example"
    record["evidence"]["notes"] = ""
    pair = PolymorphPair.model_validate(record)
    prediction = PairEnergyPredictionRecord(
        pair_id="fixture",
        energy_a=-1.0,
        energy_b=0.0,
        energy_uncertainty_a=0.2,
        energy_uncertainty_b=0.2,
        model_name="fixture",
    )
    report = build_calibration_report([pair], [prediction], bins=5)
    assert len(report.points) == 1
    assert report.points[0].correct is True
    assert report.brier_score >= 0.0
