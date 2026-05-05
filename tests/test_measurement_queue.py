from crystalprobe.insight.measurement_queue import measurement_queue_markdown, measurement_queue_report


def test_measurement_queue_prioritizes_blocked_coordinates_and_disagreement():
    report = measurement_queue_report(
        {
            "profiles": [
                {
                    "name": "lisdexamfetamine dimesylate",
                    "readiness": "blocked_no_crystal_coordinates",
                    "evidence_tier": "blocked_no_coordinates",
                    "measurement_outputs": ["parent.json"],
                    "next_actions": ["search coordinates"],
                },
                {
                    "name": "carbamazepine",
                    "readiness": "backend_disagreement_inspection",
                    "cposs_family_code": "CBZ",
                    "cposs_backend_profile": {"family": "CBZ"},
                },
                {
                    "name": "paracetamol",
                    "readiness": "queue_seed_needs_sources",
                },
            ]
        }
    )

    assert report["items"][0]["substance"] == "lisdexamfetamine dimesylate"
    assert report["items"][0]["action_type"] == "coordinate_acquisition"
    assert report["items"][1]["action_type"] == "inspect_backend_disagreement"
    assert report["items"][2]["action_type"] == "seed_source_discovery"


def test_measurement_queue_prioritizes_adhd_source_discovery_over_seed():
    report = measurement_queue_report(
        {
            "profiles": [
                {
                    "name": "atomoxetine hydrochloride",
                    "priority_group": "adhd_core",
                    "readiness": "source_discovery_profile",
                    "known_public_evidence": ["doi"],
                },
                {
                    "name": "aspirin",
                    "priority_group": "everyday_foundation_medicines",
                    "readiness": "queue_seed_needs_sources",
                },
            ]
        }
    )

    assert report["items"][0]["substance"] == "atomoxetine hydrochloride"
    assert report["items"][0]["action_type"] == "source_discovery"


def test_measurement_queue_markdown_renders_policy():
    markdown = measurement_queue_markdown(measurement_queue_report({"profiles": []}))

    assert markdown.startswith("# CrystalProbe measurement and curation queue")
    assert "not medical importance" in markdown
