from pathlib import Path

from crystalprobe.insight.status import project_status_markdown, project_status_report


ROOT = Path(__file__).resolve().parents[1]


def test_project_status_report_extracts_blockers():
    blockers = """
# Blockers

## Current Blockers

- installed

## Remaining User Input

- Request UMA access.
- Obtain target CIF.

## Other
""".strip()
    report = project_status_report(
        readiness={"status": "paper_pilot_ready", "passed": 8, "failed": 0},
        bundle={"artifacts": [{}, {}], "manifest_sha256": "a" * 64},
        cposs_bridge={"family_count": 2, "structure_count": 16, "families": {"IBP": {}, "CBZ": {}}},
        therapeutic_contrast={"backend": "mace", "target_count": 2},
        blockers_text=blockers,
        test_summary="1 passed",
        docker_status="fairchem_verified",
        git_status="clean",
    )
    assert report["remaining_user_input"] == ["Request UMA access.", "Obtain target CIF."]
    assert report["cposs_bridge"]["families"] == ["CBZ", "IBP"]
    assert report["therapeutic_contrast"]["status"] == "mace_contrast_ready"
    assert report["verification"]["docker_status"] == "fairchem_verified"
    assert report["verification"]["git_status"] == "clean"


def test_project_status_markdown_contains_next_steps():
    report = project_status_report(
        readiness={"status": "paper_pilot_ready", "passed": 8, "failed": 0},
        bundle={"artifacts": [{}, {}], "manifest_sha256": "a" * 64},
        cposs_bridge={"family_count": 2, "structure_count": 16, "families": {"IBP": {}, "CBZ": {}}},
        therapeutic_contrast={"backend": "mace", "target_count": 2},
        blockers_text="## Remaining User Input\n- Request UMA access.\n",
        test_summary="1 passed",
    )
    markdown = project_status_markdown(report)
    assert markdown.startswith("# CrystalProbe Project Status Dashboard")
    assert "Next Recommended Steps" in markdown
    assert "Therapeutic Contrast" in markdown
    assert "Request UMA access" in markdown


def test_project_status_markdown_handles_empty_remaining_input():
    report = project_status_report(
        readiness={"status": "paper_pilot_ready", "passed": 8, "failed": 0},
        bundle={"artifacts": [{}, {}], "manifest_sha256": "a" * 64},
        cposs_bridge={"family_count": 2, "structure_count": 16, "families": {"IBP": {}, "CBZ": {}}},
        therapeutic_contrast={"backend": "mace", "target_count": 2},
        blockers_text="## Remaining User Input\n\n## Other\n",
        test_summary="1 passed",
    )
    markdown = project_status_markdown(report)
    assert "- None currently recorded." in markdown
    assert "Extend UMA from AMPETP sensitivity into therapeutic contrast workflows." in markdown


def test_project_status_omits_uma_contrast_step_when_verified():
    report = project_status_report(
        readiness={"status": "paper_pilot_ready", "passed": 8, "failed": 0},
        bundle={"artifacts": [{}, {}], "manifest_sha256": "a" * 64},
        cposs_bridge={"family_count": 2, "structure_count": 16, "families": {"IBP": {}, "CBZ": {}}},
        therapeutic_contrast={"backend": "mace", "target_count": 2},
        blockers_text="## Remaining User Input\n\n## Other\n",
        test_summary="1 passed",
        docker_status="fairchem_omc25_uma_ampetp_sensitivity_uma_therapeutic_contrast_cuda_verified",
    )

    assert "Extend UMA from AMPETP sensitivity into therapeutic contrast workflows." not in report["next_recommended_steps"]


def test_project_status_omits_aimnet2_contrast_step_when_verified():
    report = project_status_report(
        readiness={"status": "paper_pilot_ready", "passed": 8, "failed": 0},
        bundle={"artifacts": [{}, {}], "manifest_sha256": "a" * 64},
        cposs_bridge={"family_count": 2, "structure_count": 16, "families": {"IBP": {}, "CBZ": {}}},
        therapeutic_contrast={"backend": "mace", "target_count": 2},
        blockers_text="## Remaining User Input\n\n## Other\n",
        test_summary="1 passed",
        docker_status="fairchem_omc25_aimnet2_therapeutic_contrast_cuda_verified",
    )

    assert "Run AIMNet2 on the ibuprofen sensitivity grid in Linux/Docker." not in report["next_recommended_steps"]


def test_project_status_summarizes_evidence_tiers():
    report = project_status_report(
        readiness={"status": "paper_pilot_ready", "passed": 8, "failed": 0},
        bundle={"artifacts": [{}, {}], "manifest_sha256": "a" * 64},
        cposs_bridge={"family_count": 2, "structure_count": 16, "families": {"IBP": {}, "CBZ": {}}},
        therapeutic_contrast={"backend": "mace", "target_count": 2},
        evidence_tiers={
            "status": "evidence_tiers_recorded",
            "targets": [
                {"target": "missing", "tier": {"tier": "blocked_no_coordinates"}},
                {"target": "pilot", "tier": {"tier": "agi_assisted_guardrailed_pilot"}},
            ],
        },
        blockers_text="## Remaining User Input\n\n## Other\n",
        test_summary="1 passed",
    )
    markdown = project_status_markdown(report)

    assert report["evidence_tiers"]["target_count"] == 2
    assert report["evidence_tiers"]["guardrailed_pilot_count"] == 1
    assert report["evidence_tiers"]["blocked_count"] == 1
    assert "## Evidence Tiers" in markdown


def test_project_status_summarizes_execution_unblock_report():
    report = project_status_report(
        readiness={"status": "paper_pilot_ready", "passed": 8, "failed": 0},
        bundle={"artifacts": [{}, {}], "manifest_sha256": "a" * 64},
        cposs_bridge={"family_count": 2, "structure_count": 16, "families": {"IBP": {}, "CBZ": {}}},
        therapeutic_contrast={"backend": "mace", "target_count": 2},
        execution_unblock={
            "status": "execution_unblock_queue_recorded",
            "blocker_count": 15,
            "counts": {
                "active_python_dependency": 4,
                "backend_execution": 5,
                "queue_active_runner": 6,
            },
            "approval_batch": ["Select or repair the CrystalProbe Python runner."],
        },
        blockers_text="## Remaining User Input\n\n## Other\n",
        test_summary="1 passed",
    )
    markdown = project_status_markdown(report)

    assert report["execution_unblock"]["blocker_count"] == 15
    assert "Select or repair the CrystalProbe Python runner." in report["next_recommended_steps"]
    assert "## Execution Unblock" in markdown
    assert "Active Python dependency blockers: `4`" in markdown
    assert "Select or repair the CrystalProbe Python runner." in markdown


def test_readme_records_fastcsp_positioning_and_claim_risks():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "FastCSP generates and ranks candidate crystal landscapes" in readme
    assert "CrystalProbe audits, compares, calibrates, curates" in readme
    assert "MACE, AIMNet2, and UMA absolute energies are not automatically comparable" in readme
