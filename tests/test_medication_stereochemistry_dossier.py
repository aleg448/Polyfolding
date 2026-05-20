from crystalprobe.insight.medication_stereochemistry_dossier import (
    medication_stereochemistry_dossier_markdown,
    medication_stereochemistry_dossier_report,
)


def test_medication_stereochemistry_dossier_records_missing_scope_fields():
    report = medication_stereochemistry_dossier_report(
        _stereochemistry(),
        _seed_ranking(),
        _evidence_manifest(stereochemistry_decision="blocked: unresolved", promotion_decision="do_not_promote"),
    )

    dossier = report["dossiers"][0]
    assert report["dossier_count"] == 1
    assert dossier["dossier_status"] == "curation_required"
    assert "local_block_stereochemistry_map" in dossier["present_fields"]
    assert "ranking_interpretation" in dossier["present_fields"]
    assert "source_racemate_or_enantiomer_scope" in dossier["missing_fields"]
    assert "promotion_decision" in dossier["missing_fields"]
    assert "Keep S/R rankings below polymorph benchmark status" in dossier["next_actions"][-1]


def test_medication_stereochemistry_dossier_can_be_claim_scope_ready():
    report = medication_stereochemistry_dossier_report(
        _stereochemistry(blockers=[]),
        _seed_ranking(),
        _evidence_manifest(
            stereochemistry_decision="source maps S and R single-enantiomer records explicitly",
            promotion_decision="promote_enantiomeric_claim_scope",
        ),
    )

    dossier = report["dossiers"][0]
    assert dossier["dossier_status"] == "claim_scope_ready"
    assert dossier["missing_fields"] == []


def test_medication_stereochemistry_dossier_markdown_renders_actions():
    markdown = medication_stereochemistry_dossier_markdown(
        medication_stereochemistry_dossier_report(
            _stereochemistry(),
            _seed_ranking(),
            _evidence_manifest(stereochemistry_decision="blocked", promotion_decision="do_not_promote"),
        )
    )

    assert markdown.startswith("# Medication Stereochemistry Dossier")
    assert "Lock whether each source form is racemic" in markdown
    assert "`modafinil_s`" in markdown


def _stereochemistry(*, blockers=None):
    return {
        "targets": [
            {
                "target": "modafinil",
                "stereochemistry_status": "paired_enantiomer_records_available",
                "ranked_backends": ["mace"],
                "blockers": blockers
                if blockers is not None
                else ["do not collapse enantiomeric records into polymorph benchmark claims"],
                "enantiomer_labeled_blocks": [
                    {
                        "block_id": "(S)-modafinil",
                        "structure_id": "modafinil_s",
                        "stereochemical_scope": "single_enantiomer_s_or_plus",
                        "ccdc_deposition": "CCDC 1",
                    },
                    {
                        "block_id": "(R)-modafinil",
                        "structure_id": "modafinil_r",
                        "stereochemical_scope": "single_enantiomer_r_or_minus",
                        "ccdc_deposition": "CCDC 2",
                    },
                ],
            }
        ]
    }


def _seed_ranking():
    return {
        "targets": [
            {
                "target": "modafinil",
                "ranking_status": "ranked_within_backend",
                "backend_rankings": [
                    {
                        "backend": "mace",
                        "rows": [
                            {
                                "rank": 1,
                                "structure_id": "modafinil_r",
                                "delta_ev_per_formula_unit": 0.0,
                            }
                        ],
                    }
                ],
            }
        ]
    }


def _evidence_manifest(*, stereochemistry_decision, promotion_decision):
    return {
        "records": [
            {
                "target": "modafinil",
                "form_label_map": {"mapping_status": "mapped", "local_candidate_blocks": ["(S)-modafinil"]},
                "stereochemistry_decision": stereochemistry_decision,
                "promotion_decision": promotion_decision,
            }
        ]
    }
