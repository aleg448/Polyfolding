from tests.test_schema import _record

from crystalprobe.benchmark.metrics import PairEnergyPrediction, ranking_accuracy
from crystalprobe.benchmark.schema import PolymorphPair


def test_ranking_accuracy_skips_ambiguous_and_scores_defined_pairs():
    correct_record = _record()
    correct_record["pair_id"] = "correct"
    correct_record["evidence"]["stability_ordering"] = "A>B"
    correct_record["evidence"]["citation_doi"] = "10.0000/example"
    correct_record["evidence"]["notes"] = ""

    ambiguous_record = _record()
    ambiguous_record["pair_id"] = "ambiguous"

    pairs = [PolymorphPair.model_validate(correct_record), PolymorphPair.model_validate(ambiguous_record)]
    predictions = {
        "correct": PairEnergyPrediction(energy_a=-1.0, energy_b=0.0),
        "ambiguous": PairEnergyPrediction(energy_a=0.0, energy_b=-1.0),
    }

    result = ranking_accuracy(pairs, predictions)
    assert result.correct == 1
    assert result.evaluated == 1
    assert result.skipped == 1
    assert result.accuracy == 1.0

