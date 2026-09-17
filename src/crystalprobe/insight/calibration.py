"""Calibration diagnostics for pairwise ranking predictions."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, hypot, isfinite

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
    brier_score: float | None
    expected_calibration_error: float | None
    reliability_bins: list[dict[str, object]]
    excluded_predictions: list[dict[str, str]]

    def as_dict(self) -> dict[str, object]:
        return {
            "status": "heuristic_diagnostics_not_validated" if self.points else "no_eligible_evidence",
            "calibration_validated": False,
            "confidence_method": "heuristic_gap_over_combined_uncertainty",
            "evidence_scope": "verified_non_ood_pairs_with_finite_energy_and_positive_combined_uncertainty",
            "excluded_predictions": self.excluded_predictions,
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
    """Diagnose heuristic confidence on verified evidence, not validate calibration.

    The exponential mapping is not a fitted probability model. Keep low-margin
    predictions: filtering by ranking success or confidence would bias diagnostics.
    """

    pair_by_id = {pair.pair_id: pair for pair in pairs}
    points: list[PairCalibrationPoint] = []
    excluded: list[dict[str, str]] = []
    for record in prediction_records:
        pair = pair_by_id.get(record.pair_id)
        reason = _exclusion_reason(pair, record)
        if reason is not None:
            excluded.append({"pair_id": record.pair_id, "reason": reason})
            continue
        assert pair is not None
        predicted = "A" if record.energy_a < record.energy_b else "B" if record.energy_b < record.energy_a else "tie"
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
        excluded_predictions=excluded,
    )


def _combined_uncertainty(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return hypot(a, b)


def _ranking_confidence(gap: float, uncertainty: float | None) -> float:
    if not isfinite(gap) or gap < 0 or uncertainty is None or not isfinite(uncertainty) or uncertainty <= 0:
        raise ValueError("confidence requires a finite gap and positive finite uncertainty")
    # Smoothly maps gap/uncertainty to [0.5, 1.0).
    return 0.5 + 0.5 * (1.0 - exp(-gap / uncertainty))


def _exclusion_reason(pair: PolymorphPair | None, record: PairEnergyPredictionRecord) -> str | None:
    if pair is None:
        return "missing_manifest_pair"
    if pair.curation_status.value != "verified":
        return "non_verified_record"
    if pair.experimental_winner is None:
        return "undefined_experimental_winner"
    if record.energy_unit != "eV":
        return "unsupported_energy_unit"
    if not all(isfinite(value) for value in (record.energy_a, record.energy_b, record.energy_b - record.energy_a)):
        return "nonfinite_energy"
    if record.energy_a == record.energy_b:
        return "tie_prediction"
    if record.ood_flag_a or record.ood_flag_b:
        return "ood_prediction"
    a, b = record.energy_uncertainty_a, record.energy_uncertainty_b
    if a is None or b is None:
        return "missing_uncertainty"
    if not all(isfinite(value) and value >= 0 for value in (a, b)):
        return "invalid_uncertainty"
    combined = hypot(a, b)
    if not isfinite(combined) or combined <= 0:
        return "invalid_uncertainty"
    return None
