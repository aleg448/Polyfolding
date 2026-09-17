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


def test_dense_and_neighbor_paths_agree_on_nonperiodic_structure():
    # A small chain of atoms with no cell: the exact dense scan and the
    # neighbour-list cutoff scan must produce identical close-pair diagnostics.
    positions = [(1.1 * index, 0.0, 0.0) for index in range(12)]
    atoms = ase.Atoms("C12", positions=positions)

    dense = analyze_local_geometry(atoms, max_dense_atoms=1500)
    neighbor = analyze_local_geometry(atoms, max_dense_atoms=0)

    assert dense["pairwise_method"] == "dense"
    assert neighbor["pairwise_method"] == "neighbor_list"
    assert dense["bond_count"] == neighbor["bond_count"]
    assert dense["bond_count"] > 0
    assert dense["bond_geometry_outliers"] == neighbor["bond_geometry_outliers"]
    assert dense["short_contacts"] == neighbor["short_contacts"]


def test_periodic_neighbor_scan_uses_closest_image():
    atoms = ase.Atoms("C2", positions=[(0, 0, 0), (0.3, 0, 0)], cell=[2, 5, 5], pbc=True)
    dense = analyze_local_geometry(atoms, max_dense_atoms=5)
    neighbor = analyze_local_geometry(atoms, max_dense_atoms=0)
    assert neighbor["short_contacts"] == dense["short_contacts"]
    assert neighbor["bond_geometry_outliers"] == dense["bond_geometry_outliers"]


def test_neighbor_cutoff_includes_custom_short_contact_threshold():
    atoms = ase.Atoms("C2", positions=[(0, 0, 0), (2, 0, 0)])
    dense = analyze_local_geometry(atoms, bond_cutoff_scale=1, short_contact_scale=1.5)
    neighbor = analyze_local_geometry(atoms, bond_cutoff_scale=1, short_contact_scale=1.5, max_dense_atoms=0)
    assert neighbor["short_contacts"] == dense["short_contacts"]


@pytest.mark.parametrize("max_dense_atoms", [0, 1500])
def test_coincident_atoms_are_reported_as_short_contacts(max_dense_atoms):
    atoms = ase.Atoms("C2", positions=[(0, 0, 0), (0, 0, 0)])
    report = analyze_local_geometry(atoms, max_dense_atoms=max_dense_atoms)
    assert "short_contact" in report["diagnostic_flags"]
    assert report["short_contacts"][0]["distance_ang"] == 0


@pytest.mark.parametrize("forces", [[], [(0, 0, 0)], [(1, 2), (1, 2)],
                                    [(float("nan"), 0, 0), (0, 0, 0)]])
def test_invalid_force_arrays_are_rejected(forces):
    atoms = ase.Atoms("C2", positions=[(0, 0, 0), (1, 0, 0)])
    with pytest.raises(ValueError, match="forces"):
        analyze_local_geometry(atoms, forces=forces)


def test_nonfinite_positions_are_rejected():
    atoms = ase.Atoms("C", positions=[(float("nan"), 0, 0)])
    with pytest.raises(ValueError, match="positions"):
        analyze_local_geometry(atoms)


def test_periodic_distance_failure_is_not_retried_as_cluster(monkeypatch):
    atoms = ase.Atoms("C2", positions=[(0, 0, 0), (1, 0, 0)], cell=[5, 5, 5], pbc=True)
    original = atoms.get_all_distances

    def distance(*, mic=False):
        if mic:
            raise ValueError("broken periodic cell")
        return original()

    monkeypatch.setattr(atoms, "get_all_distances", distance)
    with pytest.raises(ValueError, match="periodic"):
        analyze_local_geometry(atoms)
