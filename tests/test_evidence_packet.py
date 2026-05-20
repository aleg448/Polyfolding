from pathlib import Path

from crystalprobe.benchmark.dataset import load_manifest
from crystalprobe.benchmark.predictions import load_pair_energy_prediction_records
from crystalprobe.insight.evidence_packet import evidence_packet_markdown, evidence_packet_report, select_pair_for_packet


ROOT = Path(__file__).resolve().parents[1]


def test_evidence_packet_combines_motif_triage_prediction_and_blockers():
    dataset = load_manifest(ROOT / "data" / "benchmark" / "v0.1" / "manifest.jsonl")
    pair = select_pair_for_packet(dataset.pairs, "paracetamol_form_i_vs_form_ii_seed")
    predictions = {record.pair_id: record for record in load_pair_energy_prediction_records(ROOT / "examples" / "demo_predictions.jsonl")}

    report = evidence_packet_report(pair, prediction=predictions[pair.pair_id])

    assert report["status"] == "evidence_packet_blocked"
    assert report["headline_claim_gate"] == "blocked_until_verified"
    assert report["motif_prior"]["network_classification"] == "strong_h_bond_network"
    assert report["active_triage"]["recommended_action"] == "resolve_stability_evidence"
    assert report["prediction_and_abstention"]["status"] == "prediction_recorded"
    assert report["prediction_and_abstention"]["abstention"]["decision"] == "abstain_needs_verified_evidence"
    assert report["promotion_gate"]["blocker_count"] > 0


def test_evidence_packet_markdown_keeps_claim_gate_visible():
    dataset = load_manifest(ROOT / "data" / "benchmark" / "v0.1" / "manifest.jsonl")
    pair = select_pair_for_packet(dataset.pairs, "paracetamol_form_i_vs_form_ii_seed")
    markdown = evidence_packet_markdown(evidence_packet_report(pair))

    assert markdown.startswith("# CrystalProbe Evidence Packet: paracetamol_form_i_vs_form_ii_seed")
    assert "Headline claim gate: `blocked_until_verified`" in markdown
    assert "Prediction status: `prediction_not_available`" in markdown
    assert "An evidence packet is a promotion worklist" in markdown


def test_select_pair_for_packet_defaults_to_highest_priority_triage_item():
    dataset = load_manifest(ROOT / "data" / "benchmark" / "v0.1" / "manifest.jsonl")

    assert select_pair_for_packet(dataset.pairs).pair_id == "aspirin_form_i_vs_form_ii_seed"
