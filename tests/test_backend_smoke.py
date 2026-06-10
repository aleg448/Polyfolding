import sqlite3

from crystalprobe.insight.backend_smoke import (
    backend_smoke_markdown,
    backend_smoke_report,
    write_backend_smoke_sqlite,
)


def _manifest():
    return {
        "claim_boundary": "backend_ready_generated_conformer_input_not_scientific_evidence",
        "rows": [
            {
                "molecule_id": "water",
                "common_name": "water",
                "status": "ready",
                "review_status": "candidate_unverified",
                "release_category": "local_generated_coordinate_input_metadata",
                "xyz_path": "outputs/generated_conformers/water.xyz",
                "sha256": "abc123",
                "atom_count": 3,
            },
            {
                "molecule_id": "ethanol",
                "common_name": "ethanol",
                "status": "ready",
                "review_status": "candidate_unverified",
                "release_category": "local_generated_coordinate_input_metadata",
                "xyz_path": "outputs/generated_conformers/ethanol.xyz",
                "sha256": "def456",
                "atom_count": 9,
            },
            {
                "molecule_id": "blocked",
                "common_name": "blocked",
                "status": "blocked",
                "review_status": "candidate_unverified",
                "release_category": "local_generated_coordinate_input_metadata",
                "xyz_path": "",
                "sha256": "",
                "atom_count": 0,
            },
        ],
    }


def _fake_executor(input_row, backend, options):
    if backend == "aimnet2":
        raise RuntimeError("Compiler: cl is not found.")
    return {
        "formula": "H2O",
        "natoms": 3,
        "pbc": [False, False, False],
        "energy_ev": -12.5,
        "force_summary": {
            "max_force_ev_per_ang": 0.25,
            "mean_force_ev_per_ang": 0.15,
        },
        "model_metadata": {"adapter": backend, "device": options["device"]},
    }


def test_backend_smoke_report_records_passes_and_backend_blockers():
    report = backend_smoke_report(
        _manifest(),
        backends=("mace", "aimnet2"),
        limit=1,
        device="cpu",
        executor=_fake_executor,
    )
    by_backend = {row["backend"]: row for row in report["benchmark_rows"]}

    assert report["status"] == "backend_smoke_recorded_with_blockers"
    assert report["counts"]["input_rows_available"] == 2
    assert report["counts"]["input_rows_selected"] == 1
    assert report["counts"]["passed_count"] == 1
    assert report["counts"]["blocked_count"] == 1
    assert report["counts"]["cached_environment_blocker_count"] == 0
    assert report["counts"]["claim_ready_count"] == 0
    assert by_backend["mace"]["status"] == "passed"
    assert by_backend["mace"]["energy_ev"] == -12.5
    assert by_backend["aimnet2"]["issue_signature"] == "backend_missing_windows_cpp_compiler"
    assert by_backend["aimnet2"]["review_status"] == "candidate_unverified"


def test_backend_smoke_all_rows_caches_environment_blockers():
    calls = []

    def executor(input_row, backend, options):
        calls.append((input_row["molecule_id"], backend))
        return _fake_executor(input_row, backend, options)

    report = backend_smoke_report(
        _manifest(),
        backends=("mace", "aimnet2"),
        limit=0,
        device="cpu",
        executor=executor,
    )
    rows = {(row["molecule_id"], row["backend"]): row for row in report["benchmark_rows"]}

    assert report["counts"]["input_rows_selected"] == 2
    assert report["counts"]["backend_row_count"] == 4
    assert report["counts"]["passed_count"] == 2
    assert report["counts"]["blocked_count"] == 2
    assert report["counts"]["cached_environment_blocker_count"] == 1
    assert ("ethanol", "aimnet2") not in calls
    assert rows[("ethanol", "aimnet2")]["issue_signature"] == "backend_missing_windows_cpp_compiler"
    assert rows[("ethanol", "aimnet2")]["metrics"]["cached_environment_blocker"] is True


def test_backend_smoke_dry_run_markdown_and_sqlite(tmp_path):
    report = backend_smoke_report(_manifest(), backends=("mace",), limit=1, execute=False)
    markdown = backend_smoke_markdown(report)

    assert markdown.startswith("# CrystalProbe Backend Smoke Benchmark")
    assert "Skipped rows: `1`" in markdown
    assert "Claim-ready rows: `0`" in markdown
    assert "Absolute energies from different backends are not commensurate" in markdown

    sqlite_path = tmp_path / "backend_smoke.sqlite"
    write_backend_smoke_sqlite(report, sqlite_path)
    with sqlite3.connect(sqlite_path) as connection:
        row_count = connection.execute("SELECT COUNT(*) FROM backend_smoke_rows").fetchone()[0]
        signature_count = connection.execute("SELECT COUNT(*) FROM bug_signatures").fetchone()[0]

    assert row_count == report["counts"]["backend_row_count"]
    assert signature_count == report["counts"]["bug_signature_count"]
