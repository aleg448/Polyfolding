import pytest

from crystalprobe.insight.sensitivity import PerturbationSpec, perturb_atoms, sensitivity_manifest, summarize_perturbation


ase = pytest.importorskip("ase")
ase_io = pytest.importorskip("ase.io")


def test_perturb_atoms_is_deterministic_for_position_noise(tmp_path):
    atoms = ase.Atoms("OH2", positions=[(0, 0, 0), (0, 0, 0.96), (0.9, 0, -0.25)])
    spec = PerturbationSpec(name="noise", position_sigma_ang=0.01, seed=7)
    first = perturb_atoms(atoms, spec)
    second = perturb_atoms(atoms, spec)
    assert first.get_positions().tolist() == second.get_positions().tolist()
    assert first.get_positions().tolist() != atoms.get_positions().tolist()


def test_summarize_perturbation_reports_cell_and_position_changes(tmp_path):
    atoms = ase.Atoms("He", positions=[(0.5, 0.5, 0.5)], cell=[10, 10, 10], pbc=True)
    spec = PerturbationSpec(name="scaled", cell_scale=1.01)
    perturbed = perturb_atoms(atoms, spec)
    out = tmp_path / "scaled.cif"
    ase_io.write(str(out), perturbed)
    summary = summarize_perturbation(atoms, perturbed, spec, path=out)
    assert summary["name"] == "scaled"
    assert summary["sha256"]
    assert summary["cell_frobenius_delta_ang"] > 0
    assert summary["rms_position_delta_ang"] > 0


def test_sensitivity_manifest_counts_variants():
    manifest = sensitivity_manifest(title="x", source="source.cif", block_id="AMPETP", variants=[{"name": "reference"}])
    assert manifest["variant_count"] == 1
    assert "not experimentally observed" in manifest["interpretation"][0]
