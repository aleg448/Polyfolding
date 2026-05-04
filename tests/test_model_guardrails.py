from crystalprobe.insight.model_guardrails import fairchem_guardrail_markdown, fairchem_guardrail_report, fairchem_model_guardrail


def test_omat24_guardrail_blocks_mp_corrections_and_organic_claims():
    guardrail = fairchem_model_guardrail("facebook/OMAT24")

    assert guardrail.status == "access_verified_validation_blocked"
    assert "Materials Project correction mixing" in guardrail.blocked_uses
    assert "organic molecular crystal ranking" in guardrail.blocked_uses


def test_omol25_guardrail_blocks_crystal_claims_until_validated():
    guardrail = fairchem_model_guardrail("facebook/OMol25")

    assert guardrail.status == "access_verified_validation_blocked"
    assert "CPOSS polymorph benchmark claims" in guardrail.blocked_uses


def test_fairchem_guardrail_markdown_renders_models():
    report = fairchem_guardrail_report(["facebook/UMA", "facebook/OMAT24"])
    markdown = fairchem_guardrail_markdown(report)

    assert markdown.startswith("# FAIR Chemistry Model Guardrails")
    assert "facebook/UMA" in markdown
    assert "facebook/OMAT24" in markdown
    assert "Accepted repository access is not sufficient" in markdown
