import sqlite3

from crystalprobe.insight.molecule_bug_dashboard import (
    molecule_bug_dashboard_markdown,
    molecule_bug_dashboard_report,
    write_molecule_bug_dashboard_sqlite,
)


def _tentative():
    return {
        "molecules": [
            {"molecule_id": "water", "common_name": "water", "source_set": "fixture", "stress_tags": ["tiny"]},
            {
                "molecule_id": "cholesterol",
                "common_name": "cholesterol",
                "source_set": "fixture",
                "stress_tags": ["large"],
            },
        ],
        "benchmark_rows": [
            {
                "molecule_id": "water",
                "tool": "smiles_lexical",
                "status": "passed",
                "issue_signature": "none",
                "detail": "ok",
            },
            {
                "molecule_id": "water",
                "tool": "rdkit_smiles",
                "status": "passed",
                "issue_signature": "none",
                "detail": "ok",
            },
            {
                "molecule_id": "cholesterol",
                "tool": "smiles_lexical",
                "status": "passed",
                "issue_signature": "none",
                "detail": "ok",
            },
            {
                "molecule_id": "cholesterol",
                "tool": "rdkit_smiles",
                "status": "passed",
                "issue_signature": "none",
                "detail": "ok",
            },
        ],
    }


def _ready_inputs():
    return {
        "rows": [
            {
                "molecule_id": "water",
                "common_name": "water",
                "status": "ready",
                "issue_signature": "none",
                "xyz_path": "water.xyz",
            },
            {
                "molecule_id": "cholesterol",
                "common_name": "cholesterol",
                "status": "warning",
                "issue_signature": "rdkit_uff_not_converged",
                "xyz_path": "cholesterol.xyz",
            },
        ]
    }


def _backend_smoke():
    return {
        "benchmark_rows": [
            {
                "molecule_id": "water",
                "backend": "mace",
                "status": "passed",
                "issue_signature": "none",
                "energy_ev": -1.0,
                "max_force_ev_per_ang": 0.5,
                "mean_force_ev_per_ang": 0.2,
                "metrics": {"formula": "H2O"},
            },
            {
                "molecule_id": "water",
                "backend": "aimnet2",
                "status": "blocked",
                "issue_signature": "backend_missing_windows_cpp_compiler",
                "energy_ev": None,
                "max_force_ev_per_ang": None,
                "mean_force_ev_per_ang": None,
                "metrics": {},
            },
        ]
    }


def test_molecule_bug_dashboard_joins_parser_conformer_backend_statuses():
    report = molecule_bug_dashboard_report(
        tentative_benchmark=_tentative(),
        backend_ready_inputs=_ready_inputs(),
        backend_smoke=_backend_smoke(),
    )
    by_id = {row["molecule_id"]: row for row in report["rows"]}

    assert report["counts"]["molecule_count"] == 2
    assert report["counts"]["claim_ready_count"] == 0
    assert by_id["water"]["parser_status"] == "passed"
    assert by_id["water"]["conformer_status"] == "ready"
    assert by_id["water"]["backend_status"] == "partial_backend_blocker"
    assert by_id["water"]["energy_force_sanity"] == "passed"
    assert by_id["water"]["issue_signature"] == "backend_missing_windows_cpp_compiler"
    assert by_id["cholesterol"]["conformer_status"] == "warning"
    assert by_id["cholesterol"]["backend_status"] == "not_run"
    assert "rdkit_uff_not_converged" in by_id["cholesterol"]["issue_signature"]
    assert "backend_not_run" in by_id["cholesterol"]["issue_signature"]


def test_molecule_bug_dashboard_markdown_and_sqlite(tmp_path):
    report = molecule_bug_dashboard_report(
        tentative_benchmark=_tentative(),
        backend_ready_inputs=_ready_inputs(),
        backend_smoke=_backend_smoke(),
    )
    markdown = molecule_bug_dashboard_markdown(report)

    assert markdown.startswith("# CrystalProbe Molecule Bug Dashboard")
    assert "Backend" in markdown
    assert "Claim-ready rows: `0`" in markdown
    assert "backend_missing_windows_cpp_compiler" in markdown

    sqlite_path = tmp_path / "dashboard.sqlite"
    write_molecule_bug_dashboard_sqlite(report, sqlite_path)
    with sqlite3.connect(sqlite_path) as connection:
        row_count = connection.execute("SELECT COUNT(*) FROM molecule_bug_dashboard").fetchone()[0]
        signature_count = connection.execute("SELECT COUNT(*) FROM issue_signatures").fetchone()[0]

    assert row_count == report["counts"]["molecule_count"]
    assert signature_count == report["counts"]["issue_signature_count"]
