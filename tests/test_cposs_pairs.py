from crystalprobe.insight.cposs_pairs import (
    cposs_pair_candidate_markdown,
    cposs_pair_candidate_report,
    cposs_evidence_workpack,
    cposs_evidence_workpack_markdown,
    cposs_pair_triage_markdown,
    cposs_pair_triage_report,
)


def _bridge():
    return {
        "families": {
            "IBP": {
                "structures": [
                    {
                        "block_id": "IBP01",
                        "formula": "C13H18O2",
                        "formula_unit_count": 1,
                        "relative_kj_mol_per_formula_unit": 0.0,
                        "local_diagnostic_flags": [],
                    },
                    {
                        "block_id": "IBP02",
                        "formula": "C13H18O2",
                        "formula_unit_count": 1,
                        "relative_kj_mol_per_formula_unit": 1.5,
                        "local_diagnostic_flags": ["high_force_atom"],
                    },
                    {
                        "block_id": "IBP03",
                        "formula": "C13H18O2",
                        "formula_unit_count": 1,
                        "relative_kj_mol_per_formula_unit": 4.0,
                        "local_diagnostic_flags": [],
                    },
                ]
            }
        }
    }


def test_cposs_pair_candidate_report_builds_adjacent_queue():
    report = cposs_pair_candidate_report(_bridge())
    assert report["status"] == "candidate_queue_requires_curation"
    assert report["candidate_count"] == 2
    assert report["candidates"][0]["candidate_id"] == "ibp_ibp01_vs_ibp02"
    assert report["candidates"][0]["model_lower_energy_structure"] == "IBP01"
    assert report["candidates"][0]["model_gap_kj_mol_per_formula_unit"] == 1.5
    assert report["candidates"][0]["curation_status"] == "needs_experimental_evidence"
    assert "high_force_atom" in report["candidates"][0]["diagnostic_flags"]


def test_cposs_pair_candidate_markdown_lists_guardrails():
    markdown = cposs_pair_candidate_markdown(cposs_pair_candidate_report(_bridge()))
    assert markdown.startswith("# CPOSS local pair-candidate queue")
    assert "needs_experimental_evidence" in markdown
    assert "not verified polymorph benchmark records" in markdown


def test_cposs_pair_triage_report_prioritizes_first_small_gap():
    report = cposs_pair_triage_report(cposs_pair_candidate_report(_bridge()))
    assert report["status"] == "triage_requires_human_evidence_review"
    assert report["priority_counts"]["high"] == 1
    assert report["top_candidates"][0]["candidate_id"] == "ibp_ibp01_vs_ibp02"
    assert report["top_candidates"][0]["priority"] == "high"
    assert "Find primary experimental stability citation." in report["top_candidates"][0]["evidence_tasks"]


def test_cposs_pair_triage_markdown_lists_evidence_tasks():
    markdown = cposs_pair_triage_markdown(cposs_pair_triage_report(cposs_pair_candidate_report(_bridge())))
    assert markdown.startswith("# CPOSS pair-candidate triage")
    assert "Find primary experimental stability citation" in markdown
    assert "not a verified stability claim" in markdown


def test_cposs_evidence_workpack_contains_curator_fields():
    triage = cposs_pair_triage_report(cposs_pair_candidate_report(_bridge()))
    workpack = cposs_evidence_workpack(triage, max_candidates=1)
    assert workpack["status"] == "awaiting_curator_input"
    assert workpack["work_item_count"] == 1
    form = workpack["work_items"][0]["evidence_form"]
    assert form["promotion_decision"] == "pending"
    assert "citation_doi" in form
    assert "has_disorder_a" in form
    assert workpack["work_items"][0]["structure_a"]["block_id"] == "IBP01"
    assert workpack["work_items"][0]["structure_b"]["block_id"] == "IBP02"


def test_cposs_evidence_workpack_fallback_preserves_second_structure_id():
    workpack = cposs_evidence_workpack(
        {
            "top_candidates": [
                {
                    "candidate_id": "ibp_ibp01_psicrys_vs_ibp06_psicrys",
                    "family": "IBP",
                    "priority": "high",
                    "model_gap_kj_mol_per_formula_unit": 1.2,
                    "model_lower_energy_structure": "IBP01_PsiCrys",
                    "diagnostic_flags": [],
                    "triage_reasons": [],
                }
            ]
        }
    )
    assert workpack["work_items"][0]["structure_a"]["block_id"] == "IBP01_PSICRYS"
    assert workpack["work_items"][0]["structure_b"]["block_id"] == "IBP06_PSICRYS"


def test_cposs_evidence_workpack_markdown_renders_form():
    triage = cposs_pair_triage_report(cposs_pair_candidate_report(_bridge()))
    markdown = cposs_evidence_workpack_markdown(cposs_evidence_workpack(triage, max_candidates=1))
    assert markdown.startswith("# CPOSS pair evidence workpack")
    assert "experimental_stability_ordering" in markdown
    assert "No pair with unresolved ambiguity" in markdown
