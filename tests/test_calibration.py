import json
from xml.etree import ElementTree

import pytest

from tests.test_schema import _record

from crystalprobe.benchmark.predictions import PairEnergyPredictionRecord
from crystalprobe.benchmark.schema import PolymorphPair
from crystalprobe.insight.calibration import build_calibration_report
from crystalprobe.insight.figures import calibration_reliability_svg
from crystalprobe.uncertainty.calibration import brier_score, expected_calibration_error


def test_binary_calibration_helpers():
    assert brier_score([0.9, 0.2], [True, False]) < 0.05
    assert expected_calibration_error([0.9, 0.2], [True, False], bins=2) >= 0.0


def test_pair_calibration_report_scores_defined_pairs():
    record = _record()
    record["curation_status"] = "verified"
    record["molecule"]["inchi"] = None
    record["has_disorder"] = False
    record["disorder_notes"] = ""
    record["notes"] = "Synthetic test fixture, not scientific evidence"
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
    assert report.as_dict()["calibration_validated"] is False
    assert report.as_dict()["status"] == "heuristic_diagnostics_not_validated"


def _pair_and_prediction(**overrides):
    data = _record(ordering="A>B")
    data.update(curation_status="verified", has_disorder=False, disorder_notes="", notes="Fixture")
    data["molecule"]["inchi"] = None
    data["evidence"].update(citation_doi="10.0000/fixture", notes="Synthetic test evidence")
    pair = PolymorphPair.model_validate(data)
    values = dict(pair_id=pair.pair_id, energy_a=0, energy_b=1,
                  energy_uncertainty_a=0.2, energy_uncertainty_b=0.2, model_name="fixture")
    return pair, PairEnergyPredictionRecord(**(values | overrides))


@pytest.mark.parametrize("overrides, reason", [
    ({"energy_uncertainty_a": None}, "missing_uncertainty"),
    ({"energy_uncertainty_a": -0.1}, "invalid_uncertainty"),
    ({"energy_uncertainty_b": float("nan")}, "invalid_uncertainty"),
    ({"energy_uncertainty_b": float("inf")}, "invalid_uncertainty"),
    ({"energy_uncertainty_a": 0, "energy_uncertainty_b": 0}, "invalid_uncertainty"),
    ({"energy_uncertainty_a": 1.7e308, "energy_uncertainty_b": 1.7e308}, "invalid_uncertainty"),
    ({"energy_a": float("nan")}, "nonfinite_energy"),
    ({"energy_b": float("inf")}, "nonfinite_energy"),
    ({"energy_a": -1.7e308, "energy_b": 1.7e308}, "nonfinite_energy"),
    ({"energy_b": 0}, "tie_prediction"),
    ({"ood_flag_a": True}, "ood_prediction"),
    ({"energy_unit": "kJ/mol"}, "unsupported_energy_unit"),
])
def test_report_excludes_unusable_predictions(overrides, reason):
    pair, prediction = _pair_and_prediction(**overrides)
    report = build_calibration_report([pair], [prediction])
    assert report.points == []
    assert report.brier_score is None
    assert report.expected_calibration_error is None
    assert report.as_dict()["excluded_predictions"] == [{"pair_id": pair.pair_id, "reason": reason}]
    json.dumps(report.as_dict(), allow_nan=False)


def test_unverified_record_cannot_supply_calibration_evidence():
    pair, prediction = _pair_and_prediction()
    pair = PolymorphPair.model_validate(pair.model_dump() | {"curation_status": "draft"})
    report = build_calibration_report([pair], [prediction])
    assert report.points == []
    assert report.as_dict()["excluded_predictions"][0]["reason"] == "non_verified_record"


def test_empty_evidence_has_unavailable_scores_and_renders():
    report = build_calibration_report([], [])
    assert brier_score([], []) is None
    assert expected_calibration_error([], []) is None
    assert report.as_dict()["status"] == "no_eligible_evidence"
    svg = calibration_reliability_svg(report.as_dict())
    assert "ECE: unavailable; Brier: unavailable" in svg
    assert "ECE: 0.000" not in svg
    text_rows = {node.text: float(node.attrib["y"]) for node in ElementTree.fromstring(svg)
                 if node.tag.endswith("text")}
    assert text_rows["Predicted confidence"] + 16 <= text_rows[
        "Heuristic confidence diagnostics; calibration not validated."
    ]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -0.1, 1.1])
@pytest.mark.parametrize("metric", [brier_score, expected_calibration_error])
def test_invalid_confidence_rejected(value, metric):
    with pytest.raises(ValueError, match="finite.*between"):
        metric([value], [True])


def test_uncertain_ranking_is_kept_to_avoid_selection_bias():
    pair, prediction = _pair_and_prediction(energy_b=0.01)
    report = build_calibration_report([pair], [prediction])
    assert len(report.points) == 1
    assert 0.5 < report.points[0].confidence < 0.6
