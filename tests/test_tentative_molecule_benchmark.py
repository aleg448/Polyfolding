import sqlite3
from pathlib import Path

from crystalprobe.insight.tentative_molecule_benchmark import (
    build_tentative_molecule_benchmark,
    load_molecule_panel,
    tentative_molecule_benchmark_markdown,
    write_tentative_molecule_benchmark_sqlite,
)


ROOT = Path(__file__).resolve().parents[1]
STRESS_CATALOG = ROOT / "data" / "curation" / "molecule_bug_hunt_stress_v0.1.json"
PANEL = ROOT / "data" / "curation" / "molecule_benchmark_panel_v0.1.csv"


def test_load_molecule_panel_combines_stress_catalog_and_csv_panel():
    records = load_molecule_panel(STRESS_CATALOG, PANEL)
    ids = {record.molecule_id for record in records}

    assert len(records) >= 80
    assert "cholesterol" in ids
    assert "sodium_acetate" in ids
    assert "glucose_pyranose" in ids


def test_tentative_molecule_benchmark_keeps_claim_boundary_and_backend_preflight():
    report = build_tentative_molecule_benchmark(load_molecule_panel(STRESS_CATALOG, PANEL))

    assert report["candidate_payload_enabled"] is True
    assert report["claim_boundary"] == "tentative_software_benchmark_not_scientific_evidence"
    assert report["counts"]["molecule_count"] >= 80
    assert report["counts"]["claim_ready_count"] == 0
    assert "warning_count" in report["counts"]
    assert report["tool_counts"]["smiles_lexical"] == report["counts"]["molecule_count"]
    assert report["tool_counts"]["rdkit_conformer"] == report["counts"]["molecule_count"]
    assert report["conformer_generation"]["generated_count"] >= 0
    assert {"mace_off", "aimnet2", "uma", "fastcsp"}.issubset(report["tool_counts"])
    signatures = {signature["issue_signature"] for signature in report["bug_signatures"]}
    assert signatures & {
        "optional_backend_missing_dependency",
        "backend_blocked_no_generated_conformers",
        "backend_execution_not_requested",
    }
    assert signatures & {
        "optional_conformer_generator_missing_dependency",
        "rdkit_embed_failure",
        "rdkit_parse_failure",
        "rdkit_uff_not_converged",
    } or report["conformer_generation"]["generated_count"] > 0
    lexical_rows = {
        row["molecule_id"]: row
        for row in report["benchmark_rows"]
        if row["tool"] == "smiles_lexical"
    }
    assert lexical_rows["glycine_zwitterion"]["status"] == "passed"
    assert lexical_rows["ammonium"]["status"] == "passed"
    synthetic_warning = {
        "issue_signature": "fixture_warning",
        "status": "warning",
        "molecule_id": "fixture",
        "tool": "fixture_tool",
        "detail": "warning detail",
    }
    from crystalprobe.insight.tentative_molecule_benchmark import _bug_signatures

    assert _bug_signatures([synthetic_warning])[0]["severity"] == "warning"


def test_tentative_molecule_benchmark_markdown_and_sqlite(tmp_path):
    report = build_tentative_molecule_benchmark(load_molecule_panel(STRESS_CATALOG, PANEL))
    markdown = tentative_molecule_benchmark_markdown(report)

    assert markdown.startswith("# CrystalProbe Tentative Molecule Benchmark")
    assert "Claim-ready rows: `0`" in markdown
    assert "Warning rows:" in markdown
    assert "Generated conformers:" in markdown
    assert "Optional scientific backends" in markdown

    sqlite_path = tmp_path / "benchmark.sqlite"
    write_tentative_molecule_benchmark_sqlite(report, sqlite_path)
    with sqlite3.connect(sqlite_path) as connection:
        row_count = connection.execute("SELECT COUNT(*) FROM molecule_benchmark_rows").fetchone()[0]
        signature_count = connection.execute("SELECT COUNT(*) FROM bug_signatures").fetchone()[0]

    assert row_count == report["counts"]["tool_row_count"]
    assert signature_count == report["counts"]["bug_signature_count"]
