from crystalprobe.insight.fingerprint_artifacts import fingerprint_artifact_plan, fingerprint_artifact_plan_markdown


def test_fingerprint_artifact_plan_gates_pair_figures():
    report = fingerprint_artifact_plan(
        promotion_gate={
            "promoted_count": 0,
            "family_summary": [
                {
                    "family": "CBZ",
                    "candidate_count": 8,
                    "promoted_count": 0,
                    "blocked_count": 8,
                    "high_priority_blocked_count": 1,
                }
            ],
        },
        medication_measurements={"measured_target_count": 1},
        generated_figures={"medication_case_studies": "outputs/figures/medication_case_study_coverage.svg"},
    )

    by_id = {row["figure_id"]: row for row in report["figures"]}
    assert by_id["benchmark_composition"]["status"] == "blocked"
    assert by_id["medication_case_studies"]["status"] == "ready"
    assert by_id["medication_case_studies"]["artifact_path"] == "outputs/figures/medication_case_study_coverage.svg"
    markdown = fingerprint_artifact_plan_markdown(report)
    assert "Fingerprint Artifact Plan" in markdown
    assert "## Candidate Family Summary" in markdown
    assert "| `CBZ` | `8` | `0` | `8` | `1` |" in markdown
