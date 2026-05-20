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
            "outputs/crystalprobe_energy_verification.json",
            "outputs/crystalprobe_energy_verification.md",
            "outputs/crystalprobe_execution_unblock_report.json",
            "outputs/crystalprobe_execution_unblock_report.md",
            "outputs/crystalprobe_evidence_atlas.json",
            "outputs/crystalprobe_evidence_atlas.md",
            "outputs/crystalprobe_evidence_atlas.sqlite",
            "outputs/crystalprobe_handoff_summary.json",
            "outputs/crystalprobe_handoff_summary.md",
            "outputs/crystalprobe_active_evidence_triage.json",
            "outputs/crystalprobe_active_evidence_triage.md",
            "outputs/crystalprobe_evidence_packet.json",
            "outputs/crystalprobe_evidence_packet.md",
            "outputs/crystalprobe_evidence_resolution.json",
            "outputs/crystalprobe_evidence_resolution.md",
            "outputs/crystalprobe_historical_opportunities.json",
            "outputs/crystalprobe_historical_opportunities.md",
            "outputs/crystalprobe_historical_research_modules.json",
            "outputs/crystalprobe_historical_research_modules.md",
            "outputs/crystalprobe_molecule_viewers.json",
            "outputs/crystalprobe_molecule_viewers.md",
            "outputs/crystalprobe_molecule_bug_hunt.json",
            "outputs/crystalprobe_molecule_bug_hunt.md",
            "outputs/crystalprobe_molecule_bug_hunt.sqlite",
            "outputs/crystalprobe_project_status.json",
            "outputs/crystalprobe_project_status.md",
            "outputs/crystalprobe_publication_readiness.json",
            "outputs/crystalprobe_publication_readiness.md",
            "outputs/crystalprobe_release_boundary.json",
            "outputs/crystalprobe_release_boundary.md",
            "outputs/crystalprobe_report_consistency.json",
            "outputs/crystalprobe_report_consistency.md",
            "outputs/crystalprobe_research_cycle.json",
            "outputs/crystalprobe_research_cycle.md",
            "outputs/crystalprobe_risk_register.json",
            "outputs/crystalprobe_risk_register.md",
            "outputs/crystalprobe_roadmap_status.json",
            "outputs/crystalprobe_roadmap_status.md",
            "outputs/crystalprobe_status_chain.json",
        ]
    )
    assert {record["category"] for record in report["records"]} == {"candidate_public"}


def test_release_boundary_classifies_medication_bundle_license_review():
    report = release_boundary_report(
        artifact_paths=[
            "outputs/medication_research_bundle_manifest.md",
            "outputs/figures/medication_case_study_coverage.svg",
            "outputs/figures/medication_stereochemistry_scope.svg",
        ]
    )

    assert {record["category"] for record in report["records"]} == {"license_review_required"}
    assert all("Medication" in record["reason"] for record in report["records"])


def test_release_boundary_classifies_public_case_metadata_public():
    report = release_boundary_report(
        artifact_paths=[
            "docs/public_demo.md",
            "docs/assets/public_cases/ibp_ibp01_psicrys_vs_ibp06_psicrys_backend_summary.svg",
            "data/public_cases/cposs_ibp_candidate_v0.1.json",
        ]
    )

    assert {record["category"] for record in report["records"]} == {"candidate_public"}


def test_release_boundary_default_paths_include_script_bootstrap():
    assert "scripts/_path_bootstrap.py" in DEFAULT_REPO_PATHS
    assert "data/curation/cposs_block_form_mapping_v0.1.json" in DEFAULT_REPO_PATHS
    assert "data/curation/cposs_evidence_overrides_v0.1.json" in DEFAULT_REPO_PATHS
    assert "data/curation/evidence_resolution_candidates_v0.1.json" in DEFAULT_REPO_PATHS
    assert "data/curation/historical_opportunity_matrix_v0.1.json" in DEFAULT_REPO_PATHS
    assert "data/curation/medication_polymorphism_evidence_v0.1.json" in DEFAULT_REPO_PATHS
    assert "data/curation/molecule_bug_hunt_stress_v0.1.json" in DEFAULT_REPO_PATHS
    assert "docs/evidence_atlas.md" in DEFAULT_REPO_PATHS
    assert "docs/evidence_atlas.html" in DEFAULT_REPO_PATHS
    assert "docs/historical_research_opportunities.md" in DEFAULT_REPO_PATHS
    assert "docs/molecule_bug_hunt.md" in DEFAULT_REPO_PATHS
    assert "docs/molecule_viewers.md" in DEFAULT_REPO_PATHS
    assert "docs/release_boundary_review_2026-05-06.md" in DEFAULT_REPO_PATHS
    report = release_boundary_report(artifact_paths=DEFAULT_REPO_PATHS)
    by_path = {record["path"]: record for record in report["records"]}
    assert by_path["scripts/_path_bootstrap.py"]["category"] == "candidate_public"
    assert by_path["data/curation/cposs_block_form_mapping_v0.1.json"]["category"] == "candidate_public"
    assert by_path["data/curation/cposs_evidence_overrides_v0.1.json"]["category"] == "candidate_public"
    assert by_path["docs/release_boundary_review_2026-05-06.md"]["category"] == "candidate_public"


def test_release_boundary_default_paths_include_cposs_block_mapping_surface():
    expected_paths = {
        "scripts/build_cposs_block_mapping_dossier.py",
        "scripts/build_cposs_block_mapping_report.py",
        "scripts/build_cposs_promotion_burndown_report.py",
        "scripts/seed_cposs_block_form_mapping_manifest.py",
        "src/crystalprobe/insight/cposs_block_mapping.py",
        "src/crystalprobe/insight/cposs_burndown.py",
        "tests/test_cposs_block_mapping.py",
        "tests/test_cposs_burndown.py",
    }

    assert expected_paths.issubset(set(DEFAULT_REPO_PATHS))
    report = release_boundary_report(artifact_paths=DEFAULT_REPO_PATHS)
    by_path = {record["path"]: record for record in report["records"]}
    assert {by_path[path]["category"] for path in expected_paths} == {"candidate_public"}


def test_release_boundary_default_paths_include_status_and_roadmap_surface():
    expected_paths = {
        "scripts/build_project_status_dashboard.py",
        "scripts/build_active_evidence_triage_report.py",
        "scripts/build_evidence_atlas.py",
        "scripts/build_energy_verification_report.py",
        "scripts/build_evidence_packet_report.py",
        "scripts/build_evidence_resolution_report.py",
        "scripts/build_historical_opportunity_report.py",
        "scripts/build_historical_research_modules_report.py",
        "scripts/build_roadmap_status_report.py",
        "scripts/build_status_chain.py",
        "scripts/run_research_cycle.py",
        "scripts/build_environment_blockers_report.py",
        "scripts/build_execution_unblock_report.py",
        "scripts/build_handoff_report.py",
        "scripts/build_publication_readiness_report.py",
        "scripts/build_report_consistency_report.py",
        "scripts/build_risk_register_report.py",
        "scripts/build_medication_benchmark_evidence_report.py",
        "scripts/build_medication_polymorph_generation_report.py",
        "scripts/build_medication_polymorphism_autonomy_report.py",
        "scripts/build_medication_seed_ranking_report.py",
        "scripts/build_medication_stereochemistry_report.py",
        "scripts/build_medication_stereochemistry_dossier.py",
        "scripts/build_molecule_bug_hunt_database.py",
        "scripts/build_molecule_viewer_report.py",
        "src/crystalprobe/core/io.py",
        "src/crystalprobe/datahub/cif_repair.py",
        "src/crystalprobe/insight/active_evidence_triage.py",
        "src/crystalprobe/insight/energy_verification.py",
        "src/crystalprobe/insight/environment.py",
        "src/crystalprobe/insight/evidence_atlas.py",
        "src/crystalprobe/insight/evidence_packet.py",
        "src/crystalprobe/insight/evidence_resolution.py",
        "src/crystalprobe/insight/free_energy_probe.py",
        "src/crystalprobe/insight/handoff.py",
        "src/crystalprobe/insight/historical_opportunities.py",
        "src/crystalprobe/insight/landscape_audit.py",
        "src/crystalprobe/insight/medication_benchmark_evidence.py",
        "src/crystalprobe/insight/medication_generation.py",
        "src/crystalprobe/insight/medication_polymorphism.py",
        "src/crystalprobe/insight/medication_seed_ranking.py",
        "src/crystalprobe/insight/medication_stereochemistry.py",
        "src/crystalprobe/insight/medication_stereochemistry_dossier.py",
        "src/crystalprobe/insight/molecule_bug_hunt.py",
        "src/crystalprobe/insight/molecule_viewers.py",
        "src/crystalprobe/insight/publication.py",
        "src/crystalprobe/insight/report_consistency.py",
        "src/crystalprobe/insight/risk.py",
        "src/crystalprobe/insight/motif_prior.py",
        "src/crystalprobe/insight/roadmap.py",
        "src/crystalprobe/insight/status.py",
        "src/crystalprobe/insight/unblock.py",
        "src/crystalprobe/uncertainty/calibrated_abstention.py",
        "tests/test_active_evidence_triage.py",
        "tests/test_calibrated_abstention.py",
        "tests/test_energy_verification.py",
        "tests/test_environment.py",
        "tests/test_evidence_atlas.py",
        "tests/test_evidence_packet.py",
        "tests/test_evidence_resolution.py",
        "tests/test_free_energy_probe.py",
        "tests/test_handoff.py",
        "tests/test_historical_opportunities.py",
        "tests/test_landscape_audit.py",
        "tests/test_medication_benchmark_evidence.py",
        "tests/test_medication_generation.py",
        "tests/test_medication_polymorphism.py",
        "tests/test_medication_seed_ranking.py",
        "tests/test_medication_stereochemistry.py",
        "tests/test_medication_stereochemistry_dossier.py",
        "tests/test_molecule_bug_hunt.py",
        "tests/test_molecule_viewers.py",
        "tests/test_motif_prior.py",
        "tests/test_publication.py",
        "tests/test_report_consistency.py",
        "tests/test_risk.py",
        "tests/test_unblock.py",
        "tests/test_io.py",
        "tests/test_report_workflows.py",
        "tests/test_research_cycle.py",
        "tests/test_roadmap.py",
        "tests/test_run_structure_inference.py",
        "tests/test_status.py",
    }

    assert expected_paths.issubset(set(DEFAULT_REPO_PATHS))
    report = release_boundary_report(artifact_paths=DEFAULT_REPO_PATHS)
    by_path = {record["path"]: record for record in report["records"]}
    assert {by_path[path]["category"] for path in expected_paths} == {"candidate_public"}
