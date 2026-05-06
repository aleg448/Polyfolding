from crystalprobe.insight.environment import environment_blockers_markdown, environment_blockers_report


def test_environment_report_records_missing_dependencies():
    report = environment_blockers_report(
        finder=lambda module: object() if module == "torch" else None,
        python_executable="python-under-test",
    )

    assert report["status"] == "environment_blockers_recorded"
    assert report["python_executable"] == "python-under-test"
    assert report["available_count"] == 1
    assert report["missing_count"] == report["dependency_count"] - 1
    assert any(row["module"] == "ase" and row["status"] == "missing_from_configured_runners" for row in report["dependencies"])
    assert any("ase" in item for item in report["recommendations"])


def test_environment_report_can_be_ready():
    report = environment_blockers_report(finder=lambda module: object())

    assert report["status"] == "environment_ready"
    assert report["missing_count"] == 0
    assert report["recommendations"] == []


def test_environment_report_uses_configured_runner_availability():
    report = environment_blockers_report(
        finder=lambda module: None,
        python_executable="bare-python",
        configured_runners=[
            {"name": "project_venv", "modules": {"ase": True, "torch": True, "mace": True, "aimnet": True}},
            {"name": "fairchem_venv", "modules": {"fairchem": True}},
        ],
    )

    assert report["status"] == "environment_ready"
    assert report["available_count"] == report["dependency_count"]
    ase = next(row for row in report["dependencies"] if row["module"] == "ase")
    fairchem = next(row for row in report["dependencies"] if row["module"] == "fairchem")
    assert ase["active_python_status"] == "missing"
    assert ase["available_in_runners"] == ["project_venv"]
    assert fairchem["available_in_runners"] == ["fairchem_venv"]


def test_environment_markdown_renders_dependency_table():
    report = environment_blockers_report(finder=lambda module: None, python_executable="python-under-test")

    markdown = environment_blockers_markdown(report)

    assert "# CrystalProbe Active Environment Blockers" in markdown
    assert "`python-under-test`" in markdown
    assert "| `ase` | `ase` | `missing_from_configured_runners` | `missing` | none |" in markdown
