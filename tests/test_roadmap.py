from crystalprobe.insight.roadmap import roadmap_status_markdown, roadmap_status_report


def test_roadmap_status_report_maps_deliverables():
    report = roadmap_status_report(
        project_status={
            "ampetp": {"readiness_status": "paper_pilot_ready"},
            "verification": {"latest_local_test_summary": "1 passed", "docker_status": "fairchem_omc25_uma_ampetp_cuda_verified"},
        },
        readiness={"status": "paper_pilot_ready"},
        cposs_bridge={"family_count": 2, "structure_count": 16},
        has_preprint_draft=True,
        has_joss_draft=True,
        has_fastcsp_plan=True,
        has_release_boundary=True,
        has_cposs_pair_candidates=True,
        has_cposs_pair_triage=True,
        has_cposs_candidate_cards=True,
        has_cposs_evidence_workpack=True,
        has_backend_disagreement=True,
        has_cposs_backend_disagreement=True,
        has_cposs_disagreement_inspection=True,
        has_source_discovery=True,
        has_model_guardrails=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
        has_measurement_queue=True,
    )
    assert report["status"] == "roadmap_active"
    assert len(report["deliverables"]) == 5
    assert report["deliverables"][1]["status"] == "pilot_draft_ready"


def test_roadmap_status_markdown_contains_remaining_work():
    report = roadmap_status_report(
        project_status={
            "ampetp": {"readiness_status": "paper_pilot_ready"},
            "verification": {"latest_local_test_summary": "1 passed", "docker_status": "fairchem_omc25_uma_ampetp_cuda_verified"},
        },
        readiness={"status": "paper_pilot_ready"},
        cposs_bridge={"family_count": 2, "structure_count": 16},
        has_preprint_draft=True,
        has_joss_draft=True,
        has_fastcsp_plan=True,
        has_release_boundary=True,
        has_cposs_pair_candidates=True,
        has_cposs_pair_triage=True,
        has_cposs_candidate_cards=True,
        has_cposs_evidence_workpack=True,
        has_backend_disagreement=True,
        has_cposs_backend_disagreement=True,
        has_cposs_disagreement_inspection=True,
        has_source_discovery=True,
        has_model_guardrails=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
        has_measurement_queue=True,
    )
    markdown = roadmap_status_markdown(report)
    assert markdown.startswith("# CrystalProbe Roadmap Status")
    assert "Polymorph-pair benchmark" in markdown
    assert "Keep Docker/fairchem verification current" in markdown
    assert "Release-boundary report" in markdown
    assert "pair-candidate records" in markdown
    assert "triage report" in markdown
    assert "candidate cards" in markdown
    assert "evidence workpacks" in markdown
    assert "backend-disagreement metrics" in markdown
    assert "CPOSS backend-disagreement" in markdown
    assert "Uncertainty proxy v0" in markdown
    assert "OMAT24/OMol25 model guardrails" in markdown
    assert "Substance profiles" in markdown
    assert "Measurement queue" in markdown
    assert "Source-discovery report" in markdown
    assert "CBZ backend-disagreement inspection" in markdown
    assert "UMA access now verifies" in markdown
    assert "UMA reference measurement" in markdown


def test_roadmap_status_records_completed_uma_contrast():
    report = roadmap_status_report(
        project_status={
            "ampetp": {"readiness_status": "paper_pilot_ready"},
            "verification": {
                "latest_local_test_summary": "1 passed",
                "docker_status": "fairchem_omc25_uma_ampetp_sensitivity_uma_therapeutic_contrast_cuda_verified",
            },
        },
        readiness={"status": "paper_pilot_ready"},
        cposs_bridge={"family_count": 2, "structure_count": 16},
        has_preprint_draft=True,
        has_joss_draft=True,
        has_fastcsp_plan=True,
        has_release_boundary=True,
        has_cposs_pair_candidates=True,
        has_cposs_pair_triage=True,
        has_cposs_candidate_cards=True,
        has_cposs_evidence_workpack=True,
        has_backend_disagreement=True,
        has_cposs_backend_disagreement=True,
        has_cposs_disagreement_inspection=True,
        has_source_discovery=True,
        has_model_guardrails=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
        has_measurement_queue=True,
    )
    paper = report["deliverables"][1]

    assert "AMPETP-vs-ibuprofen UMA contrast is available." in paper["evidence"]
    assert "Scale UMA contrast to curated pairwise benchmark slices." in paper["remaining"]


def test_roadmap_status_records_completed_aimnet2_contrast():
    report = roadmap_status_report(
        project_status={
            "ampetp": {"readiness_status": "paper_pilot_ready"},
            "verification": {
                "latest_local_test_summary": "1 passed",
                "docker_status": "fairchem_omc25_aimnet2_therapeutic_contrast_cuda_verified",
            },
        },
        readiness={"status": "paper_pilot_ready"},
        cposs_bridge={"family_count": 2, "structure_count": 16},
        has_preprint_draft=True,
        has_joss_draft=True,
        has_fastcsp_plan=True,
        has_release_boundary=True,
        has_cposs_pair_candidates=True,
        has_cposs_pair_triage=True,
        has_cposs_candidate_cards=True,
        has_cposs_evidence_workpack=True,
        has_backend_disagreement=True,
        has_cposs_backend_disagreement=True,
        has_cposs_disagreement_inspection=True,
        has_source_discovery=True,
        has_model_guardrails=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
        has_measurement_queue=True,
    )
    paper = report["deliverables"][1]

    assert "AMPETP-vs-ibuprofen AIMNet2 contrast is available." in paper["evidence"]
    assert "Scale AIMNet2 contrast to curated pairwise benchmark slices." in paper["remaining"]


def test_roadmap_status_records_candidate_cards_and_disagreement():
    report = roadmap_status_report(
        project_status={
            "ampetp": {"readiness_status": "paper_pilot_ready"},
            "verification": {"latest_local_test_summary": "1 passed", "docker_status": "verified"},
        },
        readiness={"status": "paper_pilot_ready"},
        cposs_bridge={"family_count": 2, "structure_count": 16},
        has_preprint_draft=True,
        has_joss_draft=True,
        has_fastcsp_plan=True,
        has_release_boundary=True,
        has_cposs_pair_candidates=True,
        has_cposs_pair_triage=True,
        has_cposs_candidate_cards=True,
        has_cposs_evidence_workpack=True,
        has_backend_disagreement=True,
        has_cposs_backend_disagreement=True,
        has_cposs_disagreement_inspection=True,
        has_source_discovery=True,
        has_model_guardrails=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
        has_measurement_queue=True,
    )

    benchmark = report["deliverables"][0]
    paper = report["deliverables"][1]
    uncertainty = report["deliverables"][2]
    assert "CPOSS candidate cards include claim boundaries and follow-up backend commands." in benchmark["evidence"]
    assert "Prioritized CPOSS pairs have multi-backend disagreement evidence." in benchmark["evidence"]
    assert "CBZ backend-disagreement inspection report records the ordering flip and follow-up actions." in benchmark["evidence"]
    assert "Substance profiles consolidate medication-priority source, measurement, and claim-boundary status." in benchmark["evidence"]
    assert "Measurement queue ranks the next source, inspection, and measurement actions." in benchmark["evidence"]
    assert "Source-discovery report differentiates modafinil download, atomoxetine validation, and methylphenidate deeper search." in benchmark["evidence"]
    assert "AMPETP backend-disagreement metrics are available." in paper["evidence"]
    assert "High-priority CPOSS backend-disagreement metrics are available." in paper["evidence"]
    assert "Backend-disagreement metrics provide the first uncalibrated uncertainty proxy." in uncertainty["evidence"]
    assert "Uncertainty proxy v0 aggregates AMPETP sensitivity and high-priority CPOSS disagreement evidence." in uncertainty["evidence"]


def test_roadmap_status_uses_cposs_promotion_milestones():
    report = roadmap_status_report(
        project_status={
            "ampetp": {"readiness_status": "paper_pilot_ready"},
            "verification": {"latest_local_test_summary": "1 passed", "docker_status": "verified"},
        },
        readiness={"status": "paper_pilot_ready"},
        cposs_bridge={"family_count": 2, "structure_count": 16},
        cposs_promotion_gate={
            "promoted_count": 0,
            "milestones": [
                {"pair_count": 20, "remaining": 20, "status": "pending"},
                {"pair_count": 50, "remaining": 50, "status": "pending"},
                {"pair_count": 100, "remaining": 100, "status": "pending"},
            ],
        },
        has_preprint_draft=True,
        has_joss_draft=True,
        has_fastcsp_plan=True,
        has_release_boundary=True,
        has_cposs_pair_candidates=True,
        has_cposs_pair_triage=True,
        has_cposs_candidate_cards=True,
        has_cposs_evidence_workpack=True,
        has_backend_disagreement=True,
        has_cposs_backend_disagreement=True,
        has_cposs_disagreement_inspection=True,
        has_source_discovery=True,
        has_model_guardrails=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
        has_measurement_queue=True,
        has_medication_cif_ingestion=True,
        has_medication_measurements=True,
        has_cposs_promotion_gate=True,
        has_fingerprint_artifact_plan=True,
    )

    benchmark = report["deliverables"][0]
    assert (
        "CPOSS promotion gate records 0 promoted benchmark pairs; milestones: "
        "20 pairs: pending (20 remaining), 50 pairs: pending (50 remaining), "
        "100 pairs: pending (100 remaining)."
    ) in benchmark["evidence"]
    assert (
        "Use the CPOSS promotion gate to fill 20 more verified pairs for the 20-pair milestone, "
        "then continue to 50 and 100+."
    ) in benchmark["remaining"]


def test_roadmap_status_uses_fingerprint_candidate_slices():
    report = roadmap_status_report(
        project_status={
            "ampetp": {"readiness_status": "paper_pilot_ready"},
            "verification": {"latest_local_test_summary": "1 passed", "docker_status": "verified"},
        },
        readiness={"status": "paper_pilot_ready"},
        cposs_bridge={"family_count": 2, "structure_count": 16},
        fingerprint_artifact_plan={
            "candidate_family_summary": [
                {"family": "CBZ", "candidate_count": 8, "promoted_count": 0},
                {"family": "IBP", "candidate_count": 6, "promoted_count": 0},
            ]
        },
        has_preprint_draft=True,
        has_joss_draft=True,
        has_fastcsp_plan=True,
        has_release_boundary=True,
        has_cposs_pair_candidates=True,
        has_cposs_pair_triage=True,
        has_cposs_candidate_cards=True,
        has_cposs_evidence_workpack=True,
        has_backend_disagreement=True,
        has_cposs_backend_disagreement=True,
        has_cposs_disagreement_inspection=True,
        has_source_discovery=True,
        has_model_guardrails=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
        has_measurement_queue=True,
        has_fingerprint_artifact_plan=True,
    )

    paper = report["deliverables"][1]
    assert (
        "Fingerprint artifact plan gates chemistry-slice figures and tracks pre-benchmark candidate slices: "
        "CBZ=8 candidates/0 promoted, IBP=6 candidates/0 promoted."
    ) in paper["evidence"]


def test_roadmap_status_uses_environment_blockers():
    report = roadmap_status_report(
        project_status={
            "ampetp": {"readiness_status": "paper_pilot_ready"},
            "verification": {"latest_local_test_summary": "1 passed", "docker_status": "verified"},
        },
        readiness={"status": "paper_pilot_ready"},
        cposs_bridge={"family_count": 2, "structure_count": 16},
        environment_blockers={
            "missing_count": 2,
            "dependencies": [
                {"module": "ase", "status": "missing_from_active_python"},
                {"module": "torch", "status": "available"},
                {"module": "fairchem", "status": "missing_from_active_python"},
            ],
        },
        has_preprint_draft=True,
        has_joss_draft=True,
        has_fastcsp_plan=True,
        has_release_boundary=True,
        has_cposs_pair_candidates=True,
        has_cposs_pair_triage=True,
        has_cposs_candidate_cards=True,
        has_cposs_evidence_workpack=True,
        has_backend_disagreement=True,
        has_cposs_backend_disagreement=True,
        has_cposs_disagreement_inspection=True,
        has_source_discovery=True,
        has_model_guardrails=True,
        has_environment_blockers=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
        has_measurement_queue=True,
    )

    fastcsp = report["deliverables"][3]
    software = report["deliverables"][4]
    assert (
        "Active Python environment report records missing optional dependencies in this runner: ase, fairchem."
        in fastcsp["evidence"]
    )
    assert (
        "Run dependency-heavy commands through `.venv`, Docker, or a Python where ASE/MACE/AIMNet2/fairchem are visible."
        in fastcsp["remaining"]
    )
    assert (
        "Active-environment blocker report records optional dependency visibility for reproducible troubleshooting."
        in software["evidence"]
    )
