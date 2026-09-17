import sys
import types

import pytest

try:  # numpy is an optional (non-core) dependency; the AIMNet2 tests below skip without it.
    import numpy as np
except ImportError:  # pragma: no cover - exercised in minimal CI environments
    np = None

from crystalprobe.foundry.optional_adapters import AIMNet2Adapter, UMAAdapter


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

    def __init__(self, *, pbc=False, info=None):
        self.pbc = pbc
        self.info = info or {}

    def copy(self):
        duplicate = _FakeAtoms(pbc=self.pbc, info=dict(self.info))
        duplicate.calc = self.calc
        return duplicate

    def __len__(self):
        return 3

    def get_potential_energy(self):
        return self.calc.get_potential_energy(self)

    def get_forces(self):
        return self.calc.get_forces(self)

    def get_atomic_numbers(self):
        return [6, 1, 1]

    def get_positions(self):
        return [[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]]


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
    assert prediction.metadata["adapter"] == "uma"
    assert prediction.metadata["energy_reference"] == "uma:uma-s-1p2:omc"
    assert prediction.metadata["scope"] == {"periodic": False, "total_charge": 0.0, "boundary": "cluster"}


class _FakeTensor:
    def __init__(self, array):
        self._array = np.asarray(array)

    def detach(self):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return self._array


class _RecordingAIMNet2Calculator:
    last_payload: dict | None = None

    def __init__(self, *, model, device, needs_dispersion):
        self.model = model
        self.device = device
        self.needs_dispersion = needs_dispersion

    def eval(self, payload, *, forces):
        type(self).last_payload = payload
        natoms = payload["numbers"].shape[1]
        return {
            "energy": _FakeTensor(np.asarray([-2.5], dtype=np.float64)),
            "forces": _FakeTensor(np.zeros((1, natoms, 3), dtype=np.float64)),
        }


def _install_fake_aimnet(monkeypatch):
    pytest.importorskip("numpy")
    aimnet_module = types.ModuleType("aimnet")
    aimnet_calculators = types.ModuleType("aimnet.calculators")
    aimnet_calculators.AIMNet2Calculator = _RecordingAIMNet2Calculator
    fake_torch = types.ModuleType("torch")
    fake_torch.cuda = types.SimpleNamespace(is_available=lambda: False)
    monkeypatch.setitem(sys.modules, "aimnet", aimnet_module)
    monkeypatch.setitem(sys.modules, "aimnet.calculators", aimnet_calculators)
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setattr("crystalprobe.foundry.optional_adapters.require_adapter", lambda name: None)
    _RecordingAIMNet2Calculator.last_payload = None


def test_aimnet2_adapter_uses_default_charge_and_records_scope(monkeypatch):
    _install_fake_aimnet(monkeypatch)
    adapter = AIMNet2Adapter(device="cpu")
    prediction = adapter.predict(_FakeAtoms())

    assert prediction.energy == -2.5
    assert len(prediction.forces) == 3
    assert prediction.metadata["total_charge"] == 0.0
    assert prediction.metadata["treated_as_cluster"] is False
    assert prediction.metadata["energy_reference"] == "aimnet2:aimnet2"
    assert float(_RecordingAIMNet2Calculator.last_payload["charge"][0]) == 0.0


def test_aimnet2_adapter_threads_explicit_and_structure_charge(monkeypatch):
    _install_fake_aimnet(monkeypatch)

    # Constructor default charge is used when the structure does not annotate one.
    adapter = AIMNet2Adapter(device="cpu", charge=-1.0)
    adapter.predict(_FakeAtoms())
    assert float(_RecordingAIMNet2Calculator.last_payload["charge"][0]) == -1.0

    # An explicit structure-level charge overrides the constructor default.
    adapter.predict(_FakeAtoms(info={"charge": 2.0}))
    assert float(_RecordingAIMNet2Calculator.last_payload["charge"][0]) == 2.0


def test_aimnet2_adapter_refuses_periodic_input_by_default(monkeypatch):
    _install_fake_aimnet(monkeypatch)
    adapter = AIMNet2Adapter(device="cpu")
    with pytest.raises(ValueError, match="periodic"):
        adapter.predict(_FakeAtoms(pbc=[True, True, True]))


def test_aimnet2_adapter_allows_periodic_cluster_when_opted_in(monkeypatch):
    _install_fake_aimnet(monkeypatch)
    adapter = AIMNet2Adapter(device="cpu", allow_periodic_cluster=True)
    prediction = adapter.predict(_FakeAtoms(pbc=[True, False, False]))
    assert prediction.metadata["treated_as_cluster"] is True
    assert prediction.metadata["scope"]["boundary"] == "periodic"
