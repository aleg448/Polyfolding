"""Local geometry diagnostics for crystal-structure measurements."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class AtomForceHotspot:
    atom_index: int
    symbol: str
    force_norm_ev_per_ang: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BondGeometryDiagnostic:
    atom_i: int
    atom_j: int
    symbols: str
    distance_ang: float
    covalent_radius_sum_ang: float
    covalent_ratio: float
    strain_score: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ContactDiagnostic:
    atom_i: int
    atom_j: int
    symbols: str
    distance_ang: float
    covalent_radius_sum_ang: float
    covalent_ratio: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _force_norms(forces: Iterable[Iterable[float]]) -> list[float]:
    return [math.sqrt(sum(float(component) ** 2 for component in row)) for row in forces]


def _radii_for_atoms(atoms: Any) -> list[float]:
    from ase.data import covalent_radii

    return [float(covalent_radii[number]) for number in atoms.get_atomic_numbers()]


def _distance_matrix(atoms: Any) -> list[list[float]]:
    try:
        return atoms.get_all_distances(mic=True).tolist()
    except Exception:
        return atoms.get_all_distances().tolist()


def _pair_symbol(symbols: list[str], left: int, right: int) -> str:
    return f"{symbols[left]}-{symbols[right]}"


def analyze_local_geometry(
    atoms: Any,
    *,
    forces: Iterable[Iterable[float]] | None = None,
    bond_cutoff_scale: float = 1.25,
    short_contact_scale: float = 0.75,
    max_items: int = 10,
) -> dict[str, Any]:
    """Analyze local strain and force hot spots for an ASE-like Atoms object.

    The diagnostics are geometric and force-based. They are not a physical
    decomposition of MLIP energy into unique per-bond energy terms.
    """

    symbols = list(atoms.get_chemical_symbols())
    radii = _radii_for_atoms(atoms)
    distances = _distance_matrix(atoms)
    bonds: list[BondGeometryDiagnostic] = []
    short_contacts: list[ContactDiagnostic] = []
    bonded_pairs: set[tuple[int, int]] = set()

    for left in range(len(symbols)):
        for right in range(left + 1, len(symbols)):
            distance = float(distances[left][right])
            radius_sum = radii[left] + radii[right]
            if radius_sum <= 0 or distance <= 0:
                continue
            ratio = distance / radius_sum
            if ratio <= short_contact_scale:
                short_contacts.append(
                    ContactDiagnostic(
                        atom_i=left,
                        atom_j=right,
                        symbols=_pair_symbol(symbols, left, right),
                        distance_ang=distance,
                        covalent_radius_sum_ang=radius_sum,
                        covalent_ratio=ratio,
                    )
                )
            if ratio <= bond_cutoff_scale:
                bonded_pairs.add((left, right))
                bonds.append(
                    BondGeometryDiagnostic(
                        atom_i=left,
                        atom_j=right,
                        symbols=_pair_symbol(symbols, left, right),
                        distance_ang=distance,
                        covalent_radius_sum_ang=radius_sum,
                        covalent_ratio=ratio,
                        strain_score=abs(math.log(ratio)),
                    )
                )

    force_hotspots: list[AtomForceHotspot] = []
    if forces is not None:
        for index, norm in enumerate(_force_norms(forces)):
            force_hotspots.append(AtomForceHotspot(atom_index=index, symbol=symbols[index], force_norm_ev_per_ang=norm))

    flags: list[str] = []
    if short_contacts:
        flags.append("short_contact")
    if force_hotspots and max(item.force_norm_ev_per_ang for item in force_hotspots) >= 1.0:
        flags.append("high_force_atom")
    if bonds and max(item.strain_score for item in bonds) >= 0.35:
        flags.append("bond_geometry_outlier")

    return {
        "natoms": len(symbols),
        "bond_count": len(bonded_pairs),
        "diagnostic_flags": flags,
        "force_hotspots": [
            item.as_dict()
            for item in sorted(force_hotspots, key=lambda hotspot: hotspot.force_norm_ev_per_ang, reverse=True)[:max_items]
        ],
        "bond_geometry_outliers": [
            item.as_dict()
            for item in sorted(bonds, key=lambda bond: bond.strain_score, reverse=True)[:max_items]
        ],
        "short_contacts": [
            item.as_dict()
            for item in sorted(short_contacts, key=lambda contact: contact.covalent_ratio)[:max_items]
        ],
        "notes": "Geometric and force diagnostics only; not a unique per-bond energy decomposition.",
    }
