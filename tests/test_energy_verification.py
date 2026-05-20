import json
from pathlib import Path

from crystalprobe.insight.energy_verification import energy_verification_markdown, energy_verification_report
from crystalprobe.insight.molecule_bug_hunt import molecule_bug_hunt_report


ROOT = Path(__file__).resolve().parents[1]


def _stress_report():
    catalog = json.loads((ROOT / "data" / "curation" / "molecule_bug_hunt_stress_v0.1.json").read_text(encoding="utf-8"))
    return molecule_bug_hunt_report(catalog)


def test_energy_verification_blocks_claims_without_verified_calibration():
    report = energy_verification_report(
        manifest_path=ROOT / "data" / "benchmark" / "v0.1" / "manifest.jsonl",
        predictions_path=ROOT / "examples" / "demo_predictions.jsonl",
        molecule_bug_hunt=_stress_report(),
    )

    assert report["status"] == "energy_verification_blocked_until_verified_calibration"
    assert report["counts"]["prediction_rows"] == 2
    assert report["counts"]["verified_pairs"] == 0
    assert report["counts"]["stress_molecule_count"] >= 35
    assert report["counts"]["ood_prediction_count"] == 1
    assert report["counts"]["non_verified_prediction_count"] == 2
    checks = {issue["check"] for issue in report["issues"]}
    assert "verified_calibration_absent" in checks
    assert "ood_energy_row" in checks
    assert "missing_demo_prediction" in checks
    assert {row["claim_decision"] for row in report["energy_rows"]} == {"abstain_non_verified_record"}


def test_energy_verification_markdown_keeps_energy_policy_visible():
    report = energy_verification_report(
        manifest_path=ROOT / "data" / "benchmark" / "v0.1" / "manifest.jsonl",
        predictions_path=ROOT / "examples" / "demo_predictions.jsonl",
        molecule_bug_hunt=_stress_report(),
    )
    markdown = energy_verification_markdown(report)

    assert markdown.startswith("# CrystalProbe Energy Verification")
    assert "verified_calibration_absent" in markdown
    assert "abstain_non_verified_record" in markdown
    assert "Absolute energies across MACE, AIMNet2, UMA, and demo backends must not be compared directly." in markdown
