from crystalprobe.uncertainty.proxy import disagreement_uncertainty_proxy, uncertainty_proxy_markdown


def test_uncertainty_proxy_marks_disagreement_for_inspection():
    report = disagreement_uncertainty_proxy(
        [
            {
                "title": "CPOSS",
                "status": "cposs_backend_disagreement_recorded",
                "overall": {"ranking_consensus_fraction": 0.5, "mean_flag_jaccard": 0.3},
            }
        ]
    )

    assert report["targets"][0]["decision"] == "inspect"
    assert "ranking disagreement" in report["targets"][0]["reason"]


def test_uncertainty_proxy_marks_full_agreement_high_confidence_behavioral():
    report = disagreement_uncertainty_proxy(
        [
            {
                "title": "AMPETP",
                "status": "backend_disagreement_recorded",
                "overall": {
                    "largest_response_consensus_fraction": 1.0,
                    "mean_flag_jaccard": 1.0,
                    "mean_pairwise_rank_disagreement": 0.0,
                },
            }
        ]
    )

    assert report["targets"][0]["decision"] == "high_confidence_behavioral"


def test_uncertainty_proxy_markdown_renders_guardrails():
    markdown = uncertainty_proxy_markdown(disagreement_uncertainty_proxy([]))

    assert markdown.startswith("# CrystalProbe disagreement uncertainty proxy")
    assert "not calibrated thermodynamic uncertainty" in markdown
