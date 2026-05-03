from pathlib import Path

from crystalprobe.benchmark.dataset import load_manifest


def test_load_seed_manifest():
    manifest = Path("data/benchmark/v0.1/manifest.jsonl")
    dataset = load_manifest(manifest)
    assert len(dataset) == 5
    assert dataset.summary()["pairs"] == 5
    assert dataset.summary()["statuses"] == {"draft": 5}

