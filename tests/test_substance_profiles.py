from crystalprobe.insight.substance_profiles import substance_profile_markdown, substance_profile_report


def _priority():
    return {
        "priority_groups": [
            {
                "group_id": "everyday",
                "rationale": "test",
                "targets": [
                    {
                        "name": "ibuprofen",
                        "role": "analgesic",
                        "status": "measured",
                        "cposs_family_code": "IBP",
                        "next_action": "curate stability evidence",
                    },
                    {
                        "name": "carbamazepine",
                        "role": "neurology",
                        "status": "curation",
                        "cposs_family_code": "CBZ",
                        "next_action": "inspect disagreement",
                    },
                ],
            }
        ]
    }


def test_substance_profile_report_merges_cposs_disagreement():
    report = substance_profile_report(
        therapeutic_priority=_priority(),
        cposs_disagreement={
            "families": [
                {
                    "family": "IBP",
                    "backend_count": 3,
                    "ranking_consensus": True,
                    "mean_flag_jaccard": 1.0,
                    "backends": {"mace": {"lower_structure": "IBP01"}},
                },
                {
                    "family": "CBZ",
                    "backend_count": 3,
                    "ranking_consensus": False,
                    "mean_flag_jaccard": 0.33,
                    "backends": {"mace": {"lower_structure": "CBZ01"}, "uma": {"lower_structure": "CBZ03"}},
                },
            ]
        },
    )
    by_name = {profile["name"]: profile for profile in report["profiles"]}

    assert by_name["ibuprofen"]["cposs_backend_profile"]["decision"] == "high_confidence_behavioral"
    assert by_name["carbamazepine"]["cposs_backend_profile"]["decision"] == "inspect"
    assert by_name["carbamazepine"]["readiness"] == "backend_disagreement_inspection"


def test_substance_profile_report_merges_lisdexamfetamine_blocker():
    report = substance_profile_report(
        therapeutic_priority={
            "priority_groups": [
                {
                    "group_id": "adhd",
                    "targets": [{"name": "lisdexamfetamine dimesylate", "next_action": "search"}],
                }
            ]
        },
        lisdexamfetamine_proof={
            "target": {"name": "lisdexamfetamine dimesylate"},
            "proof_layers": [
                {
                    "layer": "computable_coordinates",
                    "status": "parent_conformer_measured",
                    "measurement_outputs": ["outputs/lisdexamfetamine_parent_mace.json"],
                    "blocker": "crystal coordinates missing",
                }
            ],
        },
        evidence_tiers={
            "targets": [
                {
                    "target": "lisdexamfetamine dimesylate crystal",
                    "tier": {
                        "tier": "blocked_no_coordinates",
                        "status": "blocked",
                        "blocked_claims": ["crystal-packing inference"],
                        "required_next_steps": ["obtain coordinates"],
                    },
                }
            ]
        },
    )
    profile = report["profiles"][0]

    assert profile["readiness"] == "blocked_no_crystal_coordinates"
    assert "outputs/lisdexamfetamine_parent_mace.json" in profile["measurement_outputs"]
    assert "crystal-packing inference" in profile["blocked_claims"]


def test_substance_profile_report_applies_cposs_bridge_tier_to_both_families():
    report = substance_profile_report(
        therapeutic_priority=_priority(),
        evidence_tiers={
            "targets": [
                {
                    "target": "CPOSS IBP/CBZ bridge",
                    "tier": {
                        "tier": "exploratory_local_measurement",
                        "status": "incomplete",
                        "blocked_claims": ["verified benchmark"],
                    },
                }
            ]
        },
    )
    by_name = {profile["name"]: profile for profile in report["profiles"]}

    assert by_name["ibuprofen"]["evidence_tier"] == "exploratory_local_measurement"
    assert by_name["carbamazepine"]["evidence_tier"] == "exploratory_local_measurement"


def test_substance_profile_markdown_renders_policy():
    report = substance_profile_report(
        therapeutic_priority={
            "priority_groups": [
                {
                    "group_id": "adhd",
                    "targets": [{"name": "lisdexamfetamine dimesylate", "next_action": "search"}],
                }
            ]
        },
        lisdexamfetamine_proof={
            "target": {"name": "lisdexamfetamine dimesylate"},
            "proof_layers": [{"layer": "computable_coordinates", "status": "parent_conformer_measured", "measurement_outputs": ["out.json"]}],
        },
        evidence_tiers={
            "targets": [
                {
                    "target": "lisdexamfetamine dimesylate crystal",
                    "tier": {"tier": "blocked_no_coordinates", "blocked_claims": []},
                }
            ]
        },
    )
    markdown = substance_profile_markdown(report)

    assert markdown.startswith("# CrystalProbe Substance Profiles")
    assert "not medical advice" in markdown
    assert "parent/proxy measured" in markdown
