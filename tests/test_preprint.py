from crystalprobe.insight.preprint import chemrxiv_preprint_draft


def test_chemrxiv_preprint_draft_renders_expected_sections():
    draft = chemrxiv_preprint_draft(
        memo_text="# Memo\n\nSeed text.",
        readiness={"status": "paper_pilot_ready", "passed": 8, "failed": 0},
        sensitivity={
            "reference_variant": "reference",
            "backends": {
                "mace": {
                    "max_abs_energy_delta_ev": 1.0,
                    "mean_abs_energy_delta_ev": 0.5,
                    "variants": [
                        {"variant": "reference", "energy_delta_ev": 0.0, "diagnostic_flags": []},
                        {"variant": "noise", "energy_delta_ev": 1.0, "diagnostic_flags": ["short_contact"]},
                    ],
                }
            },
        },
        cposs_bridge={
            "family_count": 1,
            "structure_count": 2,
            "families": {
                "IBP": {
                    "structure_count": 2,
                    "lowest_structure": "IBP01",
                    "second_gap_kj_mol": 1.2,
                    "energy_span_kj_mol": 5.0,
                    "flagged_fraction": 0.5,
                }
            },
        },
        bundle_manifest={"manifest_sha256": "a" * 64, "artifacts": [{}, {}]},
        therapeutic_contrast={
            "backend": "mace",
            "targets": [
                {
                    "target": "AMPETP",
                    "backend": "mace",
                    "max_abs_energy_delta_ev": 1.0,
                    "mean_abs_energy_delta_ev": 0.5,
                    "largest_response_variant": "noise",
                    "largest_response_flags": ["short_contact"],
                }
            ],
        },
    )
    assert draft.startswith("# CrystalProbe:")
    assert "## Abstract" in draft
    assert "## 5. Limitations" in draft
    assert "Therapeutic Sensitivity Contrast" in draft
    assert "Seed text." in draft
