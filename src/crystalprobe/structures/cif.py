"""CIF loading utilities with optional ASE support."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from crystalprobe.foundry.adapters import AdapterNotAvailable, check_adapter_availability


def read_cif_structure(path: str | Path, *, index: int | str = 0, block_id: str | None = None) -> Any:
    """Read a CIF structure by coordinate index or explicit data-block identity.

    ASE coordinate indices exclude metadata-only blocks. Source block ordinals
    must never be passed as coordinate indices; use block_id for indexed records.
    """

    availability = check_adapter_availability("ase_cif")
    if not availability.available:
        raise AdapterNotAvailable(availability.blocker or "ASE is required for CIF parsing")

    from ase.io import read

    if block_id is not None:
        from ase.io.cif import parse_cif

        blocks = [block for block in parse_cif(str(path)) if block.name.casefold() == block_id.casefold()]
        if len(blocks) != 1:
            raise ValueError(f"expected exactly one CIF block {block_id!r}; found {len(blocks)}")
        if not blocks[0].has_structure():
            raise ValueError(f"CIF block {block_id!r} has no atomic coordinates")
        return blocks[0].get_atoms()
    return read(str(path), index=index)
