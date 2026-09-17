"""Ensemble aggregation for MLIP adapters."""

from __future__ import annotations

from math import isfinite
from statistics import fmean, stdev
from typing import Iterable

from crystalprobe.uncertainty.base import EnergyForcePrediction, ModelAdapter, StructureInput


class EnsembleMLIPWrapper:
    """Aggregate compatible MLIP adapters without asserting calibration.

    The class is deliberately model-agnostic. Concrete MACE-OFF, AIMNet2, and UMA
    adapters can be added without changing downstream calibration code.
    """

    def __init__(
        self,
        models: Iterable[ModelAdapter],
        *,
        ood_threshold: float | None = None,
        allow_mixed_reference: bool = False,
    ) -> None:
        self.models = list(models)
        if not self.models:
            raise ValueError("EnsembleMLIPWrapper requires at least one model")
        self.ood_threshold = ood_threshold
        if allow_mixed_reference:
            raise ValueError("mixed energy reference averaging is unsupported; align models upstream first")
        if ood_threshold is not None and not isfinite(ood_threshold):
            raise ValueError("OOD threshold must be finite")
        self._energy_references: list[str] = []
        for model in self.models:
            reference = getattr(model, "energy_reference", None)
            if not isinstance(reference, str) or not reference.strip():
                raise ValueError("every ensemble member must declare an energy reference")
            self._energy_references.append(reference)
        declared = sorted(set(self._energy_references))
        if len(declared) > 1:
            raise ValueError(
                "EnsembleMLIPWrapper averages absolute energies, which is only "
                "meaningful when members share an energy reference. Got mixed "
                f"references {declared}. Absolute energies across MACE, AIMNet2, and "
                "UMA are not comparable; use the within-backend disagreement report "
                "instead. Explicitly align members onto a common scale upstream."
            )

    def predict(self, structure: StructureInput) -> EnergyForcePrediction:
        predictions = [model.predict(structure) for model in self.models]
        for reference, prediction in zip(self._energy_references, predictions):
            if prediction.metadata.get("energy_reference", reference) != reference:
                raise ValueError("prediction energy reference differs from the declared member reference")
        scopes = [prediction.metadata.get("scope") for prediction in predictions]
        if any(scope != scopes[0] for scope in scopes):
            raise ValueError("ensemble prediction scope is missing or incompatible across members")
        energies = [prediction.energy for prediction in predictions]
        if not all(isfinite(value) for value in energies):
            raise ValueError("ensemble energies must be finite")
        mean_energy = fmean(energies)
        energy_uncertainty = stdev(energies) if len(energies) > 1 else None
        if not isfinite(mean_energy) or (energy_uncertainty is not None and not isfinite(energy_uncertainty)):
            raise ValueError("ensemble statistics must be finite")

        ood_scores = [prediction.ood_score for prediction in predictions if prediction.ood_score is not None]
        if not all(isfinite(value) for value in ood_scores):
            raise ValueError("OOD scores must be finite")
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
                "energy_references": self._energy_references,
                "scope": scopes[0],
                "calibration_validated": False,
            },
        )
