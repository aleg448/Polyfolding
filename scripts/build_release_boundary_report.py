"""Build a conservative release-boundary report for CrystalProbe artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.release import release_boundary_markdown, release_boundary_report


DEFAULT_REPO_PATHS = [
    "README.md",
    "BLOCKERS.md",
    "data/curation/facebook_model_access_v0.1.json",
    "docs/report_workflows.md",
    "docs/facebook_model_access.md",
    "docs/full_suite_plan.md",
    "docs/sources.md",
    "papers/ampetp_case_study.md",
    "papers/joss_paper.md",
    "src/crystalprobe/insight/claims.py",
    "src/crystalprobe/insight/release.py",
    "tests/test_claims.py",
    "tests/test_release.py",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, default=Path("outputs/ampetp_research_bundle_manifest.json"))
    parser.add_argument("--workflow-manifest", type=Path, default=Path("data/curation/report_workflows_v0.1.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_release_boundary.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_release_boundary.md"))
    args = parser.parse_args()

    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    workflow_manifest = json.loads(args.workflow_manifest.read_text(encoding="utf-8"))
    artifact_paths = DEFAULT_REPO_PATHS + [artifact["path"] for artifact in bundle.get("artifacts", [])]
    report = release_boundary_report(artifact_paths=artifact_paths, workflow_manifest=workflow_manifest)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(release_boundary_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
