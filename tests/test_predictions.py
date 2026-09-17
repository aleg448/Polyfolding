from pathlib import Path

import pytest
from crystalprobe.benchmark.metrics import PairEnergyPrediction


from crystalprobe.benchmark.predictions import (
    load_pair_energy_prediction_records,
    load_pair_energy_predictions,
)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_energy_has_no_predicted_winner(value):
    assert PairEnergyPrediction(0, value).predicted_winner == "invalid"


def test_load_pair_energy_predictions():
    predictions = load_pair_energy_predictions(Path("examples/demo_predictions.jsonl"))
    assert "aspirin_form_i_vs_form_ii_seed" in predictions
    assert predictions["aspirin_form_i_vs_form_ii_seed"].predicted_winner == "A"


def test_load_pair_energy_predictions_rejects_mixed_units(tmp_path):
    path = tmp_path / "mixed.jsonl"
    path.write_text(
        '{"pair_id":"a","energy_a":0.0,"energy_b":1.0,"energy_unit":"eV","model_name":"m"}\n'
        '{"pair_id":"b","energy_a":0.0,"energy_b":1.0,"energy_unit":"kJ/mol","model_name":"m"}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="mixed energy units"):
        load_pair_energy_predictions(path)


def test_load_pair_energy_prediction_records_rejects_mixed_units(tmp_path):
    # The record loader feeds magnitude-sensitive calibration/verification, so it
    # must reject mixed units just like the metric loader does.
    path = tmp_path / "mixed.jsonl"
    path.write_text(
        '{"pair_id":"a","energy_a":0.0,"energy_b":1.0,"energy_unit":"eV","model_name":"m"}\n'
        '{"pair_id":"b","energy_a":0.0,"energy_b":1.0,"energy_unit":"kJ/mol","model_name":"m"}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="mixed energy units"):
        load_pair_energy_prediction_records(path)
