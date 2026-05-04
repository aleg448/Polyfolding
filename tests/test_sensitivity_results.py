from pathlib import Path

from crystalprobe.insight.sensitivity_results import load_sensitivity_rows, sensitivity_markdown, summarize_sensitivity


def test_summarize_sensitivity_uses_backend_reference():
    rows = [
        {
            "backend": "mace",
            "variant": "reference",
            "energy_ev": -10.0,
            "force_summary": {"max_force_ev_per_ang": 1.0},
            "perturbation": {"rms_position_delta_ang": 0.0, "cell_frobenius_delta_ang": 0.0},
        },
        {
            "backend": "mace",
            "variant": "noise",
            "energy_ev": -9.5,
            "force_summary": {"max_force_ev_per_ang": 1.2},
            "perturbation": {"rms_position_delta_ang": 0.01, "cell_frobenius_delta_ang": 0.0},
        },
    ]
    summary = summarize_sensitivity(rows)
    assert summary["backends"]["mace"]["max_abs_energy_delta_ev"] == 0.5
    assert summary["backends"]["mace"]["variants"][0]["variant"] == "noise"


def test_load_sensitivity_rows_validates_required_fields(tmp_path):
    path = tmp_path / "rows.jsonl"
    path.write_text('{"backend":"mace","variant":"reference","energy_ev":1.0}\n', encoding="utf-8")
    assert load_sensitivity_rows([path])[0]["variant"] == "reference"


def test_sensitivity_markdown_contains_guardrails():
    summary = summarize_sensitivity(
        [
            {
                "backend": "mace",
                "variant": "reference",
                "energy_ev": -10.0,
                "force_summary": {"max_force_ev_per_ang": 1.0},
                "perturbation": {"rms_position_delta_ang": 0.0, "cell_frobenius_delta_ang": 0.0},
            }
        ]
    )
    markdown = sensitivity_markdown(summary)
    assert markdown.startswith("# CrystalProbe Sensitivity Summary")
    assert "not experimentally observed" in markdown
