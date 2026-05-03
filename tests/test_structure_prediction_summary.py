from crystalprobe.insight.structure_predictions import (
    formula_unit_count,
    infer_common_formula_unit,
    parse_formula_counts,
    summarize_relative_structure_energies,
)


def test_parse_formula_counts():
    assert parse_formula_counts("C52H72O8") == {"C": 52, "H": 72, "O": 8}


def test_infer_common_formula_unit():
    unit = infer_common_formula_unit(["C52H72O8", "C104H144O16", "C26H36O4"])
    assert unit == {"C": 26, "H": 36, "O": 4}
    assert formula_unit_count("C104H144O16", unit) == 4


def test_summarize_relative_structure_energies_normalizes_formula_units():
    summary = summarize_relative_structure_energies(
        [
            {"block_id": "IBP01", "family_code": "IBP", "formula": "C52H72O8", "energy_ev": -400.0},
            {"block_id": "IBP02", "family_code": "IBP", "formula": "C104H144O16", "energy_ev": -808.0},
            {
                "block_id": "IBP03",
                "family_code": "IBP",
                "formula": "C26H36O4",
                "energy_ev": -198.0,
                "local_geometry": {"diagnostic_flags": ["high_force_atom"], "force_hotspots": [{"atom_index": 3}]},
            },
        ]
    )
    family = summary["families"]["IBP"]
    assert family["formula_unit"] == "C26H36O4"
    assert [row["block_id"] for row in family["structures"]] == ["IBP02", "IBP01", "IBP03"]
    assert family["structures"][2]["local_diagnostic_flags"] == ["high_force_atom"]
