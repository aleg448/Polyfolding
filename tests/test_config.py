from pathlib import Path

from crystalprobe.config import load_config


def test_load_quick_config():
    config = load_config(Path("examples/quick_config.json"))
    assert config.workflow == "quick_benchmark"
    assert config.quick_benchmark.manifest.endswith("manifest.jsonl")

