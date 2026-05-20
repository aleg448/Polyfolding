from pathlib import Path

from crystalprobe.insight.public_demo import run_public_demo


def test_public_demo_writes_claim_gated_report(tmp_path):
    report = run_public_demo(output_dir=tmp_path, backend_smoke="never")

    assert (tmp_path / "public_demo_report.json").exists()
    assert (tmp_path / "public_demo_report.md").exists()
    assert (tmp_path / "figures" / "claim_gate.svg").exists()
    assert (tmp_path / "figures" / "pipeline.svg").exists()
    assert (tmp_path / "figures" / "backend_readiness.svg").exists()
    assert (tmp_path / "figures" / "provenance_ledger.svg").exists()
    assert (tmp_path / "figures" / "calibration_reliability.svg").exists()
    assert (tmp_path / "figures" / "energy_uncertainty.svg").exists()
    assert report["claim_gate"]["decision"] == "blocked_headline_benchmark_claims_until_verified_records_exist"
    assert report["dataset"]["statuses"]["draft"] == 5
    assert {row["label"] for row in report["claim_gate"]["rows"]} == {"candidate", "reviewed", "verified"}
    assert report["quick_benchmark"]["evaluated"] == 0
    assert "draft/unverified" in (tmp_path / "figures" / "energy_uncertainty.svg").read_text(encoding="utf-8")
    assert "No verified calibration points yet" in (tmp_path / "figures" / "calibration_reliability.svg").read_text(encoding="utf-8")


def test_public_case_study_exposes_iso_grade_artifacts():
    text = Path("CASE_STUDY.md").read_text(encoding="utf-8")

    assert "python scripts\\run_public_demo.py --backend-smoke auto" in text
    assert "flowchart LR" in text
    assert "outputs/public_demo/figures/energy_uncertainty.svg" in text
    assert "| candidate |" in text
    assert "What Molecular Prediction Systems Must Prove Before They Are Useful In Drug Discovery" in text
