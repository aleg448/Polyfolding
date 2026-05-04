from crystalprobe.insight.status import project_status_markdown, project_status_report


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
    assert "Wire UMA into a CrystalProbe fairchem prediction adapter." in markdown
