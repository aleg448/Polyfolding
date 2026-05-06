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


def test_measurement_queue_uses_source_discovery_actionability():
    report = measurement_queue_report(
        {
            "profiles": [
                {
                    "name": "modafinil",
                    "readiness": "source_download_candidate",
                    "source_discovery_actionability": "download_candidate",
                },
                {
                    "name": "atomoxetine hydrochloride",
                    "readiness": "coordinate_access_validation",
                    "source_discovery_actionability": "validate_coordinate_access",
                },
                {
                    "name": "methylphenidate hydrochloride",
                    "readiness": "deeper_source_search",
                    "source_discovery_actionability": "deeper_source_search",
                },
            ]
        }
    )

    assert report["items"][0]["action_type"] == "download_public_cif_candidate"
    assert report["items"][1]["action_type"] == "validate_coordinate_access"
    assert report["items"][2]["action_type"] == "deeper_source_search"


def test_measurement_queue_markdown_renders_policy():
    markdown = measurement_queue_markdown(measurement_queue_report({"profiles": []}))

    assert markdown.startswith("# CrystalProbe measurement and curation queue")
    assert "not medical importance" in markdown


def test_measurement_queue_marks_active_runner_blockers():
    report = measurement_queue_report(
        {
            "profiles": [
                {
                    "name": "modafinil",
                    "readiness": "coordinates_available_locally",
                },
                {
                    "name": "lisdexamfetamine dimesylate",
                    "readiness": "blocked_no_crystal_coordinates",
                    "evidence_tier": "blocked_no_coordinates",
                },
            ]
        },
        environment_blockers={
            "dependencies": [
                {"module": "ase", "status": "missing_from_active_python"},
                {"module": "torch", "status": "available"},
                {"module": "mace", "status": "missing_from_active_python"},
            ]
        },
    )

    by_substance = {item["substance"]: item for item in report["items"]}
    assert report["active_runner_missing_modules"] == ["ase", "mace"]
    assert report["active_runner_blocked_count"] == 1
    assert by_substance["modafinil"]["active_runner_blocked"] is True
    assert by_substance["modafinil"]["active_runner_missing_modules"] == ["ase", "mace"]
    assert by_substance["lisdexamfetamine dimesylate"]["active_runner_blocked"] is False


def test_measurement_queue_markdown_renders_active_runner_blockers():
    report = measurement_queue_report(
        {"profiles": [{"name": "carbamazepine", "readiness": "backend_disagreement_inspection"}]},
        environment_blockers={"dependencies": [{"module": "fairchem", "status": "missing_from_active_python"}]},
    )

    markdown = measurement_queue_markdown(report)

    assert "Active Runner Blockers" in markdown
    assert "carbamazepine: missing `fairchem`" in markdown
