import pytest

from crystalprobe.datahub.sources import source_registry
from crystalprobe.foundry.adapters import check_adapter_availability
from crystalprobe.foundry.adapters import AdapterNotAvailable
from crystalprobe.structures.cif import read_cif_structure


def test_source_registry_has_core_sources():
    names = {source.name for source in source_registry()}
    assert {"CPOSS209", "OMC25 dataset", "MACE-OFF23", "fairchem"}.issubset(names)


def test_read_cif_reports_clear_error_without_ase(tmp_path):
    if check_adapter_availability("ase_cif").available:
        pytest.skip("ASE installed; missing-dependency behavior is not active")
    with pytest.raises(AdapterNotAvailable, match="ASE"):
        read_cif_structure(tmp_path / "missing.cif")

