"""CPOSS209 source indexing utilities."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from crystalprobe.foundry.adapters import AdapterNotAvailable, check_adapter_availability


BLOCK_RE = re.compile(r"^data_(?P<block_id>[^\s]+)")
FORM_RE = re.compile(r"^(?P<family>[A-Za-z]+)(?P<form_number>\d+)(?:_(?P<suffix>.+))?$")

CELL_TAGS = {
    "_cell_length_a": "a",
    "_cell_length_b": "b",
    "_cell_length_c": "c",
    "_cell_angle_alpha": "alpha",
    "_cell_angle_beta": "beta",
    "_cell_angle_gamma": "gamma",
    "_cell_volume": "volume",
}


@dataclass(frozen=True)
class CpossStructureRecord:
    """One structure block discovered inside a CPOSS209 CIF file."""

    block_id: str
    family_code: str
    form_number: int | None
    suffix: str | None
    source_file: str
    source_index: int
    formula: str | None
    natoms: int | None
    space_group: str | None
    cell_setting: str | None
    cell: dict[str, float]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CpossPairCandidate:
    """A within-family CPOSS pair candidate awaiting stability curation."""

    pair_id: str
    family_code: str
    structure_a: str
    structure_b: str
    source_file: str
    source_index_a: int
    source_index_b: int
    form_number_a: int | None
    form_number_b: int | None
    curation_status: str = "candidate"
    stability_status: str = "uncurated"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_cposs_block_id(block_id: str) -> tuple[str, int | None, str | None]:
    """Return molecule family, form number, and suffix from a CPOSS block id."""

    match = FORM_RE.match(block_id)
    if not match:
        return block_id, None, None
    form_text = match.group("form_number")
    return match.group("family"), int(form_text), match.group("suffix")


def iter_cif_block_ids(path: Path) -> list[str]:
    """List CIF data block identifiers without requiring ASE."""

    block_ids: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = BLOCK_RE.match(line.strip())
        if match:
            block_ids.append(match.group("block_id"))
    return block_ids


def _clean_cif_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_float(value: str) -> float:
    cleaned = _clean_cif_value(value).split("(", 1)[0]
    return float(cleaned)


def _block_tag_maps(path: Path) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if BLOCK_RE.match(line):
            current = {}
            blocks.append(current)
            continue
        if current is None or not line.startswith("_"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            current[parts[0]] = _clean_cif_value(parts[1])
    return blocks


def _atoms_metadata(path: Path) -> list[tuple[str, int]]:
    availability = check_adapter_availability("ase_cif")
    if not availability.available:
        raise AdapterNotAvailable(availability.blocker or "ASE is required for CPOSS atom metadata")

    from ase.io import read

    atoms_list = read(str(path), index=":")
    return [(atoms.get_chemical_formula(), len(atoms)) for atoms in atoms_list]


def index_cposs_cif(path: str | Path, *, with_atoms: bool = True) -> list[CpossStructureRecord]:
    """Index one CPOSS209 CIF file."""

    cif_path = Path(path)
    block_ids = iter_cif_block_ids(cif_path)
    tag_maps = _block_tag_maps(cif_path)
    atom_rows: list[tuple[str | None, int | None]]
    if with_atoms:
        atom_rows = list(_atoms_metadata(cif_path))
    else:
        atom_rows = [(None, None) for _ in block_ids]

    if not (len(block_ids) == len(tag_maps) == len(atom_rows)):
        raise ValueError(
            f"CPOSS CIF block mismatch for {cif_path}: "
            f"blocks={len(block_ids)} tags={len(tag_maps)} atoms={len(atom_rows)}"
        )

    records: list[CpossStructureRecord] = []
    for index, (block_id, tags, atom_row) in enumerate(zip(block_ids, tag_maps, atom_rows, strict=True)):
        family, form_number, suffix = parse_cposs_block_id(block_id)
        cell = {
            name: _parse_float(tags[tag])
            for tag, name in CELL_TAGS.items()
            if tag in tags
        }
        records.append(
            CpossStructureRecord(
                block_id=block_id,
                family_code=family,
                form_number=form_number,
                suffix=suffix,
                source_file=cif_path.name,
                source_index=index,
                formula=atom_row[0],
                natoms=atom_row[1],
                space_group=tags.get("_symmetry_space_group_name_H-M") or tags.get("_space_group_name_H-M_alt"),
                cell_setting=tags.get("_symmetry_cell_setting"),
                cell=cell,
            )
        )
    return records


def index_cposs_directory(source_dir: str | Path, *, with_atoms: bool = True) -> list[CpossStructureRecord]:
    """Index every CIF in a CPOSS209 extracted supplemental directory."""

    root = Path(source_dir)
    records: list[CpossStructureRecord] = []
    for path in sorted(root.glob("*.cif")):
        records.extend(index_cposs_cif(path, with_atoms=with_atoms))
    return records


def summarize_cposs_records(records: Iterable[CpossStructureRecord]) -> dict[str, Any]:
    """Summarize indexed CPOSS records for curation planning."""

    rows = list(records)
    family_counts: dict[str, int] = {}
    file_counts: dict[str, int] = {}
    for row in rows:
        family_counts[row.family_code] = family_counts.get(row.family_code, 0) + 1
        file_counts[row.source_file] = file_counts.get(row.source_file, 0) + 1
    return {
        "records": len(rows),
        "families": len(family_counts),
        "family_counts": dict(sorted(family_counts.items())),
        "source_files": dict(sorted(file_counts.items())),
    }


def generate_cposs_pair_candidates(
    records: Iterable[CpossStructureRecord],
    *,
    mode: str = "adjacent",
) -> list[CpossPairCandidate]:
    """Generate within-family pair candidates from indexed CPOSS structures.

    `adjacent` pairs neighboring form numbers and matches the Month 1 queue size
    in the roadmap. `all` emits every within-family combination.
    """

    if mode not in {"adjacent", "all"}:
        raise ValueError("mode must be 'adjacent' or 'all'")

    grouped: dict[tuple[str, str], list[CpossStructureRecord]] = {}
    for record in records:
        grouped.setdefault((record.source_file, record.family_code), []).append(record)

    candidates: list[CpossPairCandidate] = []
    for (source_file, family_code), rows in sorted(grouped.items()):
        ordered = sorted(rows, key=lambda row: (row.form_number is None, row.form_number or 0, row.block_id))
        if mode == "adjacent":
            pairs = zip(ordered, ordered[1:], strict=False)
        else:
            pairs = (
                (ordered[left], ordered[right])
                for left in range(len(ordered))
                for right in range(left + 1, len(ordered))
            )
        for left, right in pairs:
            pair_id = f"cposs209_{family_code.lower()}_{left.block_id.lower()}_vs_{right.block_id.lower()}"
            candidates.append(
                CpossPairCandidate(
                    pair_id=pair_id,
                    family_code=family_code,
                    structure_a=left.block_id,
                    structure_b=right.block_id,
                    source_file=source_file,
                    source_index_a=left.source_index,
                    source_index_b=right.source_index,
                    form_number_a=left.form_number,
                    form_number_b=right.form_number,
                )
            )
    return candidates


def summarize_cposs_pair_candidates(candidates: Iterable[CpossPairCandidate]) -> dict[str, Any]:
    """Summarize generated pair candidates."""

    rows = list(candidates)
    family_counts: dict[str, int] = {}
    file_counts: dict[str, int] = {}
    for row in rows:
        family_counts[row.family_code] = family_counts.get(row.family_code, 0) + 1
        file_counts[row.source_file] = file_counts.get(row.source_file, 0) + 1
    return {
        "candidate_pairs": len(rows),
        "families": len(family_counts),
        "family_counts": dict(sorted(family_counts.items())),
        "source_files": dict(sorted(file_counts.items())),
    }
