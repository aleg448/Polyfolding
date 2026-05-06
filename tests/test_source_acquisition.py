from crystalprobe.insight.source_acquisition import source_acquisition_markdown, source_acquisition_report


def test_source_acquisition_report_counts_user_input_and_failures():
    report = source_acquisition_report(
        {
            "targets": [
                {
                    "name": "modafinil",
                    "task": "download_public_cif_candidate",
                    "status": "download_not_completed_manual_access_required",
                    "download_attempts": [{"result": "failed", "method": "curl"}],
                    "local_coordinate_sources": [{"path": "data/sources/modafinil/file.cif"}],
                    "required_user_input": ["Download in browser."],
                },
                {
                    "name": "carbamazepine",
                    "task": "inspect_backend_disagreement",
                    "status": "local_evidence_available",
                },
            ],
            "policy": ["guardrail"],
        }
    )

    by_name = {target["name"]: target for target in report["targets"]}
    assert report["targets_requiring_user_input"] == 1
    assert by_name["modafinil"]["failed_download_attempt_count"] == 1
    assert by_name["modafinil"]["local_coordinate_source_count"] == 1
    assert by_name["carbamazepine"]["requires_user_input"] is False


def test_source_acquisition_markdown_renders_required_input():
    report = source_acquisition_report(
        {
            "targets": [
                {
                    "name": "atomoxetine hydrochloride",
                    "task": "validate_coordinate_access",
                    "status": "manual_validation_required",
                    "required_user_input": ["Search CCDC."],
                    "claim_boundary": "coordinates_not_obtained",
                }
            ],
            "policy": ["policy"],
        }
    )

    markdown = source_acquisition_markdown(report)

    assert markdown.startswith("# CrystalProbe Source Acquisition Report")
    assert "Search CCDC." in markdown
