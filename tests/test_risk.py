from crystalprobe.insight.risk import risk_register_markdown, risk_register_report


def test_risk_register_tracks_open_claim_license_and_energy_risks():
    report = risk_register_report(
        publication_readiness={
            "policy": [
                "CrystalProbe is positioned as an audit, curation, calibration, and claim-readiness layer that complements FastCSP-style crystal-landscape generation."
            ]
        },
        release_boundary={"counts": {"license_review_required": 2, "local_only": 1}},
        cposs_promotion={"promoted_count": 0, "literature_mapped_count": 25},
        cposs_block_mapping={"candidate_mapping_ready_count": 0},
        cposs_promotion_burndown={
            "remaining_to_target": 20,
            "selected_candidate_count": 20,
            "selected_block_count": 27,
        },
        fingerprint_plan={
            "figures": [
                {"figure_id": "uncertainty_calibration", "status": "blocked"},
                {"figure_id": "medication_stereochemistry", "status": "ready"},
            ]
        },
        medication_stereochemistry={
            "enantiomer_scope_target_count": 1,
            "rankable_enantiomer_scope_target_count": 1,
            "targets": [{"blockers": ["do not collapse enantiomeric records into polymorph benchmark claims"]}],
        },
        medication_stereochemistry_dossier={"dossier_count": 1, "ready_for_claim_scope_count": 0},
    )

    assert report["status"] == "risk_register_recorded"
    assert report["risk_count"] == 5
    assert report["critical_risk_count"] == 2
    risks = {risk["risk_id"]: risk for risk in report["risks"]}
    assert risks["overclaiming_candidate_evidence"]["status"] == "open"
    assert risks["ccdc_csd_license_boundary"]["status"] == "open"
    assert risks["cross_backend_energy_interpretation"]["status"] == "watch"
    assert risks["medication_stereochemistry_scope_confusion"]["status"] == "open"
    assert "0 of 1 stereochemistry dossiers ready" in risks["medication_stereochemistry_scope_confusion"]["evidence"]
    assert risks["fastcsp_positioning_drift"]["status"] == "mitigated"
    assert "20 burn-down candidates covering 27 block rows" in risks["overclaiming_candidate_evidence"]["evidence"]


def test_risk_register_can_mark_release_and_claim_risks_mitigated():
    report = risk_register_report(
        publication_readiness={"policy": ["missing"]},
        release_boundary={"counts": {"license_review_required": 0, "local_only": 0}},
        cposs_promotion={"promoted_count": 20, "literature_mapped_count": 0},
        cposs_block_mapping={"candidate_mapping_ready_count": 20},
        fingerprint_plan={"figures": [{"figure_id": "uncertainty_calibration", "status": "ready"}]},
        medication_stereochemistry={"enantiomer_scope_target_count": 0},
        medication_stereochemistry_dossier={"dossier_count": 0, "ready_for_claim_scope_count": 0},
    )

    risks = {risk["risk_id"]: risk for risk in report["risks"]}
    assert risks["overclaiming_candidate_evidence"]["status"] == "mitigated"
    assert risks["ccdc_csd_license_boundary"]["status"] == "mitigated"
    assert risks["cross_backend_energy_interpretation"]["status"] == "mitigated"
    assert risks["medication_stereochemistry_scope_confusion"]["status"] == "mitigated"
    assert risks["fastcsp_positioning_drift"]["status"] == "open"


def test_risk_register_markdown_renders_policy_and_table():
    markdown = risk_register_markdown(
        risk_register_report(
            publication_readiness={"policy": []},
            release_boundary={"counts": {"license_review_required": 1, "local_only": 0}},
            cposs_promotion={"promoted_count": 0, "literature_mapped_count": 1},
            cposs_block_mapping={"candidate_mapping_ready_count": 0},
            fingerprint_plan={"figures": []},
            medication_stereochemistry={"enantiomer_scope_target_count": 1},
            medication_stereochemistry_dossier={"dossier_count": 1, "ready_for_claim_scope_count": 0},
        )
    )

    assert markdown.startswith("# CrystalProbe Risk Register")
    assert "overclaiming_candidate_evidence" in markdown
    assert "ccdc_csd_license_boundary" in markdown
    assert "medication_stereochemistry_scope_confusion" in markdown
    assert "Use the CPOSS promotion burn-down" in markdown
    assert "claim-readiness layer around CSP outputs" in markdown
