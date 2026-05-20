"""Build a dependency-light report for the implemented historical research modules."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.benchmark.dataset import load_manifest
from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.active_evidence_triage import active_evidence_triage_report, triage_items_from_pairs
from crystalprobe.insight.free_energy_probe import free_energy_probe_report
from crystalprobe.insight.historical_opportunities import historical_opportunity_report
from crystalprobe.insight.landscape_audit import landscape_audit_report
from crystalprobe.insight.motif_prior import motif_prior_report
from crystalprobe.uncertainty.calibrated_abstention import (
    calibrated_abstention_decision,
    conformal_abs_error_threshold,
)


LANDSCAPE_SMOKE_FIXTURE = [
    {"family_id": "demo_fixture", "candidate_id": "form_a", "backend": "mace", "energy": -12.0, "fingerprint": "basin_1"},
    {"family_id": "demo_fixture", "candidate_id": "form_b", "backend": "mace", "energy": -11.6, "fingerprint": "basin_2"},
    {"family_id": "demo_fixture", "candidate_id": "form_a", "backend": "aimnet2", "energy": -8.1, "fingerprint": "basin_1"},
    {"family_id": "demo_fixture", "candidate_id": "form_b", "backend": "aimnet2", "energy": -8.4, "fingerprint": "basin_2"},
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data/benchmark/v0.1/manifest.jsonl"))
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("data/curation/historical_opportunity_matrix_v0.1.json"),
    )
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_historical_research_modules.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_historical_research_modules.md"))
    args = parser.parse_args()

    dataset = load_manifest(args.manifest)
    opportunities = historical_opportunity_report(json.loads(args.matrix.read_text(encoding="utf-8")))
    motif_priors = motif_prior_report(dataset.pairs)
    triage = active_evidence_triage_report(triage_items_from_pairs(dataset.pairs))
    landscape = landscape_audit_report(LANDSCAPE_SMOKE_FIXTURE)
    free_energy = free_energy_probe_report([4.8, 5.0, 5.2, 5.1], reverse_work_kj_per_mol=[-5.1, -4.9, -5.0, -5.2])
    conformal = conformal_abs_error_threshold([0.2, 0.4, 0.7, 0.8], coverage=0.8)
    abstention = calibrated_abstention_decision(
        predicted_gap=1.6,
        combined_uncertainty=0.4,
        conformal_threshold=float(conformal["threshold"]),
        evidence_status="candidate_unverified",
    )
    report = {
        "schema_version": "0.1.0",
        "status": "historical_research_modules_recorded",
        "claim_boundary": "This report exercises method surfaces; smoke fixtures are not scientific evidence.",
        "opportunities": opportunities,
        "motif_priors": motif_priors,
        "active_evidence_triage": triage,
        "landscape_audit": landscape,
        "free_energy_probe": free_energy,
        "calibrated_abstention": {
            "conformal_threshold": conformal,
            "decision": abstention,
        },
    }
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, _markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


def _markdown(report: dict[str, object]) -> str:
    opportunities = report["opportunities"]  # type: ignore[index]
    motif_priors = report["motif_priors"]  # type: ignore[index]
    triage = report["active_evidence_triage"]  # type: ignore[index]
    landscape = report["landscape_audit"]  # type: ignore[index]
    free_energy = report["free_energy_probe"]  # type: ignore[index]
    abstention = report["calibrated_abstention"]  # type: ignore[index]
    lines = [
        "# CrystalProbe Historical Research Modules",
        "",
        f"- Status: `{report['status']}`",
        f"- Claim boundary: {report['claim_boundary']}",
        "",
        "## Implemented Surfaces",
        "",
        f"- Historical opportunity targets: `{opportunities['opportunity_count']}`",
        f"- Motif-prior pairs: `{motif_priors['pair_count']}`",
        f"- Active-triage items: `{triage['item_count']}`",
        f"- Landscape audit status: `{landscape['status']}`",
        f"- Free-energy probe status: `{free_energy['status']}`",
        f"- Abstention decision: `{abstention['decision']['decision']}`",
        "",
        "## Next Evidence Batch",
        "",
        "| Rank | Item | Action | Priority |",
        "|---:|---|---|---:|",
    ]
    for rank, item in enumerate(triage["next_batch"], start=1):
        lines.append(f"| {rank} | `{item['item_id']}` | `{item['recommended_action']}` | {item['priority_score']} |")
    lines.extend(
        [
            "",
            "## Policy",
            "",
            "- Smoke fixtures in this report prove code paths, not chemistry.",
            "- Candidate and draft records remain unverified even when modules run successfully.",
            "- Verified evidence remains the gate for headline benchmark claims.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
