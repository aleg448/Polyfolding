"""Structure-scope helpers shared by MLIP adapters.

These functions make the *scope* of an energy explicit so downstream code can
refuse to compare or average energies computed under incompatible assumptions
(for example a non-periodic cluster energy versus a periodic crystal energy, or
a neutral molecule versus a charged ion). They operate on ASE-like ``Atoms``
objects but only use light-weight duck-typed access so they can be unit-tested
with tiny fakes and without importing ASE.
"""

from __future__ import annotations

from math import isfinite
from typing import Any


def structure_is_periodic(structure: Any) -> bool:
    """Return True when the structure declares periodicity on any axis.

    Accepts a scalar ``pbc`` (bool) or a per-axis iterable, matching ASE's
    ``Atoms.pbc``. Structures without a ``pbc`` attribute are treated as
    non-periodic (isolated molecule/cluster).
    """

    pbc = getattr(structure, "pbc", None)
    if pbc is None:
        return False
    try:
        return any(bool(axis) for axis in pbc)
    except TypeError:
        return bool(pbc)


def structure_total_charge(structure: Any, *, default: float = 0.0) -> float:
    """Return the net total charge for a structure.

    Resolution order:
    1. ``structure.info["charge"]`` when present (explicit override).
    2. The sum of explicitly annotated ASE per-atom initial charges.
    3. ``default``.
    """

    info = getattr(structure, "info", None)
    if isinstance(info, dict) and "charge" in info:
        return _finite_charge(info["charge"])

    has_array = getattr(structure, "has", None)
    if callable(has_array) and not has_array("initial_charges"):
        return _finite_charge(default)

    getter = getattr(structure, "get_initial_charges", None)
    if callable(getter):
        try:
            charges = getter()
        except Exception as exc:
            raise ValueError("cannot read declared charge annotations") from exc
        return _finite_charge(sum(_finite_charge(value) for value in charges))

    return _finite_charge(default)


def _finite_charge(value: Any) -> float:
    charge = float(value)
    if not isfinite(charge):
        raise ValueError("total charge must be finite")
    return charge


def describe_structure_scope(structure: Any, *, default_charge: float = 0.0) -> dict[str, Any]:
    """Summarize the comparison-relevant scope of a structure."""

    periodic = structure_is_periodic(structure)
    return {
        "periodic": periodic,
        "total_charge": structure_total_charge(structure, default=default_charge),
        "boundary": "periodic" if periodic else "cluster",
    }
