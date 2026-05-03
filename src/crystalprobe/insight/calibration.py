"""Calibration diagnostics for pairwise ranking predictions."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, sqrt

from crystalprobe.benchmark.predictions import PairEnergyPredictionRecord
from crystalprobe.benchmark.schema import PolymorphPair
from crystalprobe.uncertainty.calibration import brier_score, expected_calibration_error, reliability_bins


@dataclass(frozen=True)
class PairCalibrationPoint:
    pair_id: str
    confidence: float
    correct: bool
    ood_flag: bool


@dataclass(frozen=True)
class CalibrationReport:
    points: list[PairCalibrationPoint]
    brier_score: float
    expected_calibration_error: float
    reliability_bins: list[dict[str, object]]

    def as_dict(self) -> dict[str, object]:
        return {
            "points": [point.__dict__ for point in self.points],
            "brier_score": self.brier_score,
            "expected_calibration_error": self.expected_calibration_error,
            "reliability_bins": self.reliability_bins,
        }


def build_calibration_report(
    pairs: list[PolymorphPair],
    prediction_records: list[PairEnergyPredictionRecord],
    *,
    bins: int = 10,
) -> CalibrationReport:
    """Build a binary calibration report for pairwise ranking confidence."""

    pair_by_id = {pair.pair_id: pair for pair in pairs}
    points: list[PairCalibrationPoint] = []
    for record in prediction_records:
        pair = pair_by_id.get(record.pair_id)
        if pair is None or pair.experimental_winner is None:
            continue
        predicted = "A" if record.energy_a < record.energy_b else "B" if record.energy_b < record.energy_a else "tie"
        if predicted == "tie":
            continue
        uncertainty = _combined_uncertainty(record.energy_uncertainty_a, record.energy_uncertainty_b)
        confidence = _ranking_confidence(abs(record.energy_a - record.energy_b), uncertainty)
        points.append(
            PairCalibrationPoint(
                pair_id=record.pair_id,
                confidence=confidence,
                correct=predicted == pair.experimental_winner,
                ood_flag=record.ood_flag_a or record.ood_flag_b,
            )
        )

    confidences = [point.confidence for point in points]
    outcomes = [point.correct for point in points]
    rows = [row.__dict__ for row in reliability_bins(confidences, outcomes, bins=bins)]
    return CalibrationReport(
        points=points,
        brier_score=brier_score(confidences, outcomes),
        expected_calibration_error=expected_calibration_error(confidences, outcomes, bins=bins),
        reliability_bins=rows,
    )


def _combined_uncertainty(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return sqrt(a * a + b * b)


def _ranking_confidence(gap: float, uncertainty: float | None) -> float:
    if uncertainty is None or uncertainty <= 0:
        return 1.0 if gap > 0 else 0.5
    # Smoothly maps gap/uncertainty to [0.5, 1.0).
    return 0.5 + 0.5 * (1.0 - exp(-gap / uncertainty))
