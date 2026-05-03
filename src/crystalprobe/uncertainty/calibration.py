"""Post-hoc calibration helpers for uncertainty estimates."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean


@dataclass(frozen=True)
class CoverageResult:
    interval_multiplier: float
    covered: int
    total: int

    @property
    def coverage(self) -> float | None:
        if self.total == 0:
            return None
        return self.covered / self.total


def interval_coverage(errors: list[float], uncertainties: list[float], *, multiplier: float = 1.0) -> CoverageResult:
    """Estimate empirical coverage for symmetric uncertainty intervals."""

    if len(errors) != len(uncertainties):
        raise ValueError("errors and uncertainties must have the same length")
    covered = sum(abs(error) <= multiplier * uncertainty for error, uncertainty in zip(errors, uncertainties))
    return CoverageResult(interval_multiplier=multiplier, covered=covered, total=len(errors))


def scalar_temperature(errors: list[float], uncertainties: list[float], *, target_z: float = 1.0) -> float:
    """Return a scalar factor that brings mean absolute z-score toward target_z."""

    if len(errors) != len(uncertainties):
        raise ValueError("errors and uncertainties must have the same length")
    z_scores = [abs(error) / uncertainty for error, uncertainty in zip(errors, uncertainties) if uncertainty > 0]
    if not z_scores:
        return 1.0
    observed = fmean(z_scores)
    if target_z <= 0:
        raise ValueError("target_z must be positive")
    return observed / target_z


@dataclass(frozen=True)
class ReliabilityBin:
    lower: float
    upper: float
    count: int
    mean_confidence: float | None
    empirical_accuracy: float | None


def reliability_bins(confidences: list[float], outcomes: list[bool], *, bins: int = 10) -> list[ReliabilityBin]:
    """Compute reliability bins for confidence-calibrated binary outcomes."""

    if len(confidences) != len(outcomes):
        raise ValueError("confidences and outcomes must have the same length")
    if bins <= 0:
        raise ValueError("bins must be positive")

    rows: list[ReliabilityBin] = []
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        selected = []
        for confidence, outcome in zip(confidences, outcomes):
            in_bin = lower <= confidence <= upper if index == bins - 1 else lower <= confidence < upper
            if in_bin:
                selected.append((confidence, outcome))
        if not selected:
            rows.append(ReliabilityBin(lower=lower, upper=upper, count=0, mean_confidence=None, empirical_accuracy=None))
            continue
        bin_confidences = [confidence for confidence, _ in selected]
        bin_outcomes = [outcome for _, outcome in selected]
        rows.append(
            ReliabilityBin(
                lower=lower,
                upper=upper,
                count=len(selected),
                mean_confidence=fmean(bin_confidences),
                empirical_accuracy=sum(bin_outcomes) / len(bin_outcomes),
            )
        )
    return rows


def expected_calibration_error(confidences: list[float], outcomes: list[bool], *, bins: int = 10) -> float:
    """Return ECE for binary confidence estimates."""

    rows = reliability_bins(confidences, outcomes, bins=bins)
    total = sum(row.count for row in rows)
    if total == 0:
        return 0.0
    error = 0.0
    for row in rows:
        if row.count == 0 or row.mean_confidence is None or row.empirical_accuracy is None:
            continue
        error += (row.count / total) * abs(row.mean_confidence - row.empirical_accuracy)
    return error


def brier_score(probabilities: list[float], outcomes: list[bool]) -> float:
    """Return the binary Brier score."""

    if len(probabilities) != len(outcomes):
        raise ValueError("probabilities and outcomes must have the same length")
    if not probabilities:
        return 0.0
    return fmean((probability - float(outcome)) ** 2 for probability, outcome in zip(probabilities, outcomes))
