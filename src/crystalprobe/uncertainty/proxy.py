"""Uncalibrated uncertainty proxy from backend-disagreement reports."""

from __future__ import annotations

from statistics import fmean
from typing import Any


def disagreement_uncertainty_proxy(
    reports: list[dict[str, Any]],
    *,
    title: str = "CrystalProbe disagreement uncertainty proxy",
) -> dict[str, Any]:
    """Summarize backend disagreement as a non-calibrated uncertainty proxy."""

    targets = [_target_proxy(report) for report in reports]
    return {
        "schema_version": "0.1.0",
        "title": title,
        "status": "uncalibrated_proxy_recorded",
        "target_count": len(targets),
        "targets": targets,
        "overall": _overall(targets),
        "interpretation": [
            "This is not calibrated thermodynamic uncertainty.",
            "The proxy routes agreement/disagreement into inspect decisions for AGI-assisted triage.",
            "Use verified benchmark pairs before converting these scores into calibrated confidence.",
        ],
    }


def uncertainty_proxy_markdown(report: dict[str, Any]) -> str:
    """Render uncertainty proxy output as Markdown."""

    lines = [
        f"# {report['title']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Targets: `{report['target_count']}`",
        f"- Mean proxy score: `{float(report['overall']['mean_proxy_score']):.3f}`",
        f"- Inspect targets: `{report['overall']['inspect_count']}`",
        "",
        "| Target | Source | Decision | Proxy score | Ranking consensus | Flag agreement | Reason |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for target in report["targets"]:
        lines.append(
            f"| {target['target']} | `{target['source_status']}` | `{target['decision']}` | "
            f"{float(target['proxy_score']):.3f} | {float(target['ranking_consensus']):.3f} | "
            f"{float(target['flag_agreement']):.3f} | {target['reason']} |"
        )
    lines.extend(["", "## Guardrails", ""])
    lines.extend(f"- {note}" for note in report["interpretation"])
    return "\n".join(lines).rstrip() + "\n"


def _target_proxy(report: dict[str, Any]) -> dict[str, Any]:
    status = str(report.get("status"))
    if status == "backend_disagreement_recorded":
        target = report.get("title", "sensitivity_target")
        ranking_consensus = float(report.get("overall", {}).get("largest_response_consensus_fraction", 0.0))
        flag_agreement = float(report.get("overall", {}).get("mean_flag_jaccard", 0.0))
        rank_penalty = min(float(report.get("overall", {}).get("mean_pairwise_rank_disagreement", 0.0)) / 5.0, 1.0)
        proxy_score = _bounded_mean([ranking_consensus, flag_agreement, 1.0 - rank_penalty])
    elif status == "cposs_backend_disagreement_recorded":
        target = report.get("title", "cposs_candidate_pairs")
        ranking_consensus = float(report.get("overall", {}).get("ranking_consensus_fraction", 0.0))
        flag_agreement = float(report.get("overall", {}).get("mean_flag_jaccard", 0.0))
        proxy_score = _bounded_mean([ranking_consensus, flag_agreement])
    else:
        target = report.get("title", "unknown_target")
        ranking_consensus = 0.0
        flag_agreement = 0.0
        proxy_score = 0.0

    decision, reason = _decision(proxy_score, ranking_consensus, flag_agreement)
    return {
        "target": target,
        "source_status": status,
        "decision": decision,
        "proxy_score": proxy_score,
        "ranking_consensus": ranking_consensus,
        "flag_agreement": flag_agreement,
        "reason": reason,
    }


def _decision(proxy_score: float, ranking_consensus: float, flag_agreement: float) -> tuple[str, str]:
    if ranking_consensus < 1.0:
        return "inspect", "backend ranking disagreement present"
    if flag_agreement < 0.75:
        return "inspect", "diagnostic flag disagreement present"
    if proxy_score >= 0.9:
        return "high_confidence_behavioral", "backend response and diagnostics agree"
    return "inspect", "proxy score below high-confidence threshold"


def _overall(targets: list[dict[str, Any]]) -> dict[str, Any]:
    if not targets:
        return {"mean_proxy_score": 0.0, "inspect_count": 0}
    return {
        "mean_proxy_score": fmean(float(target["proxy_score"]) for target in targets),
        "inspect_count": sum(target["decision"] == "inspect" for target in targets),
    }


def _bounded_mean(values: list[float]) -> float:
    clipped = [max(0.0, min(1.0, value)) for value in values]
    return fmean(clipped) if clipped else 0.0
