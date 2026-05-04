from crystalprobe.insight.sensitivity import default_sensitivity_specs


def test_default_sensitivity_specs_have_reference_first():
    specs = default_sensitivity_specs()
    assert specs[0].name == "reference"
    assert any(spec.position_sigma_ang > 0 for spec in specs)
    assert any(spec.cell_scale != 1.0 for spec in specs)
