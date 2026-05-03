from dataclasses import dataclass

from crystalprobe.uncertainty import DeterministicHashModel, EnergyForcePrediction, EnsembleMLIPWrapper


@dataclass
class ConstantModel:
    name: str
    energy: float
    ood_score: float | None = None

    def predict(self, structure):
        return EnergyForcePrediction(energy=self.energy, ood_score=self.ood_score)


def test_ensemble_reports_mean_variance_and_ood_flag():
    wrapper = EnsembleMLIPWrapper(
        [
            ConstantModel(name="a", energy=1.0, ood_score=0.1),
            ConstantModel(name="b", energy=3.0, ood_score=0.9),
        ],
        ood_threshold=0.8,
    )
    prediction = wrapper.predict(structure={})
    assert prediction.energy == 2.0
    assert round(prediction.energy_uncertainty, 6) == 1.414214
    assert prediction.ood_score == 0.9
    assert prediction.ood_flag is True
    assert prediction.metadata["ensemble_members"] == ["a", "b"]


def test_deterministic_hash_model_is_stable():
    model = DeterministicHashModel()
    first = model.predict({"atoms": ["C", "H"]})
    second = model.predict({"atoms": ["C", "H"]})
    assert first.energy == second.energy
