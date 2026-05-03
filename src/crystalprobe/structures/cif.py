"""CIF loading utilities with optional ASE support."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from crystalprobe.foundry.adapters import AdapterNotAvailable, check_adapter_availability


def read_cif_structure(path: str | Path, *, index: int | str = 0) -> Any:
    """Read a CIF file as an ASE Atoms object when ASE is installed."""

    availability = check_adapter_availability("ase_cif")
    if not availability.available:
        raise AdapterNotAvailable(availability.blocker or "ASE is required for CIF parsing")

    from ase.io import read

    return read(str(path), index=index)

