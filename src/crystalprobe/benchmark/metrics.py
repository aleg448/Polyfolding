"""Metrics for polymorph-pair ranking experiments."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from crystalprobe.benchmark.schema import PolymorphPair


@dataclass(frozen=True)
class PairEnergyPrediction:
    """Predicted energies for the two structures in a pair.

    Lower energy is interpreted as more stable.
    """

    energy_a: float
    energy_b: float

    @property
    def predicted_winner(self) -> str:
        if not isfinite(self.energy_a) or not isfinite(self.energy_b):
            return "invalid"
        if self.energy_a < self.energy_b:
            return "A"
        if self.energy_b < self.energy_a:
            return "B"
        return "tie"


@dataclass(frozen=True)
class RankingAccuracy:
    correct: int
    evaluated: int
    skipped: int

    @property
    def accuracy(self) -> float | None:
        if self.evaluated == 0:
            return None
        return self.correct / self.evaluated

    @property
    def coverage(self) -> float | None:
        """Fraction of considered pairs that were actually rankable.

        Accuracy is computed over ``evaluated`` pairs only, so a high accuracy on
        a small evaluated slice (many ties/missing predictions skipped) can be
        misleading. Coverage makes that sample size explicit as one number.
        """

        considered = self.evaluated + self.skipped
        if considered == 0:
            return None
        return self.evaluated / considered


def ranking_accuracy(
    pairs: list[PolymorphPair] | tuple[PolymorphPair, ...],
    predictions: Mapping[str, PairEnergyPrediction],
) -> RankingAccuracy:
    """Compute pairwise ranking accuracy, skipping ambiguous/tied cases."""

    correct = 0
    evaluated = 0
    skipped = 0
    for pair in pairs:
        expected = pair.experimental_winner
        prediction = predictions.get(pair.pair_id)
        if expected is None or prediction is None or prediction.predicted_winner in {"tie", "invalid"}:
            skipped += 1
            continue
        evaluated += 1
        if prediction.predicted_winner == expected:
            correct += 1
    return RankingAccuracy(correct=correct, evaluated=evaluated, skipped=skipped)
