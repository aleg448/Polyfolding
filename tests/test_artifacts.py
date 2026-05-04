import json

from crystalprobe.core.artifacts import artifact_manifest_markdown, artifact_record, build_artifact_manifest, write_artifact_manifest
from scripts.build_ampetp_research_bundle import OPTIONAL_ARTIFACTS


def test_artifact_record_hashes_file(tmp_path):
    path = tmp_path / "artifact.txt"
    path.write_text("hello", encoding="utf-8")
    record = artifact_record(path, role="fixture")
    assert record.bytes == 5
    assert len(record.sha256) == 64
    assert record.role == "fixture"


def test_build_artifact_manifest_has_stable_hash(tmp_path):
    path = tmp_path / "artifact.txt"
    path.write_text("hello", encoding="utf-8")
    record = artifact_record(path, role="fixture")
    manifest = build_artifact_manifest(title="Bundle", artifacts=[record], rebuild_commands=["echo ok"])
    assert manifest["manifest_sha256"]
    markdown = artifact_manifest_markdown(manifest)
    assert "Artifact count" in markdown
    assert "echo ok" in markdown


def test_write_artifact_manifest_outputs_json(tmp_path):
    path = tmp_path / "artifact.txt"
    path.write_text("hello", encoding="utf-8")
    manifest = build_artifact_manifest(title="Bundle", artifacts=[artifact_record(path, role="fixture")], rebuild_commands=[])
    output = tmp_path / "manifest.json"
    write_artifact_manifest(output, manifest)
    assert json.loads(output.read_text(encoding="utf-8"))["title"] == "Bundle"


def test_ampetp_bundle_has_optional_uma_artifact_role():
    assert ("outputs/ccdc_ampetp_uma.json", "uma_reference_prediction") in OPTIONAL_ARTIFACTS
