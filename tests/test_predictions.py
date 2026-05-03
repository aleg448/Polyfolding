from pathlib import Path

from crystalprobe.benchmark.predictions import load_pair_energy_predictions


def test_load_pair_energy_predictions():
    predictions = load_pair_energy_predictions(Path("examples/demo_predictions.jsonl"))
    assert "aspirin_form_i_vs_form_ii_seed" in predictions
    assert predictions["aspirin_form_i_vs_form_ii_seed"].predicted_winner == "A"

