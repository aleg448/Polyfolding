import json
import sqlite3
from pathlib import Path

from crystalprobe.insight.molecule_bug_hunt import (
    molecule_bug_hunt_markdown,
    molecule_bug_hunt_report,
    write_molecule_bug_hunt_sqlite,
)


ROOT = Path(__file__).resolve().parents[1]


def _catalog():
    return json.loads((ROOT / "data" / "curation" / "molecule_bug_hunt_stress_v0.1.json").read_text(encoding="utf-8"))


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
