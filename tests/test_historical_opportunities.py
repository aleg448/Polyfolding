import json
from pathlib import Path

from crystalprobe.insight.historical_opportunities import (
    historical_opportunity_markdown,
    historical_opportunity_report,
    implementation_targets,
    top_dependency_light_targets,
)


ROOT = Path(__file__).resolve().parents[1]


def test_historical_opportunity_matrix_ranks_claim_gated_targets():
    matrix = json.loads((ROOT / "data" / "curation" / "historical_opportunity_matrix_v0.1.json").read_text())
    report = historical_opportunity_report(matrix)

    assert report["status"] == "historical_opportunities_ranked"
    assert "active_evidence_triage" in implementation_targets(report, limit=5)
    assert "free_energy_probe" in implementation_targets(report)
    assert all("claim_gate" in row for row in report["opportunities"])


def test_historical_opportunity_markdown_surfaces_policy():
    matrix = json.loads((ROOT / "data" / "curation" / "historical_opportunity_matrix_v0.1.json").read_text())
    markdown = historical_opportunity_markdown(historical_opportunity_report(matrix))

    assert markdown.startswith("# CrystalProbe Historical Opportunity Matrix")
    assert "Historical methods are implementation opportunities" in markdown
    assert "`motif_prior`" in markdown


def test_dependency_light_targets_exclude_high_claim_risk_items():
    rows = [
        {"opportunity_id": "a", "historical_thread": "A", "older_source": "A", "old_blocker": "A", "modern_enabler": "A", "implementation_target": "safe", "publication_value": 5, "implementation_readiness": 5, "claim_risk": 2, "claim_gate": "gate"},
        {"opportunity_id": "b", "historical_thread": "B", "older_source": "B", "old_blocker": "B", "modern_enabler": "B", "implementation_target": "risky", "publication_value": 5, "implementation_readiness": 5, "claim_risk": 5, "claim_gate": "gate"},
    ]

    assert top_dependency_light_targets(rows) == ["safe"]
