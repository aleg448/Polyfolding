from crystalprobe.insight.readiness import ampetp_readiness_report, readiness_markdown


def _bundle_manifest():
    roles = [
        "extracted_cif",
        "mace_sensitivity_predictions",
        "aimnet2_sensitivity_predictions",
        "figure_provenance",
        "figure_structure_projection",
        "figure_backend_diagnostics",
        "figure_sensitivity_deltas",
        "figure_claim_guardrails",
    ]
    return {
        "manifest_sha256": "a" * 64,
        "artifacts": [{"role": role} for role in roles],
    }


def test_ampetp_readiness_report_passes_complete_bundle():
    report = ampetp_readiness_report(
        bundle_manifest=_bundle_manifest(),
        case_study={
            "backend_predictions": [
                {"backend": "mace", "bond_count": 60},
                {"backend": "aimnet2", "bond_count": 60},
            ],
            "agreement": {"notes": ["guardrail"]},
        },
        sensitivity_summary={
            "backends": {"mace": {}, "aimnet2": {}},
            "interpretation": ["guardrail"],
        },
    )
    assert report["status"] == "paper_pilot_ready"
    assert report["failed"] == 0


def test_readiness_markdown_lists_checks():
    report = ampetp_readiness_report(
        bundle_manifest=_bundle_manifest(),
        case_study={
            "backend_predictions": [
                {"backend": "mace", "bond_count": 60},
                {"backend": "aimnet2", "bond_count": 60},
            ],
            "agreement": {"notes": ["guardrail"]},
        },
        sensitivity_summary={
            "backends": {"mace": {}, "aimnet2": {}},
            "interpretation": ["guardrail"],
        },
    )
    markdown = readiness_markdown(report)
    assert "Readiness Report" in markdown
    assert "source_provenance" in markdown


def test_readiness_report_includes_manuscript_claim_guardrails():
    report = ampetp_readiness_report(
        bundle_manifest=_bundle_manifest(),
        case_study={
            "backend_predictions": [
                {"backend": "mace", "bond_count": 60},
                {"backend": "aimnet2", "bond_count": 60},
            ],
            "agreement": {"notes": ["guardrail"]},
        },
        sensitivity_summary={
            "backends": {"mace": {}, "aimnet2": {}},
            "interpretation": ["guardrail"],
        },
        manuscript_text=(
            "AMPETP is a single crystal structure and does not support polymorph ranking claims. "
            "AMPETP is not lisdexamfetamine dimesylate. "
            "Generated perturbation structures are probes, not experimentally observed forms. "
            "Cross-backend absolute energy differences are not calibrated thermodynamic uncertainties. "
            "The CPOSS bridge still requires curated experimental stability evidence."
        ),
    )
    assert report["status"] == "paper_pilot_ready"
    assert report["failed"] == 0
    assert any(check["name"] == "manuscript_cposs_bridge_guardrail" for check in report["checks"])
