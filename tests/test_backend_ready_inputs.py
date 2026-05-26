import hashlib
import sqlite3

from crystalprobe.insight.backend_ready_inputs import (
    backend_ready_inputs_markdown,
    backend_ready_inputs_report,
    write_backend_ready_inputs_sqlite,
)


def _conformer_report(tmp_path):
    ready = tmp_path / "water.xyz"
    ready.write_text("3\nwater\nO 0 0 0\nH 0 0 1\nH 0 1 0\n", encoding="utf-8")
    warning = tmp_path / "cholesterol.xyz"
    warning.write_text("2\nwarning\nC 0 0 0\nH 1 0 0\n", encoding="utf-8")
    return {
        "generator": "rdkit_etkdg_v3",
        "claim_boundary": "generated_conformer_software_fixture_not_scientific_evidence",
        "rows": [
            {
                "molecule_id": "water",
                "common_name": "water",
                "smiles": "O",
                "status": "generated",
                "generator": "rdkit_etkdg_v3",
                "issue_signature": "none",
                "detail": "generated",
                "atom_count": 3,
                "heavy_atom_count": 1,
                "coordinate_payload": "written_local_generated_xyz",
                "xyz_path": str(ready),
                "metrics": {"span_x": 1.0},
            },
            {
                "molecule_id": "cholesterol",
                "common_name": "cholesterol",
                "smiles": "C",
                "status": "warning",
                "generator": "rdkit_etkdg_v3",
                "issue_signature": "rdkit_uff_not_converged",
                "detail": "UFF did not converge.",
                "atom_count": 2,
                "heavy_atom_count": 1,
                "coordinate_payload": "written_local_generated_xyz",
                "xyz_path": str(warning),
                "metrics": {},
            },
            {
                "molecule_id": "missing",
                "common_name": "missing",
                "smiles": "C",
                "status": "generated",
                "generator": "rdkit_etkdg_v3",
                "issue_signature": "none",
                "detail": "generated",
                "atom_count": 1,
                "heavy_atom_count": 1,
                "coordinate_payload": "not_written",
                "xyz_path": "",
                "metrics": {},
            },
        ],
    }


def test_backend_ready_inputs_hashes_generated_xyz_and_keeps_claim_boundary(tmp_path):
    report = backend_ready_inputs_report(_conformer_report(tmp_path), source_report_path="outputs/local.json")
    by_id = {row["molecule_id"]: row for row in report["rows"]}

    expected_digest = hashlib.sha256((tmp_path / "water.xyz").read_bytes()).hexdigest()
    assert report["counts"]["ready_count"] == 1
    assert report["counts"]["warning_count"] == 1
    assert report["counts"]["blocked_count"] == 1
    assert report["counts"]["claim_ready_count"] == 0
    assert by_id["water"]["sha256"] == expected_digest
    assert by_id["water"]["review_status"] == "candidate_unverified"
    assert by_id["water"]["claim_boundary"] == "backend_ready_generated_conformer_input_not_scientific_evidence"
    assert by_id["cholesterol"]["status"] == "warning"
    assert by_id["missing"]["issue_signature"] == "generated_coordinate_payload_missing"


def test_backend_ready_inputs_markdown_and_sqlite(tmp_path):
    report = backend_ready_inputs_report(_conformer_report(tmp_path))
    markdown = backend_ready_inputs_markdown(report)

    assert markdown.startswith("# CrystalProbe Backend-Ready Inputs")
    assert "Claim-ready rows: `0`" in markdown
    assert "candidate_unverified" in markdown
    assert "backend inputs for software smoke tests" in markdown

    sqlite_path = tmp_path / "backend_ready.sqlite"
    write_backend_ready_inputs_sqlite(report, sqlite_path)
    with sqlite3.connect(sqlite_path) as connection:
        row_count = connection.execute("SELECT COUNT(*) FROM backend_ready_inputs").fetchone()[0]
        signature_count = connection.execute("SELECT COUNT(*) FROM bug_signatures").fetchone()[0]

    assert row_count == report["counts"]["row_count"]
    assert signature_count == report["counts"]["bug_signature_count"]
