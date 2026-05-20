from crystalprobe.insight.medication_benchmark_evidence import (
    medication_benchmark_evidence_markdown,
    medication_benchmark_evidence_report,
)


def test_medication_benchmark_evidence_blocks_autonomous_candidate_without_dossier():
    report = medication_benchmark_evidence_report(_autonomy_report())

    row = report["targets"][0]
    assert row["claim_tier"] == "unverified_autonomous_candidate"
    assert "citation_doi_or_url" in row["missing_fields"]
    assert "citation_doi_or_url is required" in row["blockers"]


def test_medication_benchmark_evidence_promotes_complete_source_verified_candidate():
    report = medication_benchmark_evidence_report(
        _autonomy_report(),
        {"records": [_complete_dossier()]},
    )

    row = report["targets"][0]
    assert report["source_verified_autonomous_count"] == 1
    assert row["claim_tier"] == "source_verified_autonomous_benchmark_candidate"
    assert row["blockers"] == []


def test_medication_benchmark_evidence_treats_unresolved_dossier_fields_as_missing():
    report = medication_benchmark_evidence_report(
        _autonomy_report(),
        {
            "records": [
                {
                    **_complete_dossier(),
                    "form_label_map": {"mapping_status": "blocked: not mapped"},
                    "stereochemistry_decision": "pending: scope unresolved",
                    "promotion_decision": "do_not_promote_yet",
                }
            ]
        },
    )

    row = report["targets"][0]
    assert row["claim_tier"] == "unverified_autonomous_candidate"
    assert "form_label_map" in row["missing_fields"]
    assert "stereochemistry_decision" in row["missing_fields"]
    assert "promotion_decision is not promote_source_verified" in row["blockers"]


def test_medication_benchmark_evidence_never_promotes_single_structure_target():
    report = medication_benchmark_evidence_report(
        {
            "targets": [
                {
                    "target": "methylphenidate hydrochloride",
                    "autonomous_detection_status": "single_structure_only",
                    "measurement_readiness": "insufficient_candidate_structures",
                    "blockers": ["at least two eligible same-formula parent-like structures are required"],
                }
            ]
        },
        {"records": [{**_complete_dossier(), "target": "methylphenidate hydrochloride"}]},
    )

    assert report["targets"][0]["claim_tier"] == "not_a_polymorphism_candidate"
    assert "autonomous polymorphism candidate is not established" in report["targets"][0]["blockers"]


def test_medication_benchmark_evidence_markdown_renders_policy():
    markdown = medication_benchmark_evidence_markdown(medication_benchmark_evidence_report(_autonomy_report()))

    assert markdown.startswith("# Medication Benchmark Evidence Gate")
    assert "source_verified_autonomous_benchmark_candidate" in markdown
    assert "not expert-verified benchmark truth" in markdown


def _autonomy_report():
    return {
        "targets": [
            {
                "target": "modafinil",
                "autonomous_detection_status": "autonomous_polymorphism_candidate",
                "measurement_readiness": "rankable_within_backend",
                "blockers": [],
                "candidate_block_count": 2,
                "shared_measured_backends": ["mace"],
            }
        ]
    }


def _complete_dossier():
    return {
        "target": "modafinil",
        "citation_doi": "10.0000/example",
        "stability_ordering": "form_a<form_b",
        "stability_claim": "Example source states the ordering under recorded conditions.",
        "form_label_map": {"modafinil_s": "Form A", "modafinil_i": "Form B"},
        "identity_decision": "same neutral parent molecule",
        "stereochemistry_decision": "resolved same target scope",
        "license_decision": "local evidence only; no coordinate redistribution",
        "disorder_decision": "no disorder reported in selected source",
        "contradiction_search": "no contradiction found in recorded source set",
        "curator": "autonomous_crystalprobe",
        "reviewer": "autonomous_crystalprobe_second_pass",
        "promotion_decision": "promote_source_verified",
    }
