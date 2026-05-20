"""Small free-energy estimators with explicit abstention guardrails."""

from __future__ import annotations

from math import exp, isfinite, log
from statistics import fmean, pstdev
from typing import Iterable


R_KJ_PER_MOL_K = 0.00831446261815324


def zwanzig_delta_f(work_kj_per_mol: Iterable[float], *, temperature_K: float = 298.15) -> float:
    """Estimate free-energy difference from forward work samples using Zwanzig FEP."""

    samples = [float(value) for value in work_kj_per_mol]
    if not samples:
        raise ValueError("work samples are required")
    rt = _rt(temperature_K)
    return -rt * _log_mean_exp([-sample / rt for sample in samples])


def bennett_acceptance_delta_f(
    forward_work_kj_per_mol: Iterable[float],
    reverse_work_kj_per_mol: Iterable[float],
    *,
    temperature_K: float = 298.15,
    iterations: int = 100,
) -> float:
    """Estimate delta F with a simple equal-sample Bennett acceptance-ratio solve."""

    forward = [float(value) for value in forward_work_kj_per_mol]
    reverse = [float(value) for value in reverse_work_kj_per_mol]
    if not forward or not reverse:
        raise ValueError("forward and reverse work samples are required")
    rt = _rt(temperature_K)
    all_values = forward + [-value for value in reverse]
    lower = min(all_values) - 20 * rt
    upper = max(all_values) + 20 * rt
    for _ in range(iterations):
        midpoint = (lower + upper) / 2
        value = _bar_equation(midpoint, forward, reverse, rt)
        if value > 0:
            upper = midpoint
        else:
            lower = midpoint
    return (lower + upper) / 2


def free_energy_probe_report(
    forward_work_kj_per_mol: Iterable[float],
    *,
    reverse_work_kj_per_mol: Iterable[float] | None = None,
    temperature_K: float = 298.15,
    min_samples: int = 3,
    hysteresis_threshold_kj_per_mol: float = 5.0,
) -> dict[str, object]:
    """Compute free-energy estimates and abstain when samples are too weak."""

    forward = [float(value) for value in forward_work_kj_per_mol]
    reverse = None if reverse_work_kj_per_mol is None else [float(value) for value in reverse_work_kj_per_mol]
    if len(forward) < min_samples:
        return _abstained("abstained_insufficient_forward_samples", forward, reverse, temperature_K)
    forward_estimate = zwanzig_delta_f(forward, temperature_K=temperature_K)
    reverse_estimate = None
    bar_estimate = None
    hysteresis = None
    status = "free_energy_probe_recorded"
    if reverse is not None:
        if len(reverse) < min_samples:
            return _abstained("abstained_insufficient_reverse_samples", forward, reverse, temperature_K)
        reverse_estimate = -zwanzig_delta_f(reverse, temperature_K=temperature_K)
        hysteresis = abs(forward_estimate - reverse_estimate)
        bar_estimate = bennett_acceptance_delta_f(forward, reverse, temperature_K=temperature_K)
        if hysteresis > hysteresis_threshold_kj_per_mol:
            status = "abstained_hysteresis_too_high"
    sample_std = pstdev(forward) if len(forward) > 1 else 0.0
    return {
        "schema_version": "0.1.0",
        "status": status,
        "temperature_K": temperature_K,
        "forward_sample_count": len(forward),
        "reverse_sample_count": len(reverse or []),
        "forward_zwanzig_delta_f_kj_per_mol": forward_estimate,
        "reverse_zwanzig_delta_f_kj_per_mol": reverse_estimate,
        "bennett_delta_f_kj_per_mol": bar_estimate,
        "forward_work_mean_kj_per_mol": fmean(forward),
        "forward_work_std_kj_per_mol": sample_std,
        "hysteresis_kj_per_mol": hysteresis,
        "claim_boundary": "free-energy probe output is method evidence until convergence and verified calibration pass",
    }


def free_energy_probe_markdown(report: dict[str, object]) -> str:
    """Render free-energy probe output as Markdown."""

    lines = [
        "# CrystalProbe Free-Energy Probe",
        "",
        f"- Status: `{report['status']}`",
        f"- Temperature K: `{report['temperature_K']}`",
        f"- Forward samples: `{report['forward_sample_count']}`",
        f"- Reverse samples: `{report['reverse_sample_count']}`",
        "",
        "## Estimates",
        "",
        f"- Forward Zwanzig delta F: `{_fmt(report.get('forward_zwanzig_delta_f_kj_per_mol'))}` kJ/mol",
        f"- Reverse Zwanzig delta F: `{_fmt(report.get('reverse_zwanzig_delta_f_kj_per_mol'))}` kJ/mol",
        f"- Bennett delta F: `{_fmt(report.get('bennett_delta_f_kj_per_mol'))}` kJ/mol",
        f"- Hysteresis: `{_fmt(report.get('hysteresis_kj_per_mol'))}` kJ/mol",
        "",
        f"Claim boundary: {report['claim_boundary']}",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _abstained(status: str, forward: list[float], reverse: list[float] | None, temperature_K: float) -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "status": status,
        "temperature_K": temperature_K,
        "forward_sample_count": len(forward),
        "reverse_sample_count": len(reverse or []),
        "forward_zwanzig_delta_f_kj_per_mol": None,
        "reverse_zwanzig_delta_f_kj_per_mol": None,
        "bennett_delta_f_kj_per_mol": None,
        "forward_work_mean_kj_per_mol": fmean(forward) if forward else None,
        "forward_work_std_kj_per_mol": pstdev(forward) if len(forward) > 1 else 0.0,
        "hysteresis_kj_per_mol": None,
        "claim_boundary": "free-energy probe abstained; no thermodynamic claim is supported",
    }


def _bar_equation(delta_f: float, forward: list[float], reverse: list[float], rt: float) -> float:
    left = sum(_logistic_negative((work - delta_f) / rt) for work in forward)
    right = sum(_logistic_negative((work + delta_f) / rt) for work in reverse)
    return left - right


def _logistic_negative(value: float) -> float:
    if value >= 0:
        exponent = exp(-value)
        return exponent / (1.0 + exponent)
    return 1.0 / (1.0 + exp(value))


def _log_mean_exp(values: list[float]) -> float:
    anchor = max(values)
    total = sum(exp(value - anchor) for value in values)
    return anchor + log(total / len(values))


def _rt(temperature_K: float) -> float:
    if temperature_K <= 0 or not isfinite(temperature_K):
        raise ValueError("temperature_K must be positive and finite")
    return R_KJ_PER_MOL_K * temperature_K


def _fmt(value: object) -> str:
    if value is None:
        return "not_recorded"
    return f"{float(value):.3f}"
