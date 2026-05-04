from crystalprobe.insight.mini_benchmark import build_cposs_mini_benchmark_report, mini_benchmark_markdown


def test_build_cposs_mini_benchmark_report_summarizes_family():
    report = build_cposs_mini_benchmark_report(
        [
            {
                "families": {
                    "IBP": {
                        "formula_unit": "C26H36O4",
                        "structures": [
                            {
                                "block_id": "IBP01",
                                "relative_kj_mol_per_formula_unit": 0.0,
                                "local_diagnostic_flags": ["high_force_atom"],
                                "top_force_hotspot": {"atom_index": 1},
                                "top_bond_geometry_outlier": {"symbols": "O-C"},
                            },
                            {
                                "block_id": "IBP02",
                                "relative_kj_mol_per_formula_unit": 2.5,
                                "local_diagnostic_flags": [],
                            },
                        ],
                    }
                }
            }
        ],
        title="Fixture",
    )
    family = report["families"]["IBP"]
    assert report["structure_count"] == 2
    assert family["lowest_structure"] == "IBP01"
    assert family["second_gap_kj_mol"] == 2.5
    assert family["flagged_fraction"] == 0.5


def test_mini_benchmark_markdown_contains_guardrails():
    report = build_cposs_mini_benchmark_report(
        [
            {
                "families": {
                    "IBP": {
                        "formula_unit": "C26H36O4",
                        "structures": [
                            {"block_id": "IBP01", "relative_kj_mol_per_formula_unit": 0.0},
                        ],
                    }
                }
            }
        ],
        title="Fixture",
    )
    markdown = mini_benchmark_markdown(report)
    assert markdown.startswith("# Fixture")
    assert "not a curated experimental stability benchmark" in markdown
