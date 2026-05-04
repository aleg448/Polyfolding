from crystalprobe.insight.claims import claim_guardrail_summary, manuscript_guardrail_checks


COMPLETE_TEXT = """
AMPETP is a single crystal structure and does not support polymorph ranking claims.
AMPETP is not lisdexamfetamine dimesylate.
Generated perturbation structures are probes, not experimentally observed forms.
Cross-backend absolute energy differences are not calibrated thermodynamic uncertainties.
The CPOSS bridge still requires curated experimental stability evidence.
"""


def test_manuscript_guardrail_checks_pass_complete_text():
    checks = manuscript_guardrail_checks(COMPLETE_TEXT)
    summary = claim_guardrail_summary(checks)
    assert summary == {"status": "pass", "passed": 5, "failed": 0}


def test_manuscript_guardrail_checks_fail_missing_boundaries():
    checks = manuscript_guardrail_checks("AMPETP pilot.")
    summary = claim_guardrail_summary(checks)
    assert summary["status"] == "fail"
    assert summary["failed"] == 5
    assert all("Missing:" in check.detail for check in checks if check.status == "fail")
