from crystalprobe.insight.medication_polymorphism import (
    medication_polymorphism_autonomy_markdown,
    medication_polymorphism_autonomy_report,
)


def test_medication_polymorphism_detects_same_formula_autonomous_candidate():
    report = medication_polymorphism_autonomy_report(
        _ingestion_report(),
        _measurement_summary(shared_backend=True),
    )

    target = report["targets"][0]
    assert report["autonomous_candidate_target_count"] == 1
    assert report["rankable_target_count"] == 1
    assert target["autonomous_detection_status"] == "autonomous_polymorphism_candidate"
    assert target["measurement_readiness"] == "rankable_within_backend"
    assert target["shared_measured_backends"] == ["mace"]
    assert target["best_formula_key"] == "C15 H15 N1 O2 S1"
    assert "enantiomeric_crystal_comparison" in target["claim_scopes"]
    assert target["candidate_blocks"][0]["stereochemical_scope"] == "single_enantiomer_s_or_plus"
    assert "route enantiomer-labeled records through enantiomeric crystal comparison" in target["blockers"]


def test_medication_polymorphism_blocks_single_structure_targets():
    report = medication_polymorphism_autonomy_report(
        {
            "targets": [
                {
                    "name": "single",
                    "selected_blocks": [_block("only", "only_1", "C1 H4", "P 1")],
                }
            ]
        },
        {"targets": []},
    )

    target = report["targets"][0]
    assert target["autonomous_detection_status"] == "single_structure_only"
    assert target["measurement_readiness"] == "insufficient_candidate_structures"
    assert "at least two eligible" in target["blockers"][0]


def test_medication_polymorphism_requires_shared_backend_for_rankable_set():
    report = medication_polymorphism_autonomy_report(
        _ingestion_report(),
        _measurement_summary(shared_backend=False),
    )

    target = report["targets"][0]
    assert target["autonomous_detection_status"] == "autonomous_polymorphism_candidate"
    assert target["measurement_readiness"] == "partial_measurement_coverage"
    assert "measure at least two candidate structures with the same backend" in target["blockers"]


def test_medication_polymorphism_markdown_renders_policy_and_actions():
    markdown = medication_polymorphism_autonomy_markdown(
        medication_polymorphism_autonomy_report(
            _ingestion_report(),
            _measurement_summary(shared_backend=False),
        )
    )

    assert markdown.startswith("# Medication Polymorphism Autonomy")
    assert "autonomous_polymorphism_candidate" in markdown
    assert "not verify polymorphism without form-label" in markdown
    assert "Enantiomer-labeled records can support enantiomeric crystal comparison" in markdown
    assert "Run the same backend" in markdown


def _ingestion_report():
    return {
        "targets": [
            {
                "name": "modafinil",
                "selected_blocks": [
                    _block("(S)-(+)modafinil", "modafinil_s", "C15 H15 N O2 S", "P 21"),
                    _block("I", "modafinil_i", "C15 H15 N O2 S", "P 1 21 1"),
                    {
                        **_block("analogue", "modafinil_analogue", "C16 H17 N O2 S", "P 1"),
                        "promote_to_profile": False,
                        "target_role": "related_analogue_not_parent_proof",
                    },
                ],
            }
        ]
    }


def _measurement_summary(*, shared_backend):
    second_backends = ["mace"] if shared_backend else []
    return {
        "targets": [
            {
                "name": "modafinil",
                "blocks": [
                    _measurement("modafinil_s", ["mace"]),
                    _measurement("modafinil_i", second_backends),
                ],
            }
        ]
    }


def _block(block_id, structure_id, formula, space_group):
    return {
        "block_id": block_id,
        "structure_id": structure_id,
        "target_role": "parent_medication_candidate",
        "promote_to_profile": True,
        "formula": formula,
        "space_group": space_group,
    }


def _measurement(structure_id, backends):
    return {
        "structure_id": structure_id,
        "backend_measurements": [
            {"backend": backend, "status": "measured", "diagnostic_flags": []}
            for backend in backends
        ],
    }
