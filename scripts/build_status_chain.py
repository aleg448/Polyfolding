"""Build dependent CrystalProbe status reports in dependency order."""

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

from crystalprobe.core.io import atomic_write_json


STATUS_CHAIN_STEPS = (
    "project_status",
    "roadmap_status",
    "handoff_summary",
)


def status_chain_commands(*, test_summary: str, docker_status: str, git_status: str) -> list[tuple[str, list[str]]]:
    """Return the status-chain commands in strict dependency order."""

    return [
        (
            "project_status",
            [
                "scripts/build_project_status_dashboard.py",
                "--test-summary",
                test_summary,
                "--docker-status",
                docker_status,
                "--git-status",
                git_status,
            ],
        ),
        ("roadmap_status", ["scripts/build_roadmap_status_report.py"]),
        ("handoff_summary", ["scripts/build_handoff_report.py"]),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test-summary",
        default="not_recorded",
        help="Latest live pytest summary. Defaults to not_recorded to avoid stale verification claims.",
    )
    parser.add_argument("--docker-status", default="not_run")
    parser.add_argument("--git-status", default="not_recorded")
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_status_chain.json"))
    args = parser.parse_args()

    executed = []
    for step, command in status_chain_commands(
        test_summary=args.test_summary,
        docker_status=args.docker_status,
        git_status=args.git_status,
    ):
        subprocess.run([sys.executable, "-B", *command], check=True)
        executed.append({"step": step, "command": command})

    atomic_write_json(
        args.json_out,
        {
            "schema_version": "0.1.0",
            "status": "status_chain_built",
            "steps": executed,
            "outputs": [
                "outputs/crystalprobe_project_status.json",
                "outputs/crystalprobe_roadmap_status.json",
                "outputs/crystalprobe_handoff_summary.json",
            ],
        },
    )
    print(json.dumps({"json": str(args.json_out), "steps": [row["step"] for row in executed]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
