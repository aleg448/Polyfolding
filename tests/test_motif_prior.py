from pathlib import Path

from crystalprobe.benchmark.dataset import load_manifest
from crystalprobe.insight.motif_prior import motif_prior_for_pair, motif_prior_markdown, motif_prior_report


ROOT = Path(__file__).resolve().parents[1]


def test_motif_prior_classifies_charge_assisted_networks():
    dataset = load_manifest(ROOT / "data" / "benchmark" / "v0.1" / "manifest.jsonl")
    glycine = next(pair for pair in dataset if pair.pair_id == "glycine_alpha_vs_gamma_seed")

    prior = motif_prior_for_pair(glycine)

    assert prior["network_classification"] == "charge_assisted_h_bond_network"
    assert "charge_assisted_h_bonding" in prior["motif_signals"]
    assert prior["claim_boundary"].startswith("motif priors are explanatory")


def test_motif_prior_report_keeps_claim_boundary_visible():
    dataset = load_manifest(ROOT / "data" / "benchmark" / "v0.1" / "manifest.jsonl")
    report = motif_prior_report(dataset.pairs)
    markdown = motif_prior_markdown(report)

    assert report["status"] == "motif_priors_recorded"
    assert report["pair_count"] == 5
    assert "Motif priors do not create experimental stability labels" in markdown
