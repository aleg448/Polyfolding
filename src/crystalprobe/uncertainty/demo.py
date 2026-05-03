"""Deterministic local adapters for smoke tests and examples."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from crystalprobe.uncertainty.base import EnergyForcePrediction


@dataclass(frozen=True)
class DeterministicHashModel:
    """A tiny deterministic model used only for pipeline smoke tests.

    This is not a scientific baseline. It exists so integration code can run before
    heavyweight MLIP dependencies are installed.
    """

    name: str = "deterministic_hash_smoke_model"
    scale: float = 1.0

    def predict(self, structure: Any) -> EnergyForcePrediction:
        payload = repr(structure).encode("utf-8")
        digest = hashlib.sha256(payload).digest()
        integer = int.from_bytes(digest[:8], byteorder="big", signed=False)
        energy = self.scale * ((integer % 1_000_000) / 1_000_000.0)
        return EnergyForcePrediction(energy=energy, metadata={"adapter": self.name})

