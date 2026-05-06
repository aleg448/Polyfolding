"""Build a readiness report for the AMPETP paper-pilot bundle."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.readiness import ampetp_readiness_report, readiness_markdown


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, default=Path("outputs/ampetp_research_bundle_manifest.json"))
    parser.add_argument("--case-study", type=Path, default=Path("outputs/ampetp_case_study_report.json"))
    parser.add_argument("--sensitivity", type=Path, default=Path("outputs/ampetp_sensitivity_summary.json"))
    parser.add_argument("--evidence-tiers", type=Path, default=Path("outputs/crystalprobe_evidence_tiers.json"))
    parser.add_argument("--preprint", type=Path, default=Path("outputs/crystalprobe_chemrxiv_preprint_draft.md"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/ampetp_readiness_report.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/ampetp_readiness_report.md"))
    args = parser.parse_args()

    report = ampetp_readiness_report(
        bundle_manifest=json.loads(args.bundle.read_text(encoding="utf-8")),
        case_study=json.loads(args.case_study.read_text(encoding="utf-8")),
        sensitivity_summary=json.loads(args.sensitivity.read_text(encoding="utf-8")),
        evidence_tiers=json.loads(args.evidence_tiers.read_text(encoding="utf-8")) if args.evidence_tiers.exists() else None,
        manuscript_text=args.preprint.read_text(encoding="utf-8") if args.preprint.exists() else None,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, readiness_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out), "status": report["status"]}, indent=2, sort_keys=True))
    return 0 if report["failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
