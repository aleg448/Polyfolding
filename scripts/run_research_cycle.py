"""Run the CrystalProbe research cycle in dependency order."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
import subprocess
import sys
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text


def research_cycle_commands(
    *,
    pair_id: str,
    test_summary: str,
    docker_status: str,
    git_status: str,
) -> list[tuple[str, list[str]]]:
    """Return research-cycle commands in dependency order."""

    return [
        ("historical_opportunities", ["scripts/build_historical_opportunity_report.py"]),
        ("active_evidence_triage", ["scripts/build_active_evidence_triage_report.py"]),
        ("evidence_packet", ["scripts/build_evidence_packet_report.py", "--pair-id", pair_id]),
        ("evidence_resolution", ["scripts/build_evidence_resolution_report.py"]),
        ("historical_research_modules", ["scripts/build_historical_research_modules_report.py"]),
        ("release_boundary", ["scripts/build_release_boundary_report.py"]),
        ("publication_readiness", ["scripts/build_publication_readiness_report.py"]),
        (
            "status_chain",
            [
                "scripts/build_status_chain.py",
                "--test-summary",
                test_summary,
                "--docker-status",
                docker_status,
                "--git-status",
                git_status,
            ],
        ),
        ("report_consistency", ["scripts/build_report_consistency_report.py"]),
        ("handoff_summary", ["scripts/build_handoff_report.py"]),
        ("report_consistency_final", ["scripts/build_report_consistency_report.py"]),
    ]


def research_cycle_markdown(report: dict[str, object]) -> str:
    lines = [
        "# CrystalProbe Research Cycle",
        "",
        f"- Status: `{report['status']}`",
        f"- Pair ID: `{report['pair_id']}`",
        f"- Test summary: `{report['test_summary']}`",
        "",
        "## Steps",
        "",
        "| Order | Step | Command |",
        "|---:|---|---|",
    ]
    for index, row in enumerate(report["steps"], start=1):  # type: ignore[index]
        command = " ".join(row["command"])
        lines.append(f"| {index} | `{row['step']}` | `{command}` |")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
        ]
    )
    lines.extend(f"- `{path}`" for path in report["outputs"])  # type: ignore[index]
    lines.extend(
        [
            "",
            "## Policy",
            "",
            "- The research cycle rebuilds evidence and status artifacts; it does not promote records by itself.",
            "- Evidence packets are promotion worklists until reviewed or verified evidence gates pass.",
            "- Report consistency should be checked before using generated handoff or publication-readiness summaries.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair-id", default="paracetamol_form_i_vs_form_ii_seed")
    parser.add_argument("--test-summary", default="not_recorded")
    parser.add_argument("--docker-status", default="not_run")
    parser.add_argument("--git-status", default="dirty")
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_research_cycle.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_research_cycle.md"))
    args = parser.parse_args()

    executed = []
    for step, command in research_cycle_commands(
        pair_id=args.pair_id,
        test_summary=args.test_summary,
        docker_status=args.docker_status,
        git_status=args.git_status,
    ):
        subprocess.run([sys.executable, "-B", *command], check=True)
        executed.append({"step": step, "command": command})
    report = {
        "schema_version": "0.1.0",
        "status": "research_cycle_built",
        "pair_id": args.pair_id,
        "test_summary": args.test_summary,
        "steps": executed,
        "outputs": [
            "outputs/crystalprobe_historical_opportunities.json",
            "outputs/crystalprobe_active_evidence_triage.json",
            "outputs/crystalprobe_evidence_packet.json",
            "outputs/crystalprobe_evidence_resolution.json",
            "outputs/crystalprobe_historical_research_modules.json",
            "outputs/crystalprobe_release_boundary.json",
            "outputs/crystalprobe_publication_readiness.json",
            "outputs/crystalprobe_status_chain.json",
            "outputs/crystalprobe_report_consistency.json",
            "outputs/crystalprobe_handoff_summary.json",
        ],
    }
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, research_cycle_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
