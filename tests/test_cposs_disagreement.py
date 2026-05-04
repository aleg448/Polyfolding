from crystalprobe.insight.cposs_disagreement import cposs_backend_disagreement_markdown, cposs_backend_disagreement_report


def _row(backend: str, family: str, block_id: str, formula: str, energy: float, flags=None):
    return {
        "backend": backend,
        "family_code": family,
        "block_id": block_id,
        "formula": formula,
        "energy_ev": energy,
        "force_summary": {"max_force_ev_per_ang": 1.0},
        "local_geometry": {"diagnostic_flags": flags or []},
    }


def test_cposs_backend_disagreement_detects_ranking_disagreement():
    report = cposs_backend_disagreement_report(
        {
            "mace": [
                _row("mace", "IBP", "IBP01", "C26H36O4", -10.0, ["high_force_atom"]),
                _row("mace", "IBP", "IBP02", "C26H36O4", -9.0),
            ],
            "uma": [
                _row("uma", "IBP", "IBP01", "C26H36O4", -8.0),
                _row("uma", "IBP", "IBP02", "C26H36O4", -9.0),
            ],
        }
    )

    assert report["status"] == "cposs_backend_disagreement_recorded"
    assert report["overall"]["ranking_consensus_fraction"] == 0.0
    assert report["families"][0]["ranking_consensus"] is False


def test_cposs_backend_disagreement_markdown_renders_guardrails():
    report = cposs_backend_disagreement_report(
        {
            "mace": [
                _row("mace", "IBP", "IBP01", "C26H36O4", -10.0),
                _row("mace", "IBP", "IBP02", "C26H36O4", -9.0),
            ]
        }
    )
    markdown = cposs_backend_disagreement_markdown(report)

    assert markdown.startswith("# CPOSS backend disagreement report")
    assert "Backend ordering is compared only within each backend" in markdown
