from crystalprobe.insight.cposs_promotion import cposs_promotion_markdown, cposs_promotion_report


def _annotations():
    return {
        "CBZ": {
            "smiles": "C",
            "common_name": "fixture",
            "flexibility_class": "rigid",
            "has_halogen": False,
            "has_charge": False,
            "is_chiral": False,
        }
    }


def test_cposs_promotion_blocks_incomplete_workpack_item():
    report = cposs_promotion_report(
        {
            "work_items": [
                {
                    "candidate_id": "cbz_a_vs_b",
                    "family": "CBZ",
                    "priority": "high",
                    "structure_a": {"block_id": "A"},
                    "structure_b": {"block_id": "B"},
                    "evidence_form": {"promotion_decision": "pending"},
                }
            ]
        },
        family_annotations=_annotations(),
    )

    assert report["promoted_count"] == 0
    assert report["rows"][0]["promotion_status"] == "blocked"
    assert report["milestones"][0]["remaining"] == 20
    completion = {row["field"]: row for row in report["field_completion"]}
    assert completion["experimental_stability_ordering"]["missing_count"] == 1
    assert completion["promotion_decision"]["complete_count"] == 1
    assert completion["citation_doi_or_url"]["missing_count"] == 1
    assert report["rows"][0]["next_required_fields"] == [
        "experimental_stability_ordering",
        "citation_doi_or_url",
        "source_license_a",
        "source_license_b",
        "has_disorder_a",
        "has_disorder_b",
        "curator",
        "reviewer",
    ]
    assert report["curation_queue"][0]["priority"] == "high"
    assert report["curation_queue"][0]["missing_count"] == 8
    assert report["family_summary"] == [
        {
            "family": "CBZ",
            "candidate_count": 1,
            "promoted_count": 0,
            "blocked_count": 1,
            "high_priority_blocked_count": 1,
        }
    ]


def test_cposs_promotion_builds_verified_pair_record():
    report = cposs_promotion_report(
        {
            "work_items": [
                {
                    "candidate_id": "cbz_a_vs_b",
                    "family": "CBZ",
                    "priority": "high",
                    "structure_a": {"block_id": "A"},
                    "structure_b": {"block_id": "B"},
                    "evidence_form": {
                        "experimental_stability_ordering": "A>B",
                        "temperature_K": "298",
                        "citation_doi": "10.0000/example",
                        "source_license_a": "CC-BY-4.0",
                        "source_license_b": "CC-BY-4.0",
                        "has_disorder_a": "false",
                        "has_disorder_b": "false",
                        "curator": "curator",
                        "reviewer": "reviewer",
                        "promotion_decision": "promote",
                    },
                }
            ]
        },
        family_annotations=_annotations(),
    )

    assert report["promoted_count"] == 1
    assert report["promoted_records"][0]["curation_status"] == "verified"


def test_cposs_promotion_markdown_includes_field_completion():
    report = cposs_promotion_report(
        {
            "work_items": [
                {
                    "candidate_id": "cbz_a_vs_b",
                    "family": "CBZ",
                    "priority": "high",
                    "structure_a": {"block_id": "A"},
                    "structure_b": {"block_id": "B"},
                    "evidence_form": {"promotion_decision": "pending"},
                }
            ]
        },
        family_annotations=_annotations(),
    )

    markdown = cposs_promotion_markdown(report)
    assert "## Evidence Field Completion" in markdown
    assert "## Family Summary" in markdown
    assert "## Curation Queue" in markdown
    assert "| `CBZ` | `1` | `0` | `1` | `1` |" in markdown
    assert "| `citation_doi_or_url` | `0` | `1` |" in markdown
    assert "| `cbz_a_vs_b` | `CBZ` | `high` | `8` |" in markdown
