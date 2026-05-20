import pytest

from crystalprobe.insight.figures import (
    backend_measurement_svg,
    guardrail_svg,
    medication_case_study_svg,
    medication_stereochemistry_svg,
    provenance_flow_svg,
    sensitivity_delta_svg,
    structure_projection_svg,
)


ase = pytest.importorskip("ase")


def test_provenance_flow_svg_contains_steps():
    svg = provenance_flow_svg("Title", ["source", "extract", "measure"])
    assert svg.startswith("<svg")
    assert "source" in svg
    assert "measure" in svg


def test_backend_measurement_svg_renders_backend_names():
    svg = backend_measurement_svg(
        {
            "backend_predictions": [
                {"backend": "mace", "max_force_ev_per_ang": 1.0},
                {"backend": "aimnet2", "max_force_ev_per_ang": 2.0},
            ]
        }
    )
    assert "mace" in svg
    assert "aimnet2" in svg


def test_medication_case_study_svg_renders_targets_and_pending_runs():
    svg = medication_case_study_svg(
        {
            "targets": [
                {
                    "name": "modafinil",
                    "blocks": [
                        {
                            "measured_backend_count": 1,
                            "backend_measurements": [
                                {"backend": "mace", "status": "measured"},
                                {"backend": "uma", "status": "pending_due_limit"},
                            ],
                        }
                    ],
                }
            ]
        }
    )

    assert "modafinil" in svg
    assert "Pending backend runs" in svg


def test_medication_stereochemistry_svg_renders_enantiomer_scope():
    svg = medication_stereochemistry_svg(
        {
            "targets": [
                {
                    "target": "modafinil",
                    "stereochemistry_status": "paired_enantiomer_records_available",
                    "enantiomer_labeled_block_count": 2,
                    "claim_scopes": ["enantiomeric_crystal_comparison"],
                }
            ]
        }
    )

    assert "modafinil" in svg
    assert "2 S/R blocks" in svg
    assert "Enantiomer-labeled blocks" in svg


def test_sensitivity_delta_svg_skips_reference():
    svg = sensitivity_delta_svg(
        {
            "reference_variant": "reference",
            "backends": {
                "mace": {
                    "variants": [
                        {"variant": "reference", "energy_delta_ev": 0.0},
                        {"variant": "noise", "energy_delta_ev": 1.25},
                    ]
                }
            },
        }
    )
    assert "noise" in svg
    assert "mace: reference" not in svg


def test_guardrail_svg_contains_supported_and_blocked_claims():
    svg = guardrail_svg("Claims", ["supported"], ["blocked"])
    assert "Supported claims" in svg
    assert "blocked" in svg


def test_structure_projection_svg_renders_formula_and_elements():
    atoms = ase.Atoms("H2O", positions=[(0, 0, 0), (0, 0, 0.96), (0.9, 0, -0.25)], cell=[4, 4, 4], pbc=True)
    svg = structure_projection_svg(atoms)
    assert "H2O" in svg
    assert "Elements" in svg
    assert "<circle" in svg
