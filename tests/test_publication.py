from crystalprobe.insight.publication import publication_readiness_markdown, publication_readiness_report


def test_publication_readiness_blocks_unverified_and_restricted_artifacts():
    report = publication_readiness_report(
        cposs_promotion={"promoted_count": 0},
        cposs_block_mapping={"candidate_count": 25, "candidate_mapping_ready_count": 0},
        fingerprint_plan={"figures": [{"figure_id": "calibration", "status": "blocked"}]},
        release_boundary={"counts": {"candidate_public": 3, "license_review_required": 2, "local_only": 1}},
        execution_unblock={"blocker_count": 1, "approval_batch": ["Run pending backend commands."]},
        handoff={"human_input_needed": ["Confirm medication CIF release policy."]},
        medication_stereochemistry_dossier={"dossier_count": 1, "ready_for_claim_scope_count": 0},
    )

    assert report["status"] == "publication_blocked"
    assert report["ready"] is False
    assert report["blocked_gate_count"] == 7
    assert "Run pending backend commands." in report["approval_batch"]
    assert any("Curate and promote 20 verified CPOSS pairs" in step for step in report["next_publication_steps"])
    assert any("Lock block-to-experimental-form mappings for 25 CPOSS candidate pairs" in step for step in report["next_publication_steps"])


def test_publication_readiness_can_pass_all_gates():
    report = publication_readiness_report(
        cposs_promotion={"promoted_count": 20},
        cposs_block_mapping={"candidate_count": 20, "candidate_mapping_ready_count": 20},
        fingerprint_plan={"figures": [{"figure_id": "composition", "status": "ready"}]},
        release_boundary={"counts": {"candidate_public": 3, "license_review_required": 0, "local_only": 0}},
        execution_unblock={"blocker_count": 0, "approval_batch": []},
        handoff={"human_input_needed": []},
        medication_stereochemistry_dossier={"dossier_count": 1, "ready_for_claim_scope_count": 1},
    )

    assert report["status"] == "publication_ready"
    assert report["blocked_gate_count"] == 0
    assert report["next_publication_steps"] == ["All publication gates passed; prepare final release review."]


def test_publication_readiness_markdown_renders_gates_and_policy():
    markdown = publication_readiness_markdown(
        publication_readiness_report(
            cposs_promotion={"promoted_count": 0},
            fingerprint_plan={
                "figures": [
                    {"figure_id": "composition", "status": "blocked"},
                    {"figure_id": "medication_stereochemistry", "status": "ready"},
                ]
            },
            release_boundary={"counts": {"candidate_public": 1, "license_review_required": 1, "local_only": 0}},
            execution_unblock={"blocker_count": 0, "approval_batch": []},
            handoff={"human_input_needed": []},
            medication_stereochemistry_dossier={"dossier_count": 1, "ready_for_claim_scope_count": 0},
        )
    )

    assert markdown.startswith("# CrystalProbe Publication Readiness")
    assert "verified_pair_milestone_20" in markdown
    assert "Publication readiness requires verified benchmark evidence" in markdown
    assert "complements FastCSP-style crystal-landscape generation" in markdown
    assert "absolute energies are not a shared thermodynamic scale" in markdown
    assert "Ready medication claim-scope panels: medication_stereochemistry" in markdown
    assert "Medication stereochemistry panels are claim-scope artifacts" in markdown
    assert "medication_stereochemistry_dossier" in markdown
    assert "0 of 1 medication stereochemistry dossiers are claim-scope ready" in markdown
