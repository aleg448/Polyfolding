import pytest

from crystalprobe.insight.local_geometry import analyze_local_geometry


ase = pytest.importorskip("ase")


def test_analyze_local_geometry_reports_force_hotspots():
    atoms = ase.Atoms(["O", "H", "H"], positions=[(0, 0, 0), (0, 0, 0.96), (0.9, 0, -0.25)])
    report = analyze_local_geometry(atoms, forces=[(0, 0, 0), (1.2, 0, 0), (0.1, 0, 0)], max_items=2)
    assert report["natoms"] == 3
    assert report["bond_count"] >= 2
    assert report["force_hotspots"][0]["atom_index"] == 1
    assert "high_force_atom" in report["diagnostic_flags"]
    assert report["notes"].startswith("Geometric")


def test_analyze_local_geometry_reports_short_contacts():
    atoms = ase.Atoms("He2", positions=[(0, 0, 0), (0.2, 0, 0)])
    report = analyze_local_geometry(atoms, max_items=1)
    assert report["short_contacts"][0]["symbols"] == "He-He"
    assert "short_contact" in report["diagnostic_flags"]
