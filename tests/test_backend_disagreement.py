from crystalprobe.insight.backend_disagreement import backend_disagreement_markdown, backend_disagreement_report


def _summary():
    return {
        "reference_variant": "reference",
        "backends": {
            "mace": {
                "variants": [
                    {"variant": "reference", "energy_delta_ev": 0.0, "diagnostic_flags": []},
                    {"variant": "noise", "energy_delta_ev": 2.0, "diagnostic_flags": ["short_contact"]},
                    {"variant": "cell", "energy_delta_ev": 1.0, "diagnostic_flags": ["high_force_atom"]},
                ]
            },
            "aimnet2": {
                "variants": [
                    {"variant": "reference", "energy_delta_ev": 0.0, "diagnostic_flags": []},
                    {"variant": "noise", "energy_delta_ev": 3.0, "diagnostic_flags": ["short_contact"]},
                    {"variant": "cell", "energy_delta_ev": 0.5, "diagnostic_flags": ["high_force_atom"]},
                ]
            },
            "uma": {
                "variants": [
                    {"variant": "reference", "energy_delta_ev": 0.0, "diagnostic_flags": []},
                    {"variant": "noise", "energy_delta_ev": 1.5, "diagnostic_flags": ["short_contact"]},
                    {"variant": "cell", "energy_delta_ev": 0.25, "diagnostic_flags": []},
                ]
            },
        },
    }


def test_backend_disagreement_report_detects_largest_response_consensus():
    report = backend_disagreement_report(_summary())

    assert report["status"] == "backend_disagreement_recorded"
    assert report["backend_count"] == 3
    assert report["variant_count"] == 2
    assert report["overall"]["largest_response_consensus_fraction"] == 1.0
    assert report["backend_summaries"]["mace"]["largest_response_variant"] == "noise"


def test_backend_disagreement_markdown_renders_guardrails():
    markdown = backend_disagreement_markdown(backend_disagreement_report(_summary()))

    assert markdown.startswith("# CrystalProbe backend disagreement report")
    assert "Pairwise Disagreement" in markdown
    assert "not absolute thermodynamic energy scales" in markdown
