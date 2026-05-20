from crystalprobe.insight.medication_generation import (
    medication_polymorph_generation_markdown,
    medication_polymorph_generation_report,
)


def test_medication_generation_marks_extracted_seed_set_needing_measurements():
    report = medication_polymorph_generation_report(
        _autonomy_report(shared_backends=[]),
        _evidence_gate("unverified_autonomous_candidate"),
        _extraction_report(),
        _evidence_manifest(),
    )

    target = report["targets"][0]
    assert target["generation_status"] == "seed_set_extracted_measurements_needed"
    assert target["extracted_seed_count"] == 2
    assert target["coordinate_bearing_seed_count"] == 2
    assert target["source_forms"] == ["Form I", "Form III"]


def test_medication_generation_requires_coordinate_bearing_seeds():
    report = medication_polymorph_generation_report(
        _autonomy_report(shared_backends=[]),
        _evidence_gate("unverified_autonomous_candidate"),
        _extraction_report(second_coordinate_status="no_deposited_coordinates"),
        _evidence_manifest(),
    )

    target = report["targets"][0]
    assert target["generation_status"] == "needs_coordinate_bearing_seeds"
    assert target["coordinate_bearing_seed_count"] == 1
    assert "atom-site coordinates" in target["blockers"][-1]


def test_medication_generation_marks_rankable_when_source_verified_and_shared_backend_ready():
    report = medication_polymorph_generation_report(
        _autonomy_report(shared_backends=["mace"]),
        _evidence_gate("source_verified_autonomous_benchmark_candidate"),
        _extraction_report(),
        _evidence_manifest(),
    )

    assert report["targets"][0]["generation_status"] == "rankable_seed_set_ready"
    assert "Start CSP/FastCSP-style" in report["targets"][0]["next_generation_step"]


def test_medication_generation_markdown_renders_policy():
    markdown = medication_polymorph_generation_markdown(
        medication_polymorph_generation_report(
            _autonomy_report(shared_backends=[]),
            _evidence_gate("unverified_autonomous_candidate"),
            _extraction_report(),
            _evidence_manifest(),
        )
    )

    assert markdown.startswith("# Medication Polymorph Generation Readiness")
    assert "Generated forms are hypotheses" in markdown
    assert "`seed_a`" in markdown


def _autonomy_report(*, shared_backends):
    return {
        "targets": [
            {
                "target": "modafinil",
                "autonomous_detection_status": "autonomous_polymorphism_candidate",
                "candidate_block_count": 2,
                "shared_measured_backends": shared_backends,
                "candidate_blocks": [
                    {"block_id": "A", "structure_id": "seed_a", "target_role": "parent"},
                    {"block_id": "B", "structure_id": "seed_b", "target_role": "parent"},
                ],
            }
        ]
    }


def _evidence_gate(claim_tier):
    return {
        "targets": [
            {
                "target": "modafinil",
                "claim_tier": claim_tier,
                "blockers": ["example blocker"] if claim_tier != "source_verified_autonomous_benchmark_candidate" else [],
            }
        ]
    }


def _extraction_report(*, second_coordinate_status="coordinate_bearing"):
    return {
        "rows": [
            {
                "structure_id": "seed_a",
                "status": "extracted",
                "coordinate_status": "coordinate_bearing",
                "output": "outputs/a.cif",
            },
            {
                "structure_id": "seed_b",
                "status": "extracted",
                "coordinate_status": second_coordinate_status,
                "output": "outputs/b.cif",
            },
        ]
    }


def _evidence_manifest():
    return {
        "records": [
            {
                "target": "modafinil",
                "form_label_map": {"source_forms": ["Form I", "Form III"]},
            }
        ]
    }
