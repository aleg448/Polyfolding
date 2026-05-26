import sqlite3

import crystalprobe.insight.conformer_generation as conformers
from crystalprobe.insight.conformer_generation import (
    conformer_generation_markdown,
    conformer_generation_report,
    write_conformer_generation_sqlite,
    xyz_text,
)
from crystalprobe.insight.tentative_molecule_benchmark import MoleculeRecord


def _records():
    return [
        MoleculeRecord(
            molecule_id="ammonium",
            common_name="ammonium",
            smiles="[NH4+]",
            source_set="test",
            stress_tags=("charged",),
            expected_bug_surfaces=("formal_charge",),
        ),
        MoleculeRecord(
            molecule_id="benzene",
            common_name="benzene",
            smiles="c1ccccc1",
            source_set="test",
            stress_tags=("aromatic",),
            expected_bug_surfaces=("ring",),
        ),
    ]


def test_conformer_generation_records_missing_rdkit_as_blocker(monkeypatch):
    monkeypatch.setattr(conformers.importlib.util, "find_spec", lambda name: None)

    report = conformer_generation_report(_records())

    assert report["status"] == "conformer_generation_blocked_missing_dependency"
    assert report["coordinate_payload_enabled"] is False
    assert report["counts"]["molecule_count"] == 2
    assert report["counts"]["generated_count"] == 0
    assert report["counts"]["blocked_count"] == 2
    assert report["counts"]["coordinate_payload_count"] == 0
    assert report["counts"]["claim_ready_count"] == 0
    assert {row["issue_signature"] for row in report["rows"]} == {
        "optional_conformer_generator_missing_dependency"
    }


def test_conformer_generation_markdown_and_sqlite(monkeypatch, tmp_path):
    monkeypatch.setattr(conformers.importlib.util, "find_spec", lambda name: None)
    report = conformer_generation_report(_records())
    markdown = conformer_generation_markdown(report)

    assert markdown.startswith("# CrystalProbe Conformer Generation")
    assert "Coordinate payload enabled: `False`" in markdown
    assert "Coordinate payload rows: `0`" in markdown
    assert "generated inputs for software testing" in markdown

    sqlite_path = tmp_path / "conformers.sqlite"
    write_conformer_generation_sqlite(report, sqlite_path)
    with sqlite3.connect(sqlite_path) as connection:
        row_count = connection.execute("SELECT COUNT(*) FROM conformer_generation_rows").fetchone()[0]
        signature_count = connection.execute("SELECT COUNT(*) FROM bug_signatures").fetchone()[0]

    assert row_count == report["counts"]["row_count"]
    assert signature_count == report["counts"]["bug_signature_count"]


def test_xyz_text_renders_generated_coordinates():
    text = xyz_text(["C", "H"], [(0.0, 0.0, 0.0), (1.25, -0.5, 0.125)], comment="fixture")

    assert text.splitlines() == [
        "2",
        "fixture",
        "C 0.000000 0.000000 0.000000",
        "H 1.250000 -0.500000 0.125000",
    ]
