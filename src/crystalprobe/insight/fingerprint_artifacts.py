"""Readiness planning for fingerprint-paper calibration and figures."""

from __future__ import annotations

from typing import Any


FIGURE_REQUIREMENTS = [
    ("benchmark_composition", "Benchmark composition by chemistry class"),
    ("ranking_accuracy_by_slice", "Backend ranking accuracy by chemistry slice"),
    ("energy_gap_disagreement", "Energy-gap disagreement by backend"),
    ("uncertainty_calibration", "Reliability/calibration curve"),
    ("diagnostic_failure_modes", "Diagnostic failure-mode rates"),
    ("medication_case_studies", "Representative medication case-study panel"),
]


def fingerprint_artifact_plan(
    *,
    promotion_gate: dict[str, Any],
    medication_measurements: dict[str, Any] | None = None,
    generated_figures: dict[str, str] | None = None,
    minimum_pair_milestones: tuple[int, ...] = (20, 50, 100),
) -> dict[str, Any]:
    """Describe which fingerprint figures can be generated from current evidence."""

    promoted_count = int(promotion_gate.get("promoted_count", 0))
    measured_medication_targets = int((medication_measurements or {}).get("measured_target_count", 0))
    candidate_family_summary = list(promotion_gate.get("family_summary", []))
    generated_figures = generated_figures or {}
    figure_rows = []
    for figure_id, title in FIGURE_REQUIREMENTS:
        if figure_id == "medication_case_studies":
            ready = measured_medication_targets > 0
            blocker = "" if ready else "requires at least one measured medication target"
        else:
            ready = promoted_count >= minimum_pair_milestones[0]
            blocker = "" if ready else f"requires at least {minimum_pair_milestones[0]} verified benchmark pairs"
        figure_rows.append(
            {
                "figure_id": figure_id,
                "title": title,
                "status": "ready" if ready else "blocked",
                "blocker": blocker,
                "artifact_path": generated_figures.get(figure_id),
            }
        )
    return {
        "schema_version": "0.1.0",
        "status": "fingerprint_artifact_plan_recorded",
        "promoted_pair_count": promoted_count,
        "measured_medication_target_count": measured_medication_targets,
        "candidate_family_summary": candidate_family_summary,
        "milestones": [
            {
                "pair_count": count,
                "status": "reached" if promoted_count >= count else "pending",
            }
            for count in minimum_pair_milestones
        ],
        "figures": figure_rows,
        "policy": [
            "Fingerprint figures that report ranking accuracy or calibration require verified benchmark pairs.",
            "Medication case-study figures can use local-only measurements if release boundaries stay explicit.",
            "Backend disagreement remains an inspection proxy until calibrated against verified pairs.",
        ],
    }


def fingerprint_artifact_plan_markdown(report: dict[str, Any]) -> str:
    """Render fingerprint artifact readiness as Markdown."""

    lines = [
        "# CrystalProbe Fingerprint Artifact Plan",
        "",
        f"- Status: `{report['status']}`",
        f"- Promoted benchmark pairs: `{report['promoted_pair_count']}`",
        f"- Measured medication targets: `{report['measured_medication_target_count']}`",
        "",
        "## Milestones",
        "",
    ]
    lines.extend(f"- `{row['pair_count']}` pairs: `{row['status']}`" for row in report["milestones"])
    if report.get("candidate_family_summary"):
        lines.extend(
            [
                "",
                "## Candidate Family Summary",
                "",
                "| Family | Candidates | Promoted | Blocked | High Priority Blocked |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for row in report["candidate_family_summary"]:
            lines.append(
                f"| `{row['family']}` | `{row['candidate_count']}` | `{row['promoted_count']}` | "
                f"`{row['blocked_count']}` | `{row['high_priority_blocked_count']}` |"
            )
    lines.extend(
        [
            "",
            "## Figures",
            "",
            "| Figure | Status | Artifact | Blocker |",
            "|---|---|---|---|",
        ]
    )
    for row in report["figures"]:
        lines.append(
            f"| {row['title']} | `{row['status']}` | "
            f"{row.get('artifact_path') or 'not generated'} | {row['blocker'] or 'none'} |"
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"
