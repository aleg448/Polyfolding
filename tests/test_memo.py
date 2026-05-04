from crystalprobe.insight.memo import preliminary_findings_memo


def test_preliminary_findings_memo_renders_core_sections():
    memo = preliminary_findings_memo(
        ampetp_readiness={"status": "paper_pilot_ready", "passed": 8, "failed": 0},
        ampetp_sensitivity={
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
            "target_count": 1,
            "targets": [
                {
                    "target": "AMPETP",
                    "max_abs_energy_delta_ev": 1.0,
                    "largest_response_variant": "noise",
                    "largest_response_flags": ["short_contact"],
                }
            ],
        },
    )
    assert memo.startswith("# CrystalProbe Preliminary Findings Memo")
    assert "paper_pilot_ready" in memo
    assert "CPOSS Bridge Finding" in memo
    assert "Therapeutic Sensitivity Contrast" in memo
    assert "Guardrails" in memo
