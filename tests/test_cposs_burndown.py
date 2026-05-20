from crystalprobe.insight.cposs_burndown import (
    cposs_promotion_burndown_markdown,
    cposs_promotion_burndown_report,
)


def test_cposs_promotion_burndown_selects_target_sized_candidate_plan():
    report = cposs_promotion_burndown_report(
        _promotion_report(),
        _block_mapping_report(),
        target_pair_count=2,
    )

    assert report["status"] == "burndown_required"
    assert report["remaining_to_target"] == 2
    assert report["selected_candidate_count"] == 2
    assert [row["candidate_id"] for row in report["candidate_plan"]] == ["cbz_a_vs_b", "ibp_a_vs_b"]
    assert {row["block_id"] for row in report["block_action_plan"]} == {"CBZ01", "CBZ03", "IBP01", "IBP06"}
    assert report["blocker_summary"][0]["blocker"] == "lock block-to-form mapping"


def test_cposs_promotion_burndown_marks_reached_target_without_selected_work():
    report = cposs_promotion_burndown_report(
        {**_promotion_report(), "promoted_count": 20},
        _block_mapping_report(),
        target_pair_count=20,
    )

    assert report["status"] == "target_reached"
    assert report["remaining_to_target"] == 0
    assert report["candidate_plan"] == []
    assert report["block_action_plan"] == []


def test_cposs_promotion_burndown_markdown_renders_action_tables():
    markdown = cposs_promotion_burndown_markdown(
        cposs_promotion_burndown_report(
            _promotion_report(),
            _block_mapping_report(),
            target_pair_count=1,
        )
    )

    assert markdown.startswith("# CPOSS Promotion Burn-Down")
    assert "## Candidate Plan" in markdown
    assert "## Block Action Plan" in markdown
    assert "`cbz_a_vs_b`" in markdown
    assert "The promotion gate remains canonical" in markdown


def _promotion_report():
    return {
        "promoted_count": 0,
        "curation_queue": [
            {
                "candidate_id": "ibp_a_vs_b",
                "family": "IBP",
                "priority": "high",
                "promotion_status": "literature_mapped_candidate",
                "upgrade_requirements": ["resolve license"],
            },
            {
                "candidate_id": "cbz_a_vs_b",
                "family": "CBZ",
                "priority": "high",
                "promotion_status": "literature_mapped_candidate",
                "upgrade_requirements": ["resolve disorder"],
            },
            {
                "candidate_id": "acr_a_vs_b",
                "family": "ACR",
                "priority": "medium",
                "promotion_status": "literature_mapped_candidate",
                "upgrade_requirements": ["resolve license"],
            },
        ],
    }


def _block_mapping_report():
    return {
        "candidate_rows": [
            _candidate("cbz_a_vs_b", "CBZ", "high", "CBZ01", "CBZ03", 1.5),
            _candidate("ibp_a_vs_b", "IBP", "high", "IBP01", "IBP06", 2.5),
            _candidate("acr_a_vs_b", "ACR", "medium", "ACR01", "ACR02", 0.5),
        ],
        "block_rows": [
            _block("CBZ", "CBZ01"),
            _block("CBZ", "CBZ03"),
            _block("IBP", "IBP01"),
            _block("IBP", "IBP06"),
            _block("ACR", "ACR01"),
            _block("ACR", "ACR02"),
        ],
    }


def _candidate(candidate_id, family, priority, structure_a, structure_b, gap):
    return {
        "candidate_id": candidate_id,
        "family": family,
        "priority": priority,
        "mapping_ready": False,
        "structure_a": structure_a,
        "structure_b": structure_b,
        "model_gap_kj_mol_per_formula_unit": gap,
        "blockers": ["lock block-to-form mapping"],
    }


def _block(family, block_id):
    return {
        "family": family,
        "block_id": block_id,
        "mapping_status": "unmapped",
        "mapping_confidence": "unknown",
        "promotion_ready": False,
        "blockers": ["lock block-to-form mapping"],
    }
