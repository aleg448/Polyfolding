from crystalprobe.insight.case_study import build_single_structure_case_study, case_study_markdown
from scripts.build_ampetp_case_study import DEFAULT_PREDICTIONS, OPTIONAL_PREDICTIONS


def _prediction(backend, energy, hotspots):
    return {
        "backend": backend,
        "energy_ev": energy,
        "formula": "C2H6O",
        "force_summary": {
            "max_force_ev_per_ang": 2.0,
            "mean_force_ev_per_ang": 1.0,
        },
        "local_geometry": {
            "bond_count": 8,
            "diagnostic_flags": ["high_force_atom"],
            "force_hotspots": [{"atom_index": index, "symbol": "H", "force_norm_ev_per_ang": 1.0} for index in hotspots],
            "bond_geometry_outliers": [
                {"atom_i": 0, "atom_j": 1, "symbols": "C-O", "strain_score": 0.1},
                {"atom_i": 1, "atom_j": 2, "symbols": "O-H", "strain_score": 0.1},
            ],
            "short_contacts": [],
        },
        "model_metadata": {"adapter": backend},
        "natoms": 9,
        "pbc": [True, True, True],
        "structure_id": "fixture",
    }


def test_build_single_structure_case_study_reports_backend_agreement():
    report = build_single_structure_case_study(
        [_prediction("a", -10.0, [1, 2, 3]), _prediction("b", -12.0, [2, 3, 4])],
        title="Fixture",
        top_n=3,
    )
    assert report["structure"]["formula"] == "C2H6O"
    assert report["agreement"]["energy_range_ev"] == 2.0
    assert round(report["agreement"]["top_force_atom_jaccard"], 3) == 0.5
    assert report["agreement"]["top_bond_outlier_jaccard"] == 1.0
    assert report["agreement"]["shared_diagnostic_flags"] == ["high_force_atom"]


def test_case_study_markdown_contains_guardrails():
    report = build_single_structure_case_study(
        [_prediction("a", -10.0, [1, 2, 3]), _prediction("b", -12.0, [2, 3, 4])],
        title="Fixture",
    )
    markdown = case_study_markdown(report)
    assert markdown.startswith("# Fixture")
    assert "Backend Measurements" in markdown
    assert "not a calibrated physical stability gap" in markdown


def test_ampetp_case_study_keeps_uma_optional():
    assert [path.name for path in DEFAULT_PREDICTIONS] == ["ccdc_ampetp_mace.json", "ccdc_ampetp_aimnet2.json"]
    assert OPTIONAL_PREDICTIONS[0].name == "ccdc_ampetp_uma.json"
