"""Common interfaces for MLIP uncertainty wrappers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

StructureInput = Any


@dataclass(frozen=True)
class EnergyForcePrediction:
    """Single-structure prediction returned by a model or wrapper."""

    energy: float
    forces: tuple[tuple[float, float, float], ...] = ()
    energy_uncertainty: float | None = None
    force_uncertainty: tuple[tuple[float, float, float], ...] | None = None
    ood_score: float | None = None
    ood_flag: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelAdapter(Protocol):
    """Protocol implemented by concrete MACE, AIMNet2, UMA, or test adapters."""

    name: str

    def predict(self, structure: StructureInput) -> EnergyForcePrediction:
        """Predict energy and optionally forces for one structure."""

