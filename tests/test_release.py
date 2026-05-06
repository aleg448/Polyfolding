from crystalprobe.insight.release import release_boundary_markdown, release_boundary_report
from scripts.build_release_boundary_report import DEFAULT_REPO_PATHS


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


def test_release_boundary_classifies_environment_blocker_outputs_public():
    report = release_boundary_report(
        artifact_paths=[
            "outputs/crystalprobe_environment_blockers.json",
            "outputs/crystalprobe_environment_blockers.md",
            "outputs/crystalprobe_execution_unblock_report.json",
            "outputs/crystalprobe_execution_unblock_report.md",
            "outputs/crystalprobe_handoff_summary.json",
            "outputs/crystalprobe_handoff_summary.md",
            "outputs/crystalprobe_publication_readiness.json",
            "outputs/crystalprobe_publication_readiness.md",
        ]
    )
    assert {record["category"] for record in report["records"]} == {"candidate_public"}


def test_release_boundary_classifies_medication_bundle_license_review():
    report = release_boundary_report(
        artifact_paths=[
            "outputs/medication_research_bundle_manifest.md",
            "outputs/figures/medication_case_study_coverage.svg",
        ]
    )

    assert {record["category"] for record in report["records"]} == {"license_review_required"}
    assert all("Medication" in record["reason"] for record in report["records"])


def test_release_boundary_default_paths_include_script_bootstrap():
    assert "scripts/_path_bootstrap.py" in DEFAULT_REPO_PATHS
    report = release_boundary_report(artifact_paths=DEFAULT_REPO_PATHS)
    by_path = {record["path"]: record for record in report["records"]}
    assert by_path["scripts/_path_bootstrap.py"]["category"] == "candidate_public"


def test_release_boundary_default_paths_include_status_and_roadmap_surface():
    expected_paths = {
        "scripts/build_project_status_dashboard.py",
        "scripts/build_roadmap_status_report.py",
        "scripts/build_environment_blockers_report.py",
        "scripts/build_execution_unblock_report.py",
        "scripts/build_handoff_report.py",
        "scripts/build_publication_readiness_report.py",
        "src/crystalprobe/core/io.py",
        "src/crystalprobe/insight/environment.py",
        "src/crystalprobe/insight/handoff.py",
        "src/crystalprobe/insight/publication.py",
        "src/crystalprobe/insight/roadmap.py",
        "src/crystalprobe/insight/status.py",
        "src/crystalprobe/insight/unblock.py",
        "tests/test_environment.py",
        "tests/test_handoff.py",
        "tests/test_publication.py",
        "tests/test_unblock.py",
        "tests/test_io.py",
        "tests/test_report_workflows.py",
        "tests/test_roadmap.py",
        "tests/test_status.py",
    }

    assert expected_paths.issubset(set(DEFAULT_REPO_PATHS))
    report = release_boundary_report(artifact_paths=DEFAULT_REPO_PATHS)
    by_path = {record["path"]: record for record in report["records"]}
    assert {by_path[path]["category"] for path in expected_paths} == {"candidate_public"}
