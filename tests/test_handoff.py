from crystalprobe.insight.handoff import handoff_markdown, handoff_report


def _report():
    return handoff_report(
        project_status={
            "verification": {"latest_local_test_summary": "145 passed, 3 skipped", "git_status": "dirty"},
            "ampetp": {"readiness_status": "paper_pilot_ready"},
            "cposs_bridge": {"structure_count": 16, "family_count": 2},
            "evidence_tiers": {"blocked_count": 1},
            "remaining_user_input": ["Confirm local-only medication CIF policy."],
        },
        roadmap_status={
            "deliverables": [
                {
                    "deliverable": "Polymorph-pair benchmark",
                    "status": "partial_bridge_ready",
                    "evidence": ["bridge", "schema", "cards", "extra"],
                    "remaining": ["promote pairs", "curate stability", "scale", "extra"],
                }
            ]
        },
        measurement_queue={
            "next_batch": [
                {
                    "substance": "modafinil",
                    "action_type": "curate_claim_boundary",
                    "priority_score": 89,
                    "blocked": False,
                    "active_runner_blocked": True,
                    "first_step": "Use .venv or Docker.",
                }
            ]
        },
        execution_unblock={
            "status": "execution_unblock_queue_recorded",
            "blocker_count": 15,
            "counts": {"backend_execution": 5},
            "approval_batch": ["Run recorded Docker commands later."],
        },
        publication_readiness={
            "status": "publication_blocked",
            "ready": False,
            "blocked_gate_count": 2,
            "gates": [
                {"gate": "verified_pair_milestone_20", "status": "blocked", "detail": "0 promoted pairs."}
            ],
            "next_publication_steps": ["Curate 20 verified pairs.", "Review release boundary."],
        },
        risk_register={
            "risks": [
                {
                    "risk_id": "fastcsp_positioning_drift",
                    "severity": "medium",
                    "status": "mitigated",
                    "next_mitigation": "Keep positioning.",
                },
                {
                    "risk_id": "medication_stereochemistry_scope_confusion",
                    "severity": "high",
                    "status": "watch",
                    "next_mitigation": "Keep enantiomeric crystal comparison separate from polymorph benchmark claims.",
                },
                {
                    "risk_id": "overclaiming_candidate_evidence",
                    "severity": "critical",
                    "status": "open",
                    "next_mitigation": "Promote verified pairs.",
                },
            ]
        },
        report_consistency={
            "status": "reports_consistent",
            "blocked_check_count": 0,
            "checks": [
                {
                    "check": "test_summary_alignment",
                    "status": "passed",
                    "detail": "project=145 passed, roadmap=145 passed, handoff=145 passed",
                }
            ],
        },
    )


def test_handoff_report_distills_status_inputs():
    report = _report()

    assert report["status"] == "handoff_recorded"
    assert report["verification"]["latest_local_test_summary"] == "145 passed, 3 skipped"
    assert report["execution_unblock"]["blocker_count"] == 15
    assert report["deliverables"][0]["top_evidence"] == ["bridge", "schema", "cards"]
    assert report["deliverables"][0]["top_remaining"] == ["promote pairs", "curate stability", "scale"]
    assert report["next_batch"][0]["substance"] == "modafinil"
    assert report["publication_readiness"]["status"] == "publication_blocked"
    assert report["publication_readiness"]["blocked_gate_count"] == 2
    assert report["report_consistency"]["status"] == "reports_consistent"
    assert report["report_consistency"]["blocked_check_count"] == 0
    assert [risk["risk_id"] for risk in report["top_risks"]] == [
        "overclaiming_candidate_evidence",
        "medication_stereochemistry_scope_confusion",
    ]


def test_handoff_markdown_renders_approval_batch_and_policy():
    markdown = handoff_markdown(_report())

    assert markdown.startswith("# CrystalProbe Handoff Summary")
    assert "Run recorded Docker commands later." in markdown
    assert "Publication Gates" in markdown
    assert "Report Consistency" in markdown
    assert "test_summary_alignment" in markdown
    assert "Top Risks" in markdown
    assert "medication_stereochemistry_scope_confusion" in markdown
    assert "verified_pair_milestone_20" in markdown
    assert "Confirm local-only medication CIF policy." in markdown
    assert "source reports remain canonical" in markdown
