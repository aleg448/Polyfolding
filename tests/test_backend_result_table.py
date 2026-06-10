import sqlite3

from crystalprobe.insight.backend_result_table import (
    backend_result_table_markdown,
    backend_result_table_report,
    write_backend_result_table_sqlite,
)


def _backend_smoke():
    return {
        "status": "backend_smoke_recorded_with_blockers",
        "benchmark_rows": [
            {
                "molecule_id": "water",
                "common_name": "water",
                "backend": "mace",
                "status": "passed",
                "energy_ev": -2081.0,
                "max_force_ev_per_ang": 1.7,
                "mean_force_ev_per_ang": 1.5,
                "runtime_seconds": 8.1,
                "input_sha256": "abc",
                "issue_signature": "none",
                "metrics": {
                    "formula": "H2O",
                    "natoms": 3,
                    "model_metadata": {"adapter": "mace_off", "model": "small", "device": "cpu"},
                },
            },
            {
                "molecule_id": "water",
                "common_name": "water",
                "backend": "aimnet2",
                "status": "blocked",
                "energy_ev": None,
                "max_force_ev_per_ang": None,
                "mean_force_ev_per_ang": None,
                "runtime_seconds": 3.0,
                "input_sha256": "abc",
                "issue_signature": "backend_missing_windows_cpp_compiler",
                "metrics": {},
            },
            {
                "molecule_id": "ethanol",
                "common_name": "ethanol",
                "backend": "mace",
                "status": "skipped",
                "issue_signature": "backend_execution_not_requested",
                "metrics": {},
            },
        ],
    }


def test_backend_result_table_extracts_actual_execution_rows():
    report = backend_result_table_report(_backend_smoke())
    by_backend = {row["backend"]: row for row in report["rows"]}

    assert report["counts"]["row_count"] == 2
    assert report["counts"]["passed_count"] == 1
    assert report["counts"]["blocked_count"] == 1
    assert report["counts"]["claim_ready_count"] == 0
    assert report["counts"]["finite_result_count"] == 1
    assert by_backend["mace"]["model_label"] == "mace_off:small"
    assert by_backend["mace"]["formula"] == "H2O"
    assert by_backend["mace"]["review_status"] == "candidate_unverified"
    assert by_backend["aimnet2"]["interpretation"].startswith("aimnet2 did not produce")


def test_backend_result_table_markdown_and_sqlite(tmp_path):
    report = backend_result_table_report(_backend_smoke())
    markdown = backend_result_table_markdown(report)

    assert markdown.startswith("# CrystalProbe First Backend Result Table")
    assert "mace_off:small" in markdown
    assert "backend_missing_windows_cpp_compiler" in markdown
    assert "Claim-ready rows: `0`" in markdown

    sqlite_path = tmp_path / "backend_result_table.sqlite"
    write_backend_result_table_sqlite(report, sqlite_path)
    with sqlite3.connect(sqlite_path) as connection:
        row_count = connection.execute("SELECT COUNT(*) FROM backend_result_rows").fetchone()[0]

    assert row_count == report["counts"]["row_count"]
