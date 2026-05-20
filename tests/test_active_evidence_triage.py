from pathlib import Path

from crystalprobe.benchmark.dataset import load_manifest
from crystalprobe.insight.active_evidence_triage import (
    active_evidence_triage_markdown,
    active_evidence_triage_report,
    triage_items_from_pairs,
)


ROOT = Path(__file__).resolve().parents[1]


def test_active_evidence_triage_prioritizes_ambiguous_draft_records():
    dataset = load_manifest(ROOT / "data" / "benchmark" / "v0.1" / "manifest.jsonl")
    report = active_evidence_triage_report(triage_items_from_pairs(dataset.pairs))

    assert report["status"] == "active_evidence_triage_recorded"
    assert report["item_count"] == 5
    assert {item["recommended_action"] for item in report["next_batch"]} == {"resolve_stability_evidence"}
    assert all(item["evidence_status"] == "draft" for item in report["items"])


def test_active_evidence_triage_markdown_says_priority_is_not_claim():
    report = active_evidence_triage_report(
        [
            {
                "item_id": "fixture",
                "molecule": "fixture",
                "evidence_status": "candidate_unverified",
                "stability_ordering": "ambiguous",
                "license_status": "unknown",
                "issue_count": 3,
            }
        ]
    )
    markdown = active_evidence_triage_markdown(report)

    assert markdown.startswith("# CrystalProbe active evidence triage")
    assert "Triage priority is not a scientific claim" in markdown
