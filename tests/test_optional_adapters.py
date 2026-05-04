import sys
import types

from crystalprobe.foundry.optional_adapters import UMAAdapter


class _FakeCalculator:
    def get_potential_energy(self, atoms=None):
        return -1.25

    def get_forces(self, atoms=None):
        return [[0.0, 0.1, 0.2] for _ in range(len(atoms))]


class _FakeFAIRChemCalculator:
    @classmethod
    def from_model_checkpoint(cls, checkpoint, *, task_name, device):
        assert checkpoint == "uma-s-1p2"
        assert task_name == "omc"
        assert device == "cpu"
        return _FakeCalculator()


class _FakeAtoms:
    calc = None

    def copy(self):
        duplicate = _FakeAtoms()
        duplicate.calc = self.calc
        return duplicate

    def __len__(self):
        return 3

    def get_potential_energy(self):
        return self.calc.get_potential_energy(self)

    def get_forces(self):
        return self.calc.get_forces(self)


def test_uma_adapter_predicts_with_fairchem_calculator(monkeypatch):
    fairchem_module = types.ModuleType("fairchem")
    fairchem_core = types.ModuleType("fairchem.core")
    fairchem_core.FAIRChemCalculator = _FakeFAIRChemCalculator
    fake_torch = types.ModuleType("torch")
    fake_torch.cuda = types.SimpleNamespace(is_available=lambda: False)
    monkeypatch.setitem(sys.modules, "fairchem", fairchem_module)
    monkeypatch.setitem(sys.modules, "fairchem.core", fairchem_core)
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setattr("crystalprobe.foundry.optional_adapters.require_adapter", lambda name: None)

    adapter = UMAAdapter(device="cpu")
    prediction = adapter.predict(_FakeAtoms())

    assert prediction.energy == -1.25
    assert len(prediction.forces) == 3
    assert prediction.metadata == {
        "adapter": "uma",
        "checkpoint": "uma-s-1p2",
        "device": "cpu",
        "task_name": "omc",
    }
