import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "curation" / "report_workflows_v0.1.json"
GUIDE = ROOT / "docs" / "report_workflows.md"


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
    assert str(MANIFEST.relative_to(ROOT)).replace("\\", "/") in guide
    for workflow in manifest["workflows"]:
        assert workflow["label"] in guide
        for output in workflow["primary_outputs"]:
            assert output in guide
