from crystalprobe.insight.contrast import build_sensitivity_contrast_report, sensitivity_contrast_markdown


def _summary(delta, flags):
    return {
        "reference_variant": "reference",
        "backends": {
            "mace": {
                "variant_count": 2,
                "max_abs_energy_delta_ev": abs(delta),
                "mean_abs_energy_delta_ev": abs(delta) / 2,
                "variants": [
                    {"variant": "reference", "energy_delta_ev": 0.0, "diagnostic_flags": []},
                    {"variant": "noise", "energy_delta_ev": delta, "diagnostic_flags": flags},
                ],
            }
        },
    }


def test_build_sensitivity_contrast_report_compares_targets():
    report = build_sensitivity_contrast_report(
        title="Contrast",
        backend="mace",
        targets=[
            {"name": "a", "summary": _summary(1.0, ["high_force_atom"])},
            {"name": "b", "summary": _summary(-2.0, ["short_contact"])},
        ],
    )
    assert report["target_count"] == 2
    assert report["targets"][1]["largest_response_flags"] == ["short_contact"]


def test_sensitivity_contrast_markdown_has_guardrails():
    report = build_sensitivity_contrast_report(
        title="Contrast",
        backend="mace",
        targets=[{"name": "a", "summary": _summary(1.0, ["high_force_atom"])}],
    )
    markdown = sensitivity_contrast_markdown(report)
    assert markdown.startswith("# Contrast")
    assert "Interpretation Guardrails" in markdown
