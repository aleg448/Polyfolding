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


def _force_norms(forces: Iterable[Iterable[float]], natoms: int) -> list[float]:
    rows = [tuple(float(component) for component in row) for row in forces]
    if len(rows) != natoms or any(len(row) != 3 or not all(math.isfinite(x) for x in row) for row in rows):
        raise ValueError("forces must contain one finite three-component vector per atom")
    norms = [math.hypot(*row) for row in rows]
    if not all(math.isfinite(norm) for norm in norms):
        raise ValueError("forces have non-finite norms")
    return norms


def _radii_for_atoms(atoms: Any) -> list[float]:
    from ase.data import covalent_radii

    return [float(covalent_radii[number]) for number in atoms.get_atomic_numbers()]


def _distance_matrix(atoms: Any) -> list[list[float]]:
    return atoms.get_all_distances(mic=True).tolist()


def _pair_symbol(symbols: list[str], left: int, right: int) -> str:
    return f"{symbols[left]}-{symbols[right]}"


def _dense_pairs(atoms: Any, natoms: int) -> Iterable[tuple[int, int, float]]:
    """Yield every unique atom pair and its distance via a full distance matrix.

    O(N^2) in time and memory; used for small structures where exactness and
    parity with prior behaviour matter.
    """

    distances = _distance_matrix(atoms)
    for left in range(natoms):
        for right in range(left + 1, natoms):
            yield left, right, float(distances[left][right])


def _neighbor_pairs(atoms: Any, radii: list[float], bond_cutoff_scale: float) -> Iterable[tuple[int, int, float]]:
    """Yield candidate close pairs using an ASE neighbour list within a cutoff.

    O(N) in memory for typical atomic densities, so large crystals do not
    allocate an N*N distance matrix. The cutoff covers the largest possible bond
    distance (``bond_cutoff_scale`` times the largest covalent-radius sum).
    """

    from ase.neighborlist import neighbor_list

    cutoff = bond_cutoff_scale * 2.0 * (max(radii) if radii else 0.0)
    if cutoff <= 0:
        return
    first, second, dist = neighbor_list("ijd", atoms, cutoff)
    closest: dict[tuple[int, int], float] = {}
    for i, j, d in zip(first.tolist(), second.tolist(), dist.tolist()):
        if i >= j:
            continue
        key = (i, j)
        # ASE can return several periodic images in arbitrary order. Match the
        # dense minimum-image scan, not whichever image happens to appear first.
        closest[key] = min(closest.get(key, float("inf")), float(d))
    for (i, j), distance in sorted(closest.items()):
        yield i, j, distance


def analyze_local_geometry(
    atoms: Any,
    *,
    forces: Iterable[Iterable[float]] | None = None,
    bond_cutoff_scale: float = 1.25,
    short_contact_scale: float = 0.75,
    max_items: int = 10,
    max_dense_atoms: int = 1500,
) -> dict[str, Any]:
    """Analyze local strain and force hot spots for an ASE-like Atoms object.

    The diagnostics are geometric and force-based. They are not a physical
    decomposition of MLIP energy into unique per-bond energy terms.

    Structures with at most ``max_dense_atoms`` atoms use an exact full
    distance-matrix scan. Larger structures switch to an ASE neighbour-list
    cutoff scan so a big crystal does not allocate an N*N matrix; the two paths
    agree on the close pairs that drive the diagnostics.
    """

    symbols = list(atoms.get_chemical_symbols())
    radii = _radii_for_atoms(atoms)
    natoms = len(symbols)
    if not all(math.isfinite(float(value)) for row in atoms.get_positions() for value in row):
        raise ValueError("atom positions must be finite")
    if not all(math.isfinite(value) and value > 0 for value in (bond_cutoff_scale, short_contact_scale)):
        raise ValueError("geometry cutoff scales must be positive and finite")
    if max_items < 0 or max_dense_atoms < 0:
        raise ValueError("geometry limits must be non-negative")
    if natoms <= max_dense_atoms:
        pair_iter: Iterable[tuple[int, int, float]] = _dense_pairs(atoms, natoms)
        pairwise_method = "dense"
    else:
        pair_iter = _neighbor_pairs(atoms, radii, max(bond_cutoff_scale, short_contact_scale))
        pairwise_method = "neighbor_list"

    bonds: list[BondGeometryDiagnostic] = []
    short_contacts: list[ContactDiagnostic] = []
    bonded_pairs: set[tuple[int, int]] = set()

    for left, right, distance in pair_iter:
        radius_sum = radii[left] + radii[right]
        if not math.isfinite(distance) or distance < 0:
            raise ValueError("pair distance must be finite and non-negative")
        if radius_sum <= 0:
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
        if 0 < ratio <= bond_cutoff_scale:
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
        for index, norm in enumerate(_force_norms(forces, natoms)):
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
        "pairwise_method": pairwise_method,
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
