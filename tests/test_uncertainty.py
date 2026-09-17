from dataclasses import dataclass

import pytest

from crystalprobe.uncertainty import DeterministicHashModel, EnergyForcePrediction, EnsembleMLIPWrapper


@dataclass
class ConstantModel:
    name: str
    energy: float
    ood_score: float | None = None
    energy_reference: str | None = "test_fixture"

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


def test_ensemble_refuses_mixed_energy_references():
    with pytest.raises(ValueError, match="energy reference"):
        EnsembleMLIPWrapper(
            [
                ConstantModel(name="mace", energy=1.0, energy_reference="mace_off:small"),
                ConstantModel(name="aimnet2", energy=3.0, energy_reference="aimnet2:aimnet2"),
            ]
        )


def test_ensemble_allows_shared_reference_and_records_references():
    wrapper = EnsembleMLIPWrapper(
        [
            ConstantModel(name="mace_a", energy=1.0, energy_reference="mace_off:small"),
            ConstantModel(name="mace_b", energy=3.0, energy_reference="mace_off:small"),
        ]
    )
    prediction = wrapper.predict(structure={})
    assert prediction.energy == 2.0
    assert prediction.metadata["energy_references"] == ["mace_off:small", "mace_off:small"]


def test_ensemble_cannot_bypass_reference_validation():
    with pytest.raises(ValueError, match="reference"):
        EnsembleMLIPWrapper([
            ConstantModel(name="mace", energy=1.0, energy_reference="mace_off:small"),
            ConstantModel(name="aimnet2", energy=3.0, energy_reference="aimnet2:aimnet2"),
        ], allow_mixed_reference=True)


@pytest.mark.parametrize("reference", [None, "", "   "])
def test_ensemble_rejects_missing_reference(reference):
    with pytest.raises(ValueError, match="reference"):
        EnsembleMLIPWrapper([ConstantModel("x", 1, energy_reference=reference)])


def test_single_member_does_not_report_zero_uncertainty():
    assert EnsembleMLIPWrapper([ConstantModel("x", 1)]).predict({}).energy_uncertainty is None


@pytest.mark.parametrize("value", [float("nan"), float("inf")])
def test_ensemble_rejects_nonfinite_predictions(value):
    with pytest.raises(ValueError, match="finite"):
        EnsembleMLIPWrapper([ConstantModel("x", value)]).predict({})


def test_ensemble_rejects_mismatched_prediction_scope():
    class Scoped(ConstantModel):
        def predict(self, structure):
            return EnergyForcePrediction(energy=self.energy, metadata={"scope": {"boundary": self.name}})

    with pytest.raises(ValueError, match="scope"):
        EnsembleMLIPWrapper([Scoped("cluster", 1), Scoped("periodic", 2)]).predict({})


def test_deterministic_hash_model_is_stable():
    model = DeterministicHashModel()
    first = model.predict({"atoms": ["C", "H"]})
    second = model.predict({"atoms": ["C", "H"]})
    assert first.energy == second.energy
