from crystalprobe.insight.medication_seed_ranking import medication_seed_ranking_markdown, medication_seed_ranking_report


def test_medication_seed_ranking_normalizes_and_ranks_within_backend():
    report = medication_seed_ranking_report(_autonomy(), _measurements())

    target = report["targets"][0]
    assert target["ranking_status"] == "ranked_within_backend"
    ranking = target["backend_rankings"][0]
    assert ranking["backend"] == "mace"
    assert [row["structure_id"] for row in ranking["rows"]] == ["seed_b", "seed_a"]
    assert ranking["rows"][0]["energy_ev_per_formula_unit"] == -11.0
    assert ranking["rows"][1]["delta_ev_per_formula_unit"] == 1.0
    assert target["blockers"] == ["claim blocker"]


def test_medication_seed_ranking_markdown_renders_policy():
    markdown = medication_seed_ranking_markdown(medication_seed_ranking_report(_autonomy(), _measurements()))

    assert markdown.startswith("# Medication Seed Ranking")
    assert "Do not compare absolute energies across MACE" in markdown
    assert "`seed_b`" in markdown


def _autonomy():
    return {
        "targets": [
            {
                "target": "fixture",
                "best_formula_key": "C1 H4",
                "blockers": ["claim blocker"],
                "candidate_blocks": [
                    {"structure_id": "seed_a", "block_id": "A"},
                    {"structure_id": "seed_b", "block_id": "B"},
                ],
            }
        ]
    }


def _measurements():
    return {
        "targets": [
            {
                "name": "fixture",
                "blocks": [
                    {
                        "structure_id": "seed_a",
                        "backend_measurements": [
                            {"backend": "mace", "status": "measured", "formula": "C2H8", "energy_ev": -20.0}
                        ],
                    },
                    {
                        "structure_id": "seed_b",
                        "backend_measurements": [
                            {"backend": "mace", "status": "measured", "formula": "C3H12", "energy_ev": -33.0}
                        ],
                    },
                ],
            }
        ]
    }
