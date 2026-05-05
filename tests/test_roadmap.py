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
        has_model_guardrails=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
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
        has_model_guardrails=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
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
        has_model_guardrails=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
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
        has_model_guardrails=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
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
        has_model_guardrails=True,
        has_uncertainty_proxy=True,
        has_substance_profiles=True,
    )

    benchmark = report["deliverables"][0]
    paper = report["deliverables"][1]
    uncertainty = report["deliverables"][2]
    assert "CPOSS candidate cards include claim boundaries and follow-up backend commands." in benchmark["evidence"]
    assert "Prioritized CPOSS pairs have multi-backend disagreement evidence." in benchmark["evidence"]
    assert "Substance profiles consolidate medication-priority source, measurement, and claim-boundary status." in benchmark["evidence"]
    assert "AMPETP backend-disagreement metrics are available." in paper["evidence"]
    assert "High-priority CPOSS backend-disagreement metrics are available." in paper["evidence"]
    assert "Backend-disagreement metrics provide the first uncalibrated uncertainty proxy." in uncertainty["evidence"]
    assert "Uncertainty proxy v0 aggregates AMPETP sensitivity and high-priority CPOSS disagreement evidence." in uncertainty["evidence"]
