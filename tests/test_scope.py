import pytest

from crystalprobe.foundry.scope import (
    describe_structure_scope,
    structure_is_periodic,
    structure_total_charge,
)


class _Atoms:
    def __init__(self, *, pbc=None, info=None, initial_charges=None):
        if pbc is not None:
            self.pbc = pbc
        self.info = info if info is not None else {}
        self._initial_charges = initial_charges

    def has(self, name):
        return self._initial_charges is not None

    def get_initial_charges(self):
        if self._initial_charges is None:
            raise AttributeError("no initial charges")
        return self._initial_charges


def test_structure_is_periodic_handles_scalar_and_vector_pbc():
    assert structure_is_periodic(_Atoms(pbc=True)) is True
    assert structure_is_periodic(_Atoms(pbc=False)) is False
    assert structure_is_periodic(_Atoms(pbc=[True, False, False])) is True
    assert structure_is_periodic(_Atoms(pbc=[False, False, False])) is False


def test_structure_without_pbc_attribute_is_cluster():
    assert structure_is_periodic(object()) is False


def test_total_charge_prefers_info_then_initial_charges_then_default():
    assert structure_total_charge(_Atoms(info={"charge": -1.0})) == -1.0
    assert structure_total_charge(_Atoms(initial_charges=[1.0, -1.0, 1.0])) == 1.0
    assert structure_total_charge(_Atoms(), default=3.0) == 3.0


def test_describe_structure_scope_round_trip():
    scope = describe_structure_scope(_Atoms(pbc=[True, True, True], info={"charge": 2.0}))
    assert scope == {"periodic": True, "total_charge": 2.0, "boundary": "periodic"}


def test_unannotated_ase_zero_array_does_not_override_requested_charge():
    class Unannotated(_Atoms):
        def has(self, name):
            return False

    assert structure_total_charge(Unannotated(initial_charges=[0.0]), default=1.0) == 1.0


def test_real_ase_charge_annotations_take_precedence():
    atoms = pytest.importorskip("ase").Atoms("Na")
    assert structure_total_charge(atoms, default=1.0) == 1.0
    atoms.set_initial_charges([0.0])
    assert structure_total_charge(atoms, default=1.0) == 0.0
    atoms.info["charge"] = -1.0
    assert structure_total_charge(atoms, default=1.0) == -1.0


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_charge_is_rejected(value):
    with pytest.raises(ValueError, match="finite"):
        structure_total_charge(_Atoms(info={"charge": value}))


def test_broken_explicit_charge_annotation_cannot_fall_back_to_neutral():
    class Broken:
        def has(self, name):
            return True

        def get_initial_charges(self):
            raise RuntimeError("broken charge data")

    with pytest.raises(ValueError, match="charge"):
        structure_total_charge(Broken())
