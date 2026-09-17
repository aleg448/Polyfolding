import json
import sqlite3
from pathlib import Path

import pytest

from crystalprobe.insight.molecule_bug_hunt import (
    _canonical_smiles_key,
    _crude_smiles_features,
    _smiles_features,
    molecule_bug_hunt_markdown,
    molecule_bug_hunt_report,
    write_molecule_bug_hunt_sqlite,
)


ROOT = Path(__file__).resolve().parents[1]


def _catalog():
    return json.loads((ROOT / "data" / "curation" / "molecule_bug_hunt_stress_v0.1.json").read_text(encoding="utf-8"))


def test_crude_features_false_positive_on_explicit_single_bond():
    # The string heuristic treats an explicit '-' single bond as a charge.
    assert _crude_smiles_features("C-C")["has_charge"] is True


def test_rdkit_features_avoid_explicit_single_bond_false_positive():
    pytest.importorskip("rdkit")
    features = _smiles_features("C-C")  # ethane written with an explicit single bond
    assert features["has_charge"] is False
    # A genuinely charged species is still detected.
    assert _smiles_features("CC(=O)[O-]")["has_charge"] is True


@pytest.mark.parametrize("function", [_smiles_features, _canonical_smiles_key])
def test_rdkit_log_configuration_is_restored(function):
    rd_base = pytest.importorskip("rdkit.rdBase")
    before = rd_base.LogStatus()
    function("invalid (((")
    assert rd_base.LogStatus() == before


def _mol(molecule_id, smiles, name):
    return {"molecule_id": molecule_id, "common_name": name, "smiles": smiles, "stress_tags": [], "expected_bug_surfaces": []}


def test_canonical_smiles_key_falls_back_to_raw_string_without_rdkit_or_on_garbage():
    # Without RDKit installed the key is the raw string; identical strings still
    # collide so exact-string duplicates keep grouping.
    assert _canonical_smiles_key("CC(=O)O") == _canonical_smiles_key("CC(=O)O")
    # An unparseable string never raises; it degrades to itself.
    assert _canonical_smiles_key("not a smiles (((") == "not a smiles ((("


def test_exact_string_duplicates_group_without_rdkit():
    catalog = {"molecules": [_mol("a", "CC(=O)O", "acetic acid"), _mol("b", "CC(=O)O", "acetic acid dup")]}
    report = molecule_bug_hunt_report(catalog)
    groups = {row["molecule_id"]: row["duplicate_smiles_group"] for row in report["molecules"]}
    assert groups["a"] and groups["b"]


def test_equivalent_connectivity_groups_with_rdkit():
    pytest.importorskip("rdkit")
    # Same molecule (benzene), two different SMILES spellings: raw-string equality
    # would miss this, canonicalization catches it.
    catalog = {"molecules": [_mol("a", "c1ccccc1", "benzene"), _mol("b", "C1=CC=CC=C1", "benzene kekulized")]}
    report = molecule_bug_hunt_report(catalog)
    groups = {row["molecule_id"]: row["duplicate_smiles_group"] for row in report["molecules"]}
    assert groups["a"] and groups["b"]


def test_molecule_bug_hunt_report_covers_weird_molecule_cases():
    report = molecule_bug_hunt_report(_catalog())

    assert report["status"] == "molecule_bug_hunt_ready"
    assert report["molecule_count"] >= 35
    assert report["tag_counts"]["charged"] >= 4
    assert report["tag_counts"]["chiral"] >= 3
    assert report["tag_counts"]["fused_ring"] >= 4
    assert any(row["component_count"] > 1 for row in report["molecules"])
    assert any(row["duplicate_smiles_group"] for row in report["molecules"])
    assert all(check["status"] == "passed" for check in report["coverage_checks"])


def test_molecule_bug_hunt_markdown_and_sqlite_are_queryable(tmp_path):
    report = molecule_bug_hunt_report(_catalog())
    markdown = molecule_bug_hunt_markdown(report)
    sqlite_path = tmp_path / "molecules.sqlite"

    write_molecule_bug_hunt_sqlite(report, sqlite_path)

    with sqlite3.connect(sqlite_path) as connection:
        charged = connection.execute(
            "select count(*) from molecule_stress_cases where has_charge = 'true'"
        ).fetchone()[0]
        duplicate = connection.execute(
            "select count(*) from molecule_stress_cases where duplicate_smiles_group != ''"
        ).fetchone()[0]

    assert "software_stress_fixture_not_scientific_evidence" in markdown
    assert "sodium chloride" in markdown
    assert charged >= 4
    assert duplicate >= 2
