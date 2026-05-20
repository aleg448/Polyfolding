from crystalprobe.insight.report_consistency import report_consistency_markdown, report_consistency_report


def test_report_consistency_passes_aligned_status_reports():
    report = report_consistency_report(
        project_status={"verification": {"latest_local_test_summary": "198 passed, 3 skipped"}},
        roadmap_status={"local_verification": "198 passed, 3 skipped"},
        handoff_summary={
            "verification": {"latest_local_test_summary": "198 passed, 3 skipped"},
            "publication_readiness": {
                "blocked_gate_count": 1,
                "gates": [{"gate": "release_boundary", "status": "blocked", "detail": _release_detail()}],
            },
        },
        publication_readiness={
            "blocked_gate_count": 1,
            "gates": [{"gate": "release_boundary", "status": "blocked", "detail": _release_detail()}],
        },
        release_boundary={"counts": {"candidate_public": 132, "license_review_required": 57, "local_only": 1}},
        status_chain={
            "steps": [
                {
                    "step": "project_status",
                    "command": ["scripts/build_project_status_dashboard.py", "--test-summary", "198 passed, 3 skipped"],
                },
                {"step": "roadmap_status", "command": ["scripts/build_roadmap_status_report.py"]},
                {"step": "handoff_summary", "command": ["scripts/build_handoff_report.py"]},
            ]
        },
    )

    assert report["status"] == "reports_consistent"
    assert report["blocked_check_count"] == 0
    assert {check["status"] for check in report["checks"]} == {"passed"}


def test_report_consistency_blocks_stale_test_summary_and_release_counts():
    report = report_consistency_report(
        project_status={"verification": {"latest_local_test_summary": "198 passed, 3 skipped"}},
        roadmap_status={"local_verification": "197 passed, 3 skipped"},
        handoff_summary={
            "verification": {"latest_local_test_summary": "198 passed, 3 skipped"},
            "publication_readiness": {
                "blocked_gate_count": 1,
                "gates": [{"gate": "release_boundary", "status": "blocked", "detail": "old"}],
            },
        },
        publication_readiness={
            "blocked_gate_count": 1,
            "gates": [{"gate": "release_boundary", "status": "blocked", "detail": _release_detail()}],
        },
        release_boundary={"counts": {"candidate_public": 132, "license_review_required": 57, "local_only": 1}},
        status_chain={"steps": [{"step": "handoff_summary", "command": []}]},
    )

    by_check = {check["check"]: check for check in report["checks"]}
    assert report["status"] == "report_consistency_blocked"
    assert by_check["test_summary_alignment"]["status"] == "blocked"
    assert by_check["release_boundary_count_alignment"]["status"] == "blocked"
    assert by_check["status_chain_order"]["status"] == "blocked"


def test_report_consistency_markdown_renders_checks():
    markdown = report_consistency_markdown(
        report_consistency_report(
            project_status={"verification": {"latest_local_test_summary": "not_recorded"}},
            roadmap_status={"local_verification": "not_recorded"},
            handoff_summary={
                "verification": {"latest_local_test_summary": "not_recorded"},
                "publication_readiness": {"blocked_gate_count": 0, "gates": []},
            },
            publication_readiness={"blocked_gate_count": 0, "gates": []},
            release_boundary={"counts": {}},
            status_chain={},
        )
    )

    assert markdown.startswith("# CrystalProbe Report Consistency")
    assert "test_summary_alignment" in markdown
    assert "Run scripts/build_status_chain.py" in markdown


def _release_detail():
    return "132 candidate-public, 57 license-review-required, 1 local-only artifacts."
