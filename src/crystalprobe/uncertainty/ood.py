"""Out-of-distribution detector interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from crystalprobe.uncertainty.base import StructureInput


@dataclass(frozen=True)
class OODResult:
    score: float
    flag: bool
    method: str


class OODDetector(Protocol):
    name: str

    def score(self, structure: StructureInput) -> OODResult:
        """Return an OOD score for one structure."""

