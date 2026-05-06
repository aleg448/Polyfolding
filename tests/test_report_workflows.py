import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "curation" / "report_workflows_v0.1.json"
GUIDE = ROOT / "docs" / "report_workflows.md"
FULL_SUITE_PLAN = ROOT / "docs" / "full_suite_plan.md"


def test_report_workflow_manifest_scripts_exist():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scripts = {
        script
        for workflow in manifest["workflows"]
        for script in workflow["scripts"]
    }
    assert "scripts/build_ampetp_case_study.py" in scripts
    assert "scripts/build_sensitivity_contrast_report.py" in scripts
    missing = [script for script in sorted(scripts) if not (ROOT / script).is_file()]
    assert missing == []


def test_report_workflow_guide_mentions_manifest_outputs():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    guide = GUIDE.read_text(encoding="utf-8")
    assert "CrystalProbe Report Workflows" in guide
    assert "without setting `PYTHONPATH`" in guide
    assert "atomic replacement" in guide
    assert str(MANIFEST.relative_to(ROOT)).replace("\\", "/") in guide
    for workflow in manifest["workflows"]:
        assert workflow["label"] in guide
        for output in workflow["primary_outputs"]:
            assert output in guide


def test_crystalprobe_scripts_bootstrap_repo_local_imports():
    scripts = [
        path
        for path in (ROOT / "scripts").glob("*.py")
        if "crystalprobe" in path.read_text(encoding="utf-8")
    ]
    missing = [
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in scripts
        if "import _path_bootstrap" not in path.read_text(encoding="utf-8")
    ]
    assert missing == []


def test_full_suite_plan_mentions_current_cposs_and_fingerprint_summaries():
    plan = FULL_SUITE_PLAN.read_text(encoding="utf-8")
    assert "atomic output replacement" in plan
    assert "field-completion, curation-queue, and chemistry-family summaries" in plan
    assert "8 CBZ and 6 IBP blocked candidates" in plan
    assert "pre-benchmark CBZ/IBP candidate-slice tracking" in plan
