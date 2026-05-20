"""Build a consistency report across generated CrystalProbe status artifacts."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.report_consistency import report_consistency_markdown, report_consistency_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-status", type=Path, default=Path("outputs/crystalprobe_project_status.json"))
    parser.add_argument("--roadmap-status", type=Path, default=Path("outputs/crystalprobe_roadmap_status.json"))
    parser.add_argument("--handoff-summary", type=Path, default=Path("outputs/crystalprobe_handoff_summary.json"))
    parser.add_argument("--publication-readiness", type=Path, default=Path("outputs/crystalprobe_publication_readiness.json"))
    parser.add_argument("--release-boundary", type=Path, default=Path("outputs/crystalprobe_release_boundary.json"))
    parser.add_argument("--status-chain", type=Path, default=Path("outputs/crystalprobe_status_chain.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_report_consistency.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_report_consistency.md"))
    args = parser.parse_args()

    report = report_consistency_report(
        project_status=json.loads(args.project_status.read_text(encoding="utf-8")),
        roadmap_status=json.loads(args.roadmap_status.read_text(encoding="utf-8")),
        handoff_summary=json.loads(args.handoff_summary.read_text(encoding="utf-8")),
        publication_readiness=json.loads(args.publication_readiness.read_text(encoding="utf-8")),
        release_boundary=json.loads(args.release_boundary.read_text(encoding="utf-8")),
        status_chain=json.loads(args.status_chain.read_text(encoding="utf-8")) if args.status_chain.exists() else None,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, report_consistency_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
