from crystalprobe.insight.medication_stereochemistry import (
    medication_stereochemistry_markdown,
    medication_stereochemistry_report,
)


def test_medication_stereochemistry_detects_paired_enantiomer_records():
    report = medication_stereochemistry_report(_autonomy_report(), _seed_ranking_report())

    target = report["targets"][0]
    assert report["enantiomer_scope_target_count"] == 1
    assert report["rankable_enantiomer_scope_target_count"] == 1
    assert target["stereochemistry_status"] == "paired_enantiomer_records_available"
    assert target["enantiomer_labeled_block_count"] == 2
    assert target["ranking_status"] == "ranked_within_backend"
    assert "do not collapse enantiomeric records into polymorph benchmark claims" in target["blockers"]


def test_medication_stereochemistry_markdown_renders_policy():
    markdown = medication_stereochemistry_markdown(
        medication_stereochemistry_report(_autonomy_report(), _seed_ranking_report())
    )

    assert markdown.startswith("# Medication Stereochemistry Scope")
    assert "Enantiomeric crystal comparison is a first-class" in markdown
    assert "`s_seed`" in markdown


def _autonomy_report():
    return {
        "targets": [
            {
                "target": "fixture",
                "claim_scopes": ["enantiomeric_crystal_comparison"],
                "solid_form_scope_counts": {
                    "single_enantiomer_s_or_plus": 1,
                    "single_enantiomer_r_or_minus": 1,
                },
                "blockers": ["resolve stereochemistry/enantiomer labels before calling records polymorphs"],
                "candidate_blocks": [
                    {
                        "block_id": "(S)-fixture",
                        "structure_id": "s_seed",
                        "stereochemical_scope": "single_enantiomer_s_or_plus",
                    },
                    {
                        "block_id": "(R)-fixture",
                        "structure_id": "r_seed",
                        "stereochemical_scope": "single_enantiomer_r_or_minus",
                    },
                ],
            }
        ]
    }


def _seed_ranking_report():
    return {
        "targets": [
            {
                "target": "fixture",
                "ranking_status": "ranked_within_backend",
                "ranked_backends": ["mace"],
            }
        ]
    }
