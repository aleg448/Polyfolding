from pathlib import Path

from crystalprobe.benchmark.curation import readiness_report
from crystalprobe.benchmark.dataset import load_manifest


def test_seed_manifest_has_expected_curation_blockers():
    dataset = load_manifest(Path("data/benchmark/v0.1/manifest.jsonl"))
    report = readiness_report(dataset)
    assert report["draft"] == 5
    assert report["blocking_issues"] > 0

