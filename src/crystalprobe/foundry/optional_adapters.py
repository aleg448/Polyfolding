"""Optional MLIP adapter placeholders with clear dependency errors."""

from __future__ import annotations

import os
from pathlib import Path

from crystalprobe.foundry.adapters import require_adapter
from crystalprobe.foundry.mlip import MLIPAdapter
from crystalprobe.uncertainty.base import EnergyForcePrediction, StructureInput


class MACEOffAdapter(MLIPAdapter):
    name = "mace_off"

    def __init__(self, model: str = "small", *, device: str | None = None) -> None:
        require_adapter("mace_off")
        from mace.calculators import mace_off
        import torch

        self.model = model
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.calculator = mace_off(model=model, device=self.device)

    def predict(self, structure: StructureInput) -> EnergyForcePrediction:
        atoms = structure.copy()
        atoms.calc = self.calculator
        energy = float(atoms.get_potential_energy())
        forces = tuple(tuple(float(value) for value in row) for row in atoms.get_forces())
        return EnergyForcePrediction(
            energy=energy,
            forces=forces,
            metadata={"adapter": self.name, "model": self.model, "device": self.device},
        )


class AIMNet2Adapter(MLIPAdapter):
    name = "aimnet2"

    def __init__(
        self,
        model: str = "aimnet2",
        *,
        device: str | None = None,
        needs_dispersion: bool = False,
        warp_cache_path: str | Path | None = None,
    ) -> None:
        require_adapter("aimnet2")
        if warp_cache_path is None:
            warp_cache_path = Path.cwd() / ".cache" / "warp"
        os.environ.setdefault("WARP_CACHE_PATH", str(warp_cache_path))
        from aimnet.calculators import AIMNet2Calculator
        import torch

        self.model = model
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.needs_dispersion = needs_dispersion
        self.calculator = AIMNet2Calculator(model=model, device=self.device, needs_dispersion=needs_dispersion)

    def predict(self, structure: StructureInput) -> EnergyForcePrediction:
        import numpy as np

        numbers = np.asarray(structure.get_atomic_numbers(), dtype=np.int64)[None, :]
        coord = np.asarray(structure.get_positions(), dtype=np.float32)[None, :, :]
        charge = np.asarray([0.0], dtype=np.float32)
        output = self.calculator.eval({"numbers": numbers, "coord": coord, "charge": charge}, forces=True)
        energy = float(output["energy"].detach().cpu().numpy()[0])
        forces_array = output["forces"].detach().cpu().numpy()[0]
        forces = tuple(tuple(float(value) for value in row) for row in forces_array)
        return EnergyForcePrediction(
            energy=energy,
            forces=forces,
            metadata={
                "adapter": self.name,
                "model": self.model,
                "device": self.device,
                "needs_dispersion": self.needs_dispersion,
            },
        )


class UMAAdapter(MLIPAdapter):
    name = "uma"

    def __init__(self, checkpoint: str | None = None) -> None:
        require_adapter("uma")
        self.checkpoint = checkpoint

    def predict(self, structure: StructureInput) -> EnergyForcePrediction:
        raise NotImplementedError("UMA prediction wiring requires fairchem model configuration.")
