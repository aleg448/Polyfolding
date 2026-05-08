from crystalprobe.insight.cposs_block_mapping import (
    cposs_block_mapping_markdown,
    cposs_block_mapping_dossier,
    cposs_block_mapping_dossier_markdown,
    cposs_block_mapping_report,
    seed_cposs_block_form_mapping_manifest,
)


def _workpack():
    return {
        "work_items": [
            {
                "candidate_id": "cbz_a_vs_b",
                "family": "CBZ",
                "priority": "high",
                "model_gap_kj_mol_per_formula_unit": 1.25,
                "model_lower_energy_structure": "A",
                "structure_a": {"block_id": "A"},
                "structure_b": {"block_id": "B"},
            }
        ]
    }


def test_cposs_block_mapping_report_lists_unmapped_candidate_blocks():
    report = cposs_block_mapping_report(_workpack(), mapping_manifest={"families": {"CBZ": {"blocks": {}}}})

    assert report["block_count"] == 2
    assert report["locked_block_count"] == 0
    assert report["promotion_ready_block_count"] == 0
    assert report["candidate_mapping_ready_count"] == 0
    assert report["family_summary"] == [
        {
            "family": "CBZ",
            "block_count": 2,
            "locked_block_count": 0,
            "promotion_ready_block_count": 0,
            "unmapped_count": 2,
        }
    ]
    assert report["block_rows"][0]["mapping_status"] == "unmapped"
    assert "experimental_form_label is required" in report["block_rows"][0]["blockers"]
    assert report["candidate_rows"][0]["blockers"] == [
        "A A: 12 mapping blockers",
        "B B: 12 mapping blockers",
    ]
    assert report["mapping_curation_queue"][0]["priority"] == "high"
    assert report["mapping_curation_queue"][0]["model_gap_kj_mol_per_formula_unit"] == 1.25
    assert report["block_curation_queue"][0]["priority"] == "high"
    assert report["block_curation_queue"][0]["candidate_count"] == 1
    assert report["block_curation_queue"][0]["top_candidate_id"] == "cbz_a_vs_b"


def test_cposs_block_mapping_report_accepts_locked_high_confidence_blocks():
    manifest = {
        "families": {
            "CBZ": {
                "blocks": {
                    "A": _locked_mapping("Form III"),
                    "B": _locked_mapping("Form I"),
                }
            }
        }
    }

    report = cposs_block_mapping_report(_workpack(), mapping_manifest=manifest)

    assert report["locked_block_count"] == 2
    assert report["promotion_ready_block_count"] == 2
    assert report["candidate_mapping_ready_count"] == 1
    assert report["candidate_rows"][0]["mapping_ready"] is True
    assert report["mapping_curation_queue"] == []
    assert report["block_curation_queue"] == []


def test_cposs_block_mapping_markdown_includes_queue_and_pair_gate():
    markdown = cposs_block_mapping_markdown(cposs_block_mapping_report(_workpack()))

    assert "# CPOSS Block-to-Form Mapping" in markdown
    assert "## Mapping Curation Queue" in markdown
    assert "## Block Curation Queue" in markdown
    assert "| `high` | `cbz_a_vs_b` | `CBZ` | 1.250 | `A` | `B` |" in markdown
    assert "| `high` | `CBZ` | `A` | `1` | 1.250 | `cbz_a_vs_b` |" in markdown
    assert "## Block Mapping Queue" in markdown
    assert "## Candidate Pair Gate" in markdown
    assert "| `CBZ` | `A` | `unmapped` |" in markdown
    assert "| `cbz_a_vs_b` | `A` | `B` | `False` |" in markdown


def test_cposs_block_mapping_dossier_defaults_to_top_block_target():
    dossier = cposs_block_mapping_dossier(cposs_block_mapping_report(_workpack()))

    assert dossier["target"]["block_id"] == "A"
    assert dossier["target"]["top_candidate_id"] == "cbz_a_vs_b"
    assert dossier["candidate_uses"][0]["candidate_id"] == "cbz_a_vs_b"
    assert dossier["required_actions"][0].startswith("Fill the block row")
    assert "experimental_form_label is required" in dossier["required_actions"]


def test_cposs_block_mapping_dossier_can_select_specific_block():
    dossier = cposs_block_mapping_dossier(cposs_block_mapping_report(_workpack()), block_id="B")

    assert dossier["target"]["block_id"] == "B"
    assert dossier["block_record"]["block_id"] == "B"


def test_cposs_block_mapping_dossier_markdown_renders_checklist():
    report = cposs_block_mapping_report(
        _workpack(),
        mapping_manifest={
            "families": {
                "CBZ": {
                    "family_source_doi": "10.0000/family",
                    "family_literature_context": "Family context.",
                    "blocks": {},
                }
            }
        },
    )
    markdown = cposs_block_mapping_dossier_markdown(cposs_block_mapping_dossier(report))

    assert markdown.startswith("# CPOSS Block Mapping Dossier")
    assert "## Current Block Record" in markdown
    assert "family_source_doi | 10.0000/family" in markdown
    assert "## Family Literature Context" in markdown
    assert "Family context." in markdown
    assert "## Candidate Uses" in markdown
    assert "## Required Actions" in markdown
    assert "`cbz_a_vs_b`" in markdown


def test_seed_cposs_block_form_mapping_manifest_preserves_existing_rows():
    manifest = seed_cposs_block_form_mapping_manifest(
        _workpack(),
        mapping_manifest={
            "families": {
                "CBZ": {
                    "family_source_doi": "10.0000/family",
                    "blocks": {"A": _locked_mapping("Form III")},
                }
            }
        },
    )

    blocks = manifest["families"]["CBZ"]["blocks"]
    assert manifest["total_block_count"] == 2
    assert blocks["A"]["experimental_form_label"] == "Form III"
    assert blocks["B"]["mapping_status"] == "unmapped"
    assert blocks["B"]["matching_evidence"]["cell_match"] is None
    assert manifest["families"]["CBZ"]["family_source_doi"] == "10.0000/family"


def _locked_mapping(label: str) -> dict:
    return {
        "mapping_status": "block_form_mapping_locked",
        "experimental_form_label": label,
        "mapping_confidence": "high",
        "citation_doi": "10.0000/example",
        "matching_evidence": {
            "cell_match": True,
            "space_group_match": True,
            "formula_match": True,
            "source_label_match": True,
        },
        "license_decision": "CC-BY-4.0",
        "disorder_annotation": "false",
        "curator": "curator",
        "reviewer": "reviewer",
    }
