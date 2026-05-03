"""Uniform MLIP adapter base classes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from crystalprobe.uncertainty.base import EnergyForcePrediction, StructureInput


@dataclass(frozen=True)
class RelaxationResult:
    structure: StructureInput
    prediction: EnergyForcePrediction
    converged: bool
    steps: int
    metadata: dict[str, Any]


class MLIPAdapter:
    """Base class for concrete MLIP integrations."""

    name: str = "mlip"

    def predict(self, structure: StructureInput) -> EnergyForcePrediction:
        raise NotImplementedError

    def relax(self, structure: StructureInput, *, max_steps: int = 200) -> RelaxationResult:
        prediction = self.predict(structure)
        return RelaxationResult(
            structure=structure,
            prediction=prediction,
            converged=False,
            steps=0,
            metadata={"reason": "relaxation is not implemented for this adapter", "max_steps": max_steps},
        )

