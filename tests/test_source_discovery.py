from crystalprobe.insight.source_discovery import source_discovery_markdown, source_discovery_report


def test_source_discovery_report_classifies_coordinate_access():
    report = source_discovery_report(
        {
            "targets": [
                {
                    "name": "modafinil",
                    "source_status": "candidate",
                    "structure_sources": [{"coordinate_access": "public_si_candidate"}],
                },
                {
                    "name": "atomoxetine hydrochloride",
                    "source_status": "needs validation",
                    "structure_sources": [{"coordinate_access": "publication_known_cif_not_confirmed"}],
                },
                {
                    "name": "methylphenidate hydrochloride",
                    "source_status": "not found",
                    "structure_sources": [{"coordinate_access": "not_found"}],
                },
            ],
            "policy": ["No coordinates without license review."],
        }
    )
    by_name = {target["name"]: target for target in report["targets"]}

    assert by_name["modafinil"]["actionability"] == "download_candidate"
    assert by_name["atomoxetine hydrochloride"]["actionability"] == "validate_coordinate_access"
    assert by_name["methylphenidate hydrochloride"]["actionability"] == "deeper_source_search"


def test_source_discovery_markdown_renders_policy():
    markdown = source_discovery_markdown(source_discovery_report({"targets": [], "policy": ["guardrail"]}))

    assert markdown.startswith("# CrystalProbe Source Discovery Report")
    assert "guardrail" in markdown
