import json
import sqlite3
from pathlib import Path

from crystalprobe.insight.evidence_atlas import (
    build_evidence_atlas,
    evidence_atlas_explorer_html,
    evidence_atlas_markdown,
    write_evidence_atlas_sqlite,
)


ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: str) -> dict:
    full_path = ROOT / path
    if not full_path.exists():
        return {}
    return json.loads(full_path.read_text(encoding="utf-8"))


def _atlas():
    return build_evidence_atlas(
        manifest_path=ROOT / "data" / "benchmark" / "v0.1" / "manifest.jsonl",
        predictions_path=ROOT / "examples" / "demo_predictions.jsonl",
        evidence_packet=_load_json("outputs/crystalprobe_evidence_packet.json"),
        evidence_resolution=_load_json("outputs/crystalprobe_evidence_resolution.json"),
        molecule_viewers=_load_json("outputs/crystalprobe_molecule_viewers.json"),
        release_boundary=_load_json("outputs/crystalprobe_release_boundary.json"),
    )


def test_evidence_atlas_normalizes_manifest_predictions_viewers_and_blockers():
    report = _atlas()

    assert report["status"] == "evidence_atlas_built"
    assert report["counts"]["molecules"] == 5
    assert report["counts"]["polymorph_pairs"] == 5
    assert report["counts"]["structures"] >= 12
    assert report["counts"]["evidence_sources"] >= 3
    assert report["counts"]["viewer_links"] == 2
    assert report["counts"]["predictions"] == 2
    paracetamol = {
        row["pair_id"]: row for row in report["tables"]["polymorph_pairs"]
    }["paracetamol_form_i_vs_form_ii_seed"]
    assert paracetamol["headline_claim_gate"] == "blocked_until_verified"
    assert paracetamol["promotion_decision"] == "do_not_promote_candidate_only"
    assert paracetamol["viewer_count"] == 2
    assert any(row["source_id"] == "COD:7105573" for row in report["tables"]["structures"])
    assert any(row["status"] == "candidate_resolved_not_promoted" for row in report["tables"]["blockers"])


def test_evidence_atlas_writes_queryable_sqlite(tmp_path):
    report = _atlas()
    sqlite_path = tmp_path / "atlas.sqlite"

    write_evidence_atlas_sqlite(report, sqlite_path)

    with sqlite3.connect(sqlite_path) as connection:
        pair_count = connection.execute("select count(*) from polymorph_pairs").fetchone()[0]
        cod_rows = connection.execute(
            "select count(*) from structures where source_id in ('COD:7105573', 'COD:2105052')"
        ).fetchone()[0]
        viewer_rows = connection.execute("select count(*) from viewer_links").fetchone()[0]
        artifact_rows = connection.execute(
            "select count(*) from artifacts where category = 'candidate_public'"
        ).fetchone()[0]

    assert pair_count == 5
    assert cod_rows == 2
    assert viewer_rows == 2
    assert artifact_rows >= 1


def test_evidence_atlas_markdown_and_explorer_are_claim_safe():
    report = _atlas()
    markdown = evidence_atlas_markdown(
        report,
        sqlite_path="outputs/crystalprobe_evidence_atlas.sqlite",
        explorer_path="docs/evidence_atlas.html",
    )
    html = evidence_atlas_explorer_html(report)

    assert "select pair_id, curation_status, blocker_count" in markdown
    assert "paracetamol_form_i_vs_form_ii_seed" in html
    assert "COD/JSmol" in html
    assert "candidate_unverified" in html
    assert "blocked_until_verified" in html
    assert "_atom_site" not in html
