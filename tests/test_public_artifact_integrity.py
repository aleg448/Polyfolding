from crystalprobe.insight.public_artifact_integrity import (
    public_artifact_integrity_markdown,
    public_artifact_integrity_report,
)


def test_public_artifact_integrity_passes_current_public_surface():
    report = public_artifact_integrity_report()

    assert report["status"] == "public_artifact_integrity_passed"
    assert report["blocked_check_count"] == 0
    assert {check["status"] for check in report["checks"]} == {"passed"}


def test_public_artifact_integrity_markdown_lists_policy():
    markdown = public_artifact_integrity_markdown(public_artifact_integrity_report())

    assert markdown.startswith("# CrystalProbe Public Artifact Integrity")
    assert "unverified labels" in markdown
    assert "coordinate-bearing" in markdown
