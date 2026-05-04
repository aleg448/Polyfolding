"""Build a local CrystalProbe project status dashboard."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.status import project_status_markdown, project_status_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--readiness", type=Path, default=Path("outputs/ampetp_readiness_report.json"))
    parser.add_argument("--bundle", type=Path, default=Path("outputs/ampetp_research_bundle_manifest.json"))
    parser.add_argument("--cposs", type=Path, default=Path("outputs/cposs_mini_benchmark_report.json"))
    parser.add_argument("--contrast", type=Path, default=Path("outputs/therapeutic_sensitivity_contrast_mace.json"))
    parser.add_argument("--evidence-tiers", type=Path, default=Path("outputs/crystalprobe_evidence_tiers.json"))
    parser.add_argument("--blockers", type=Path, default=Path("BLOCKERS.md"))
    parser.add_argument("--test-summary", default="54 passed, 1 skipped")
    parser.add_argument("--docker-status", default="not_run")
    parser.add_argument("--git-status", default="not_recorded")
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_project_status.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_project_status.md"))
    args = parser.parse_args()

    report = project_status_report(
        readiness=json.loads(args.readiness.read_text(encoding="utf-8")),
        bundle=json.loads(args.bundle.read_text(encoding="utf-8")),
        cposs_bridge=json.loads(args.cposs.read_text(encoding="utf-8")),
        therapeutic_contrast=json.loads(args.contrast.read_text(encoding="utf-8")) if args.contrast.exists() else None,
        evidence_tiers=json.loads(args.evidence_tiers.read_text(encoding="utf-8")) if args.evidence_tiers.exists() else None,
        blockers_text=args.blockers.read_text(encoding="utf-8"),
        test_summary=args.test_summary,
        docker_status=args.docker_status,
        git_status=args.git_status,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(project_status_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
