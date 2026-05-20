from scripts.run_research_cycle import research_cycle_commands, research_cycle_markdown


def test_research_cycle_commands_order_dependency_chain():
    commands = research_cycle_commands(
        pair_id="paracetamol_form_i_vs_form_ii_seed",
        test_summary="225 passed, 3 skipped",
        docker_status="not_run",
        git_status="dirty",
    )

    assert [step for step, _ in commands] == [
        "historical_opportunities",
        "active_evidence_triage",
        "evidence_packet",
        "evidence_resolution",
        "historical_research_modules",
        "release_boundary",
        "publication_readiness",
        "status_chain",
        "report_consistency",
        "handoff_summary",
        "report_consistency_final",
    ]
    assert commands[2][1] == [
        "scripts/build_evidence_packet_report.py",
        "--pair-id",
        "paracetamol_form_i_vs_form_ii_seed",
    ]
    assert commands[3][1] == ["scripts/build_evidence_resolution_report.py"]
    assert commands[-1][1] == ["scripts/build_report_consistency_report.py"]


def test_research_cycle_markdown_lists_policy_and_outputs():
    markdown = research_cycle_markdown(
        {
            "status": "research_cycle_built",
            "pair_id": "paracetamol_form_i_vs_form_ii_seed",
            "test_summary": "225 passed, 3 skipped",
            "steps": [
                {"step": "evidence_packet", "command": ["scripts/build_evidence_packet_report.py"]},
                {"step": "evidence_resolution", "command": ["scripts/build_evidence_resolution_report.py"]},
            ],
            "outputs": [
                "outputs/crystalprobe_evidence_packet.json",
                "outputs/crystalprobe_evidence_resolution.json",
            ],
        }
    )

    assert markdown.startswith("# CrystalProbe Research Cycle")
    assert "outputs/crystalprobe_evidence_packet.json" in markdown
    assert "outputs/crystalprobe_evidence_resolution.json" in markdown
    assert "The research cycle rebuilds evidence and status artifacts" in markdown
