from crystalprobe.insight.cposs_inspection import (
    cposs_disagreement_inspection_markdown,
    cposs_disagreement_inspection_report,
)


def _disagreement():
    return {
        "families": [
            {
                "family": "CBZ",
                "backend_count": 3,
                "ranking_consensus": False,
                "mean_flag_jaccard": 0.33,
                "gap_range_kj_mol_per_formula_unit": 40.0,
                "backends": {
                    "mace": {
                        "lower_structure": "CBZ01",
                        "gap_kj_mol_per_formula_unit": 2.0,
                        "lower_diagnostic_flags": ["high_force_atom"],
                        "higher_diagnostic_flags": ["high_force_atom"],
                    },
                    "uma": {
                        "lower_structure": "CBZ03",
                        "gap_kj_mol_per_formula_unit": 4.0,
                        "lower_diagnostic_flags": [],
                        "higher_diagnostic_flags": [],
                    },
                },
            }
        ]
    }


def test_cposs_disagreement_inspection_detects_ordering_and_flags():
    report = cposs_disagreement_inspection_report(_disagreement())

    assert report["status"] == "cposs_disagreement_inspection_recorded"
    assert report["family"] == "CBZ"
    assert report["ranking_consensus"] is False
    assert any("Backend ordering disagreement" in finding for finding in report["findings"])
    assert any("Diagnostic flag disagreement" in finding for finding in report["findings"])


def test_cposs_disagreement_inspection_markdown_renders_guardrail():
    markdown = cposs_disagreement_inspection_markdown(cposs_disagreement_inspection_report(_disagreement()))

    assert markdown.startswith("# CPOSS CBZ Backend-Disagreement Inspection")
    assert "backend_behaviour_inspection_only" in markdown
