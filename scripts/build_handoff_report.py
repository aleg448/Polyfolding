"""Build a compact CrystalProbe handoff summary from generated reports."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.handoff import handoff_markdown, handoff_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-status", type=Path, default=Path("outputs/crystalprobe_project_status.json"))
    parser.add_argument("--roadmap-status", type=Path, default=Path("outputs/crystalprobe_roadmap_status.json"))
    parser.add_argument("--measurement-queue", type=Path, default=Path("outputs/crystalprobe_measurement_queue.json"))
    parser.add_argument("--execution-unblock", type=Path, default=Path("outputs/crystalprobe_execution_unblock_report.json"))
    parser.add_argument("--publication-readiness", type=Path, default=Path("outputs/crystalprobe_publication_readiness.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_handoff_summary.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_handoff_summary.md"))
    args = parser.parse_args()

    report = handoff_report(
        project_status=json.loads(args.project_status.read_text(encoding="utf-8")),
        roadmap_status=json.loads(args.roadmap_status.read_text(encoding="utf-8")),
        measurement_queue=json.loads(args.measurement_queue.read_text(encoding="utf-8")),
        execution_unblock=json.loads(args.execution_unblock.read_text(encoding="utf-8")),
        publication_readiness=(
            json.loads(args.publication_readiness.read_text(encoding="utf-8"))
            if args.publication_readiness.exists()
            else None
        ),
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, handoff_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
