"""Build a roadmap-level CrystalProbe status report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.roadmap import roadmap_status_markdown, roadmap_status_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-status", type=Path, default=Path("outputs/crystalprobe_project_status.json"))
    parser.add_argument("--readiness", type=Path, default=Path("outputs/ampetp_readiness_report.json"))
    parser.add_argument("--cposs", type=Path, default=Path("outputs/cposs_mini_benchmark_report.json"))
    parser.add_argument("--preprint", type=Path, default=Path("outputs/crystalprobe_chemrxiv_preprint_draft.md"))
    parser.add_argument("--joss", type=Path, default=Path("papers/joss_paper.md"))
    parser.add_argument("--fastcsp-plan", type=Path, default=Path("docs/fastcsp_integration_plan.md"))
    parser.add_argument("--release-boundary", type=Path, default=Path("outputs/crystalprobe_release_boundary.json"))
    parser.add_argument("--cposs-pair-candidates", type=Path, default=Path("outputs/cposs_pair_candidate_report.json"))
    parser.add_argument("--cposs-pair-triage", type=Path, default=Path("outputs/cposs_pair_triage_report.json"))
    parser.add_argument("--cposs-candidate-cards", type=Path, default=Path("outputs/cposs_candidate_cards.json"))
    parser.add_argument("--cposs-evidence-workpack", type=Path, default=Path("outputs/cposs_evidence_workpack.json"))
    parser.add_argument("--backend-disagreement", type=Path, default=Path("outputs/ampetp_backend_disagreement.json"))
    parser.add_argument("--cposs-backend-disagreement", type=Path, default=Path("outputs/cposs_high_priority_backend_disagreement.json"))
    parser.add_argument("--model-guardrails", type=Path, default=Path("outputs/fairchem_model_guardrails.json"))
    parser.add_argument("--uncertainty-proxy", type=Path, default=Path("outputs/crystalprobe_uncertainty_proxy_v0.json"))
    parser.add_argument("--substance-profiles", type=Path, default=Path("outputs/crystalprobe_substance_profiles.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_roadmap_status.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_roadmap_status.md"))
    args = parser.parse_args()

    report = roadmap_status_report(
        project_status=json.loads(args.project_status.read_text(encoding="utf-8")),
        readiness=json.loads(args.readiness.read_text(encoding="utf-8")),
        cposs_bridge=json.loads(args.cposs.read_text(encoding="utf-8")),
        has_preprint_draft=args.preprint.exists(),
        has_joss_draft=args.joss.exists(),
        has_fastcsp_plan=args.fastcsp_plan.exists(),
        has_release_boundary=args.release_boundary.exists(),
        has_cposs_pair_candidates=args.cposs_pair_candidates.exists(),
        has_cposs_pair_triage=args.cposs_pair_triage.exists(),
        has_cposs_candidate_cards=args.cposs_candidate_cards.exists(),
        has_cposs_evidence_workpack=args.cposs_evidence_workpack.exists(),
        has_backend_disagreement=args.backend_disagreement.exists(),
        has_cposs_backend_disagreement=args.cposs_backend_disagreement.exists(),
        has_model_guardrails=args.model_guardrails.exists(),
        has_uncertainty_proxy=args.uncertainty_proxy.exists(),
        has_substance_profiles=args.substance_profiles.exists(),
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(roadmap_status_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
