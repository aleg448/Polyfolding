from pathlib import Path

from crystalprobe.openbench.quick import run_quick_benchmark


def test_quick_benchmark_writes_reports_and_ledger(tmp_path):
    result = run_quick_benchmark(
        manifest=Path("data/benchmark/v0.1/manifest.jsonl"),
        predictions=Path("examples/demo_predictions.jsonl"),
        output_dir=tmp_path / "reports",
        ledger=tmp_path / "ledger.jsonl",
    )
    assert result.report_json.exists()
    assert result.report_markdown.exists()
    assert result.calibration_json.exists()
    assert result.ledger_path is not None
    assert result.ledger_path.exists()
