from crystalprobe.insight.evidence_tiers import classify_evidence_tier, evidence_tier_markdown, evidence_tier_report


def test_classify_blocks_missing_coordinates():
    tier = classify_evidence_tier({"target": "lisdexamfetamine dimesylate", "has_atom_coordinates": False})

    assert tier.tier == "blocked_no_coordinates"
    assert tier.status == "blocked"
    assert "MLIP measurement" in tier.blocked_claims


def test_classify_guardrailed_pilot_without_human_validation():
    tier = classify_evidence_tier(
        {
            "target": "AMPETP",
            "has_atom_coordinates": True,
            "backend_count": 3,
            "has_sensitivity_grid": True,
            "has_therapeutic_contrast": True,
            "has_source_provenance": True,
            "license_clean_for_redistribution": False,
            "human_database_validation": False,
            "experimental_stability_evidence": False,
        }
    )

    assert tier.tier == "agi_assisted_guardrailed_pilot"
    assert tier.status == "usable_with_guardrails"
    assert "verified polymorph benchmark" in tier.blocked_claims


def test_classify_verified_benchmark_candidate_requires_full_evidence():
    tier = classify_evidence_tier(
        {
            "target": "validated pair",
            "has_atom_coordinates": True,
            "backend_count": 2,
            "license_clean_for_redistribution": True,
            "human_database_validation": True,
            "experimental_stability_evidence": True,
        }
    )

    assert tier.tier == "verified_benchmark_candidate"
    assert tier.status == "promotable"


def test_evidence_tier_markdown_lists_policy_and_targets():
    report = evidence_tier_report(
        [
            {"target": "missing", "has_atom_coordinates": False},
            {
                "target": "pilot",
                "has_atom_coordinates": True,
                "backend_count": 2,
                "has_sensitivity_grid": True,
                "has_therapeutic_contrast": True,
                "has_source_provenance": True,
            },
        ]
    )
    markdown = evidence_tier_markdown(report)

    assert markdown.startswith("# CrystalProbe Evidence Tiers")
    assert "AGI-assisted curation" in markdown
    assert "blocked_no_coordinates" in markdown
    assert "agi_assisted_guardrailed_pilot" in markdown
