import json
from pathlib import Path

from crystalprobe.benchmark.dataset import load_manifest
from crystalprobe.benchmark.predictions import load_pair_energy_prediction_records
from crystalprobe.insight.evidence_packet import evidence_packet_report, select_pair_for_packet
from crystalprobe.insight.evidence_resolution import evidence_resolution_markdown, evidence_resolution_report


ROOT = Path(__file__).resolve().parents[1]


def _paracetamol_packet():
    dataset = load_manifest(ROOT / "data" / "benchmark" / "v0.1" / "manifest.jsonl")
    pair = select_pair_for_packet(dataset.pairs, "paracetamol_form_i_vs_form_ii_seed")
    predictions = {
        record.pair_id: record
        for record in load_pair_energy_prediction_records(ROOT / "examples" / "demo_predictions.jsonl")
    }
    return evidence_packet_report(pair, prediction=predictions[pair.pair_id])


def test_evidence_resolution_records_candidate_sources_without_promotion():
    candidates = json.loads(
        (ROOT / "data" / "curation" / "evidence_resolution_candidates_v0.1.json").read_text(encoding="utf-8")
    )
    report = evidence_resolution_report(_paracetamol_packet(), candidates)

    assert report["status"] == "evidence_resolution_candidate_recorded"
    assert report["promotion_decision"] == "do_not_promote_candidate_only"
    assert report["proposed_stability_ordering"] == "A>B"
    assert report["resolved_blocker_count"] == 7
    assert report["remaining_blocker_count"] == 2
    assert {blocker["field"] for blocker in report["remaining_blockers"]} == {"record", "human_review"}
    assert report["structure_candidates"]["A"]["source_id"] == "COD:7105573"
    assert report["structure_candidates"]["B"]["source_id"] == "COD:2105052"


def test_evidence_resolution_markdown_keeps_manual_review_gate_visible():
    candidates = json.loads(
        (ROOT / "data" / "curation" / "evidence_resolution_candidates_v0.1.json").read_text(encoding="utf-8")
    )
    markdown = evidence_resolution_markdown(evidence_resolution_report(_paracetamol_packet(), candidates))

    assert markdown.startswith("# CrystalProbe Evidence Resolution")
    assert "do_not_promote_candidate_only" in markdown
    assert "COD:7105573" in markdown
    assert "COD:2105052" in markdown
    assert "human_review" in markdown
    assert "A>B" in markdown
