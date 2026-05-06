"""Structure perturbation helpers for sensitivity studies."""

from __future__ import annotations

import hashlib
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from crystalprobe.core.io import atomic_write_json


@dataclass(frozen=True)
class PerturbationSpec:
    """One deterministic perturbation to apply to an ASE Atoms object."""

    name: str
    position_sigma_ang: float = 0.0
    cell_scale: float = 1.0
    seed: int = 0

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def perturb_atoms(atoms: Any, spec: PerturbationSpec) -> Any:
    """Return a perturbed copy of an ASE Atoms object."""

    perturbed = atoms.copy()
    if spec.cell_scale != 1.0:
        perturbed.set_cell(perturbed.cell * spec.cell_scale, scale_atoms=True)
    if spec.position_sigma_ang > 0:
        rng = random.Random(spec.seed)
        positions = perturbed.get_positions()
        displacements = [
            [rng.gauss(0.0, spec.position_sigma_ang) for _axis in range(3)]
            for _atom in range(len(perturbed))
        ]
        perturbed.set_positions(positions + displacements)
    return perturbed


def summarize_perturbation(reference: Any, perturbed: Any, spec: PerturbationSpec, *, path: str | Path) -> dict[str, Any]:
    """Summarize geometric perturbation magnitude."""

    deltas = perturbed.get_positions() - reference.get_positions()
    norms = [float(sum(float(component) ** 2 for component in row) ** 0.5) for row in deltas]
    cell_delta = perturbed.cell.array - reference.cell.array
    cell_norm = float(sum(float(component) ** 2 for row in cell_delta for component in row) ** 0.5)
    output_path = Path(path)
    return {
        "name": spec.name,
        "path": str(output_path),
        "sha256": sha256_file(output_path) if output_path.exists() else None,
        "spec": spec.as_dict(),
        "natoms": len(perturbed),
        "formula": perturbed.get_chemical_formula(),
        "rms_position_delta_ang": float((sum(norm**2 for norm in norms) / len(norms)) ** 0.5) if norms else 0.0,
        "max_position_delta_ang": max(norms, default=0.0),
        "cell_frobenius_delta_ang": cell_norm,
        "pbc": [bool(value) for value in perturbed.pbc],
    }


def default_sensitivity_specs() -> list[PerturbationSpec]:
    """Default AMPETP pilot sensitivity grid."""

    return [
        PerturbationSpec(name="reference"),
        PerturbationSpec(name="pos_sigma_0p01_seed_1", position_sigma_ang=0.01, seed=1),
        PerturbationSpec(name="pos_sigma_0p03_seed_1", position_sigma_ang=0.03, seed=1),
        PerturbationSpec(name="cell_scale_0p995", cell_scale=0.995),
        PerturbationSpec(name="cell_scale_1p005", cell_scale=1.005),
        PerturbationSpec(name="cell_scale_1p005_pos_sigma_0p01_seed_2", position_sigma_ang=0.01, cell_scale=1.005, seed=2),
    ]


def sensitivity_manifest(
    *,
    title: str,
    source: str,
    block_id: str,
    variants: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a JSON-serializable sensitivity manifest."""

    return {
        "schema_version": "0.1.0",
        "title": title,
        "source": source,
        "block_id": block_id,
        "variant_count": len(variants),
        "variants": variants,
        "interpretation": [
            "Generated structures are perturbation probes, not experimentally observed forms.",
            "Run MLIP inference separately on each variant before making backend sensitivity claims.",
        ],
    }


def write_json(path: str | Path, data: dict[str, Any]) -> None:
    atomic_write_json(path, data)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
