"""Ensemble aggregation for MLIP adapters."""

from __future__ import annotations

from math import sqrt
from statistics import fmean
from typing import Iterable

from crystalprobe.uncertainty.base import EnergyForcePrediction, ModelAdapter, StructureInput


class EnsembleMLIPWrapper:
    """Aggregate multiple MLIP adapters into a calibrated prediction surface.

    The class is deliberately model-agnostic. Concrete MACE-OFF, AIMNet2, and UMA
    adapters can be added without changing downstream calibration code.
    """

    def __init__(self, models: Iterable[ModelAdapter], *, ood_threshold: float | None = None) -> None:
        self.models = list(models)
        if not self.models:
            raise ValueError("EnsembleMLIPWrapper requires at least one model")
        self.ood_threshold = ood_threshold

    def predict(self, structure: StructureInput) -> EnergyForcePrediction:
        predictions = [model.predict(structure) for model in self.models]
        energies = [prediction.energy for prediction in predictions]
        mean_energy = fmean(energies)
        energy_uncertainty = _sample_std(energies)

        ood_scores = [prediction.ood_score for prediction in predictions if prediction.ood_score is not None]
        ood_score = max(ood_scores) if ood_scores else None
        model_flags = any(prediction.ood_flag for prediction in predictions)
        threshold_flag = (
            self.ood_threshold is not None
            and ood_score is not None
            and ood_score >= self.ood_threshold
        )

        return EnergyForcePrediction(
            energy=mean_energy,
            forces=(),
            energy_uncertainty=energy_uncertainty,
            ood_score=ood_score,
            ood_flag=model_flags or threshold_flag,
            metadata={
                "ensemble_members": [getattr(model, "name", model.__class__.__name__) for model in self.models],
                "member_energies": energies,
            },
        )


def _sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = fmean(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return sqrt(variance)

