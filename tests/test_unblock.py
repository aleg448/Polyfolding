from crystalprobe.insight.unblock import execution_unblock_markdown, execution_unblock_report


def test_execution_unblock_report_combines_environment_backend_and_queue_blockers():
    report = execution_unblock_report(
        environment_blockers={
            "dependencies": [
                {"module": "ase", "package": "ase", "status": "missing_from_active_python", "required_for": ["CIF"]},
                {"module": "torch", "package": "torch", "status": "available", "required_for": ["MLIP"]},
            ]
        },
        medication_backend_blockers={
            "blockers": [
                {
                    "structure_id": "atomoxetine_hcl_1519130",
                    "backend": "aimnet2",
                    "status": "pending_due_execution_limit",
                    "next_action": "Run Docker command later.",
                    "command": "docker compose run example",
                }
            ]
        },
        measurement_queue={
            "items": [
                {
                    "substance": "modafinil",
                    "action_type": "curate_claim_boundary",
                    "active_runner_blocked": True,
                    "active_runner_missing_modules": ["ase"],
                    "first_step": "Use .venv",
                }
            ]
        },
    )

    assert report["status"] == "execution_unblock_queue_recorded"
    assert report["counts"] == {
        "active_python_dependency": 1,
        "backend_execution": 1,
        "queue_active_runner": 1,
    }
    assert report["environment_blockers"][0]["module"] == "ase"
    assert report["backend_blockers"][0]["command"] == "docker compose run example"
    assert report["queue_runner_blockers"][0]["substance"] == "modafinil"
    assert len(report["approval_batch"]) == 2


def test_execution_unblock_report_can_be_clear():
    report = execution_unblock_report(
        environment_blockers={"dependencies": [{"module": "torch", "status": "available"}]},
        medication_backend_blockers={"blockers": []},
        measurement_queue={"items": []},
    )

    assert report["status"] == "execution_unblock_queue_clear"
    assert report["blocker_count"] == 0
    assert report["approval_batch"] == []


def test_execution_unblock_markdown_renders_commands_and_policy():
    report = execution_unblock_report(
        environment_blockers={"dependencies": [{"module": "fairchem", "package": "fairchem-core", "status": "missing_from_active_python"}]},
        medication_backend_blockers={
            "blockers": [
                {
                    "structure_id": "modafinil",
                    "backend": "uma",
                    "status": "pending_due_execution_limit",
                    "next_action": "Run fairchem later.",
                    "command": "docker compose run --rm crystalprobe-fairchem example",
                }
            ]
        },
        measurement_queue={"items": []},
    )

    markdown = execution_unblock_markdown(report)

    assert markdown.startswith("# CrystalProbe Execution Unblock Report")
    assert "Pending Commands" in markdown
    assert "docker compose run --rm crystalprobe-fairchem example" in markdown
    assert "not a license grant" in markdown
