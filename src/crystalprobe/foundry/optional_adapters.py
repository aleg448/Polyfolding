"""Optional MLIP adapter placeholders with clear dependency errors."""

from __future__ import annotations

import os
from pathlib import Path

from crystalprobe.foundry.adapters import require_adapter
from crystalprobe.foundry.mlip import MLIPAdapter
from crystalprobe.foundry.scope import (
    describe_structure_scope,
    structure_is_periodic,
    structure_total_charge,
)
from crystalprobe.uncertainty.base import EnergyForcePrediction, StructureInput


class MACEOffAdapter(MLIPAdapter):
    name = "mace_off"

    def __init__(self, model: str = "small", *, device: str | None = None) -> None:
        require_adapter("mace_off")
        from mace.calculators import mace_off
        import torch

        self.model = model
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.energy_reference = f"mace_off:{model}"
        self.calculator = mace_off(model=model, device=self.device)

    def predict(self, structure: StructureInput) -> EnergyForcePrediction:
        atoms = structure.copy()
        atoms.calc = self.calculator
        energy = float(atoms.get_potential_energy())
        forces = tuple(tuple(float(value) for value in row) for row in atoms.get_forces())
        return EnergyForcePrediction(
            energy=energy,
            forces=forces,
            metadata={
                "adapter": self.name,
                "model": self.model,
                "device": self.device,
                "energy_reference": self.energy_reference,
                "scope": describe_structure_scope(structure),
            },
        )


class AIMNet2Adapter(MLIPAdapter):
    name = "aimnet2"

    def __init__(
        self,
        model: str = "aimnet2",
        *,
        device: str | None = None,
        needs_dispersion: bool = False,
        charge: float = 0.0,
        allow_periodic_cluster: bool = False,
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
        self.charge = float(charge)
        # When True, a periodic input is evaluated as an isolated cluster of the
        # unit-cell atoms. This is an explicit, documented approximation; it is
        # off by default so a crystal cannot silently become a cluster energy.
        self.allow_periodic_cluster = allow_periodic_cluster
        self.energy_reference = f"aimnet2:{model}"
        self.calculator = AIMNet2Calculator(model=model, device=self.device, needs_dispersion=needs_dispersion)

    def predict(self, structure: StructureInput) -> EnergyForcePrediction:
        import numpy as np

        periodic = structure_is_periodic(structure)
        if periodic and not self.allow_periodic_cluster:
            raise ValueError(
                "AIMNet2Adapter received a periodic structure but cannot consume "
                "cell/PBC through this code path, so it would silently return a "
                "non-periodic cluster energy. Use a periodic backend (UMA task=omc) "
                "for crystals, or pass allow_periodic_cluster=True to force a "
                "documented isolated-cluster approximation."
            )

        total_charge = structure_total_charge(structure, default=self.charge)
        numbers = np.asarray(structure.get_atomic_numbers(), dtype=np.int64)[None, :]
        coord = np.asarray(structure.get_positions(), dtype=np.float32)[None, :, :]
        charge = np.asarray([total_charge], dtype=np.float32)
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
                "energy_reference": self.energy_reference,
                "total_charge": total_charge,
                "treated_as_cluster": bool(periodic),
                "scope": describe_structure_scope(structure, default_charge=self.charge),
            },
        )


class UMAAdapter(MLIPAdapter):
    name = "uma"

    def __init__(
        self,
        checkpoint: str = "uma-s-1p2",
        *,
        task_name: str = "omc",
        device: str | None = None,
    ) -> None:
        require_adapter("uma")
        import torch
        from fairchem.core import FAIRChemCalculator

        self.checkpoint = checkpoint
        self.task_name = task_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.energy_reference = f"uma:{checkpoint}:{task_name}"
        self.calculator = FAIRChemCalculator.from_model_checkpoint(
            checkpoint,
            task_name=task_name,
            device=self.device,
        )

    def predict(self, structure: StructureInput) -> EnergyForcePrediction:
        atoms = structure.copy()
        atoms.calc = self.calculator
        energy = float(atoms.get_potential_energy())
        forces = tuple(tuple(float(value) for value in row) for row in atoms.get_forces())
        return EnergyForcePrediction(
            energy=energy,
            forces=forces,
            metadata={
                "adapter": self.name,
                "checkpoint": self.checkpoint,
                "task_name": self.task_name,
                "device": self.device,
                "energy_reference": self.energy_reference,
                "scope": describe_structure_scope(structure),
            },
        )
