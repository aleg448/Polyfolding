from crystalprobe.insight.release import release_boundary_markdown, release_boundary_report


def test_release_boundary_report_classifies_coordinate_files_local_only():
    report = release_boundary_report(
        artifact_paths=[
            "src/crystalprobe/insight/release.py",
            "papers/ampetp_case_study.md",
            "outputs/ccdc_ampetp_extracted.cif",
            "outputs/ampetp_case_study_report.md",
            "outputs/figures/ampetp_structure_projection.svg",
        ]
    )
    by_path = {record["path"]: record for record in report["records"]}
    assert by_path["outputs/ccdc_ampetp_extracted.cif"]["category"] == "local_only"
    assert by_path["src/crystalprobe/insight/release.py"]["category"] == "candidate_public"
    assert by_path["papers/ampetp_case_study.md"]["category"] == "candidate_public"
    assert by_path["outputs/ampetp_case_study_report.md"]["category"] == "license_review_required"
    assert by_path["outputs/figures/ampetp_structure_projection.svg"]["category"] == "license_review_required"


def test_release_boundary_report_includes_workflow_outputs():
    report = release_boundary_report(
        artifact_paths=["README.md"],
        workflow_manifest={
            "workflows": [
                {
                    "primary_outputs": [
                        "outputs/ampetp_readiness_report.md",
                        "outputs/ccdc_ampetp_extracted.cif",
                    ]
                }
            ]
        },
    )
    paths = {record["path"] for record in report["records"]}
    assert "outputs/ampetp_readiness_report.md" in paths
    assert "outputs/ccdc_ampetp_extracted.cif" in paths


def test_release_boundary_report_normalizes_duplicate_path_separators():
    report = release_boundary_report(
        artifact_paths=[
            "outputs\\ampetp_case_study_report.md",
            "outputs/ampetp_case_study_report.md",
        ]
    )
    assert [record["path"] for record in report["records"]] == ["outputs/ampetp_case_study_report.md"]


def test_release_boundary_markdown_renders_policy():
    report = release_boundary_report(artifact_paths=["README.md", "outputs/ccdc_ampetp_extracted.cif"])
    markdown = release_boundary_markdown(report)
    assert markdown.startswith("# CrystalProbe Release Boundary Report")
    assert "candidate_public" in markdown
    assert "local_only" in markdown


def test_release_boundary_classifies_evidence_tier_outputs_public():
    report = release_boundary_report(
        artifact_paths=[
            "outputs/crystalprobe_evidence_tiers.json",
            "outputs/crystalprobe_evidence_tiers.md",
        ]
    )
    assert {record["category"] for record in report["records"]} == {"candidate_public"}
