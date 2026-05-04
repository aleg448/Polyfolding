"""Backend disagreement metrics for deterministic sensitivity summaries."""

from __future__ import annotations

from itertools import combinations
from statistics import fmean
from typing import Any


def backend_disagreement_report(
    summary: dict[str, Any],
    *,
    title: str = "CrystalProbe backend disagreement report",
) -> dict[str, Any]:
    """Compare backend response patterns in a sensitivity summary."""

    backends = summary.get("backends", {})
    reference_variant = summary.get("reference_variant", "reference")
    backend_rows = {backend: _variant_map(data, reference_variant=reference_variant) for backend, data in backends.items()}
    backend_summaries = {
        backend: _backend_response_summary(backend, variants)
        for backend, variants in sorted(backend_rows.items())
    }
    pairwise = [
        _pairwise_disagreement(left, right, backend_rows[left], backend_rows[right])
        for left, right in combinations(sorted(backend_rows), 2)
    ]
    return {
        "schema_version": "0.1.0",
        "title": title,
        "status": "backend_disagreement_recorded",
        "backend_count": len(backends),
        "variant_count": _common_variant_count(backend_rows),
        "backend_summaries": backend_summaries,
        "pairwise": pairwise,
        "overall": _overall(pairwise),
        "interpretation": [
            "Disagreement metrics compare within-backend response patterns, not absolute thermodynamic energy scales.",
            "Largest-response consensus is useful behavioural evidence, not proof of experimental stability.",
            "Flag agreement compares diagnostic categories from local geometry screens and should trigger inspection when low.",
        ],
    }


def backend_disagreement_markdown(report: dict[str, Any]) -> str:
    """Render backend disagreement metrics as Markdown."""

    lines = [
        f"# {report['title']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Backends: `{report['backend_count']}`",
        f"- Common variants: `{report['variant_count']}`",
        f"- Largest-response consensus fraction: `{float(report['overall']['largest_response_consensus_fraction']):.3f}`",
        f"- Mean pairwise rank disagreement: `{float(report['overall']['mean_pairwise_rank_disagreement']):.3f}`",
        f"- Mean diagnostic flag Jaccard: `{float(report['overall']['mean_flag_jaccard']):.3f}`",
        "",
        "## Backend Summaries",
        "",
        "| Backend | Largest-response variant | Max abs delta (eV) | Mean abs delta (eV) |",
        "|---|---|---:|---:|",
    ]
    for backend, row in report["backend_summaries"].items():
        lines.append(
            f"| {backend} | {row['largest_response_variant']} | "
            f"{float(row['max_abs_energy_delta_ev']):.6f} | {float(row['mean_abs_energy_delta_ev']):.6f} |"
        )
    lines.extend(
        [
            "",
            "## Pairwise Disagreement",
            "",
            "| Pair | Largest match | Rank disagreement | Flag Jaccard | Max-delta ratio |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for row in report["pairwise"]:
        lines.append(
            f"| {row['backend_a']} vs {row['backend_b']} | `{row['largest_response_match']}` | "
            f"{float(row['mean_abs_rank_delta']):.3f} | {float(row['mean_flag_jaccard']):.3f} | "
            f"{float(row['max_abs_delta_ratio']):.3f} |"
        )
    lines.extend(["", "## Guardrails", ""])
    lines.extend(f"- {note}" for note in report["interpretation"])
    return "\n".join(lines).rstrip() + "\n"


def _variant_map(data: dict[str, Any], *, reference_variant: str) -> dict[str, dict[str, Any]]:
    return {
        str(row["variant"]): row
        for row in data.get("variants", [])
        if row.get("variant") != reference_variant
    }


def _backend_response_summary(backend: str, variants: dict[str, dict[str, Any]]) -> dict[str, Any]:
    largest = max(variants.values(), key=lambda row: abs(float(row["energy_delta_ev"])), default={})
    deltas = [abs(float(row["energy_delta_ev"])) for row in variants.values()]
    return {
        "backend": backend,
        "variant_count": len(variants),
        "largest_response_variant": largest.get("variant"),
        "max_abs_energy_delta_ev": max(deltas, default=0.0),
        "mean_abs_energy_delta_ev": fmean(deltas) if deltas else 0.0,
    }


def _pairwise_disagreement(
    backend_a: str,
    backend_b: str,
    variants_a: dict[str, dict[str, Any]],
    variants_b: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    common = sorted(set(variants_a) & set(variants_b))
    ranks_a = _ranks(variants_a, common)
    ranks_b = _ranks(variants_b, common)
    largest_a = min(ranks_a, key=ranks_a.get) if ranks_a else None
    largest_b = min(ranks_b, key=ranks_b.get) if ranks_b else None
    rank_deltas = [abs(ranks_a[variant] - ranks_b[variant]) for variant in common]
    flag_scores = [_flag_jaccard(variants_a[variant], variants_b[variant]) for variant in common]
    max_a = max((abs(float(variants_a[variant]["energy_delta_ev"])) for variant in common), default=0.0)
    max_b = max((abs(float(variants_b[variant]["energy_delta_ev"])) for variant in common), default=0.0)
    return {
        "backend_a": backend_a,
        "backend_b": backend_b,
        "common_variant_count": len(common),
        "largest_response_a": largest_a,
        "largest_response_b": largest_b,
        "largest_response_match": largest_a == largest_b,
        "mean_abs_rank_delta": fmean(rank_deltas) if rank_deltas else 0.0,
        "mean_flag_jaccard": fmean(flag_scores) if flag_scores else 0.0,
        "max_abs_delta_ratio": _ratio(max_a, max_b),
    }


def _ranks(variants: dict[str, dict[str, Any]], common: list[str]) -> dict[str, int]:
    ordered = sorted(common, key=lambda variant: (-abs(float(variants[variant]["energy_delta_ev"])), variant))
    return {variant: rank for rank, variant in enumerate(ordered, start=1)}


def _flag_jaccard(left: dict[str, Any], right: dict[str, Any]) -> float:
    left_flags = set(left.get("diagnostic_flags", []))
    right_flags = set(right.get("diagnostic_flags", []))
    if not left_flags and not right_flags:
        return 1.0
    return len(left_flags & right_flags) / len(left_flags | right_flags)


def _ratio(left: float, right: float) -> float:
    low = min(left, right)
    high = max(left, right)
    if low == 0.0:
        return 0.0 if high == 0.0 else float("inf")
    return high / low


def _common_variant_count(backend_rows: dict[str, dict[str, dict[str, Any]]]) -> int:
    if not backend_rows:
        return 0
    common = set.intersection(*(set(rows) for rows in backend_rows.values()))
    return len(common)


def _overall(pairwise: list[dict[str, Any]]) -> dict[str, Any]:
    if not pairwise:
        return {
            "largest_response_consensus_fraction": 0.0,
            "mean_pairwise_rank_disagreement": 0.0,
            "mean_flag_jaccard": 0.0,
        }
    return {
        "largest_response_consensus_fraction": fmean(1.0 if row["largest_response_match"] else 0.0 for row in pairwise),
        "mean_pairwise_rank_disagreement": fmean(float(row["mean_abs_rank_delta"]) for row in pairwise),
        "mean_flag_jaccard": fmean(float(row["mean_flag_jaccard"]) for row in pairwise),
    }
