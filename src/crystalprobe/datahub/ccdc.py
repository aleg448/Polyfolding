"""Utilities for locally downloaded CCDC/CSD CIF exports."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from crystalprobe.core.io import atomic_write_text


DATA_RE = re.compile(r"^data_(?P<block_id>\S+)")
TAG_RE = re.compile(r"^(?P<tag>_[A-Za-z0-9_.-]+)\s+(?P<value>.+?)\s*$")

SPACE_GROUP_REPLACEMENTS = {
    "P2(1)": "P 21",
    "P2(1)/c": "P 21/c",
    "P21/c": "P 21/c",
    "P21/a": "P 21/a",
    "P 1 21 1": "P 21",
}


@dataclass(frozen=True)
class CcdcCifBlock:
    """One data block from a CCDC multi-CIF export."""

    block_id: str
    source_file: str
    source_index: int
    tags: dict[str, str]
    text: str

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("text")
        return data


def _clean_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_tags(text: str) -> dict[str, str]:
    tags: dict[str, str] = {}
    in_text_field = False
    for line in text.splitlines():
        # Skip CIF multi-line text fields (delimited by lines starting with ';')
        # so their free-text contents are not misread as single-line tag values.
        if line.startswith(";"):
            in_text_field = not in_text_field
            continue
        if in_text_field:
            continue
        match = TAG_RE.match(line.strip())
        if match:
            tags[match.group("tag")] = _clean_value(match.group("value"))
    return tags


def split_ccdc_cif(path: str | Path) -> list[CcdcCifBlock]:
    """Split a CCDC/CSD CIF export into individual data blocks."""

    source = Path(path)
    blocks: list[CcdcCifBlock] = []
    current: list[str] | None = None
    current_id: str | None = None
    in_text_field = False

    for line in source.read_text(encoding="utf-8", errors="replace").splitlines(True):
        if line.startswith(";"):
            in_text_field = not in_text_field
        match = None if in_text_field else DATA_RE.match(line.strip())
        if match:
            if current is not None and current_id is not None:
                text = "".join(current)
                blocks.append(
                    CcdcCifBlock(
                        block_id=current_id,
                        source_file=source.name,
                        source_index=len(blocks),
                        tags=_parse_tags(text),
                        text=text,
                    )
                )
            current_id = match.group("block_id")
            current = [line]
        elif current is not None:
            current.append(line)

    if current is not None and current_id is not None:
        text = "".join(current)
        blocks.append(
            CcdcCifBlock(
                block_id=current_id,
                source_file=source.name,
                source_index=len(blocks),
                tags=_parse_tags(text),
                text=text,
            )
        )
    return blocks


def find_ccdc_block(blocks: list[CcdcCifBlock], *, block_id: str | None = None, index: int | None = None) -> CcdcCifBlock:
    """Select one block by id or index."""

    if block_id is not None:
        for block in blocks:
            if block.block_id == block_id:
                return block
        raise ValueError(f"block_id not found: {block_id}")
    if index is not None:
        return blocks[index]
    raise ValueError("block_id or index is required")


def sanitize_cif_text(text: str) -> str:
    """Normalize common CSD space-group spellings that ASE cannot parse.

    The replacements are equivalence-preserving spelling normalizations (for
    example ``P 1 21 1`` and ``P 21`` denote the same space group), not
    symmetry changes. Use :func:`cif_spacegroup_replacements` to record which
    normalizations were applied for provenance.
    """

    return _normalize_spacegroup_lines(text)[0]


def cif_spacegroup_replacements(text: str) -> list[dict[str, str]]:
    """List the space-group spelling normalizations :func:`sanitize_cif_text` applies.

    Returns one ``{"from": old, "to": new}`` entry per replacement that actually
    matches a space-group tag line, so callers can log the normalization in a
    provenance record instead of silently rewriting the input.
    """

    return _normalize_spacegroup_lines(text)[1]


def _normalize_spacegroup_lines(text: str) -> tuple[str, list[dict[str, str]]]:
    pattern = re.compile(
        r"^([ \t]*_(?:symmetry_space_group_name_H-M|space_group_name_H-M_alt)[ \t]+)(.+?)[ \t]*$"
    )
    lines = []
    changes: list[dict[str, str]] = []
    in_text_field = False
    for line in text.splitlines(keepends=True):
        if line.startswith(";"):
            in_text_field = not in_text_field
        body = line.rstrip("\r\n")
        match = None if in_text_field else pattern.match(body)
        if match:
            old = _clean_value(match.group(2))
            if old in SPACE_GROUP_REPLACEMENTS:
                new = SPACE_GROUP_REPLACEMENTS[old]
                line = f"{match.group(1)}'{new}'{line[len(body):]}"
                change = {"from": old, "to": new}
                if change not in changes:
                    changes.append(change)
        lines.append(line)
    return "".join(lines), changes


def write_ccdc_block(
    source: str | Path,
    output: str | Path,
    *,
    block_id: str | None = None,
    index: int | None = None,
    sanitize: bool = True,
) -> CcdcCifBlock:
    """Extract one CCDC block to a standalone CIF file."""

    blocks = split_ccdc_cif(source)
    block = find_ccdc_block(blocks, block_id=block_id, index=index)
    text = sanitize_cif_text(block.text) if sanitize else block.text
    atomic_write_text(output, text)
    return block


def summarize_ccdc_blocks(blocks: list[CcdcCifBlock]) -> dict[str, Any]:
    """Summarize CCDC blocks for source provenance."""

    formulas: dict[str, int] = {}
    names: dict[str, int] = {}
    for block in blocks:
        formula = block.tags.get("_chemical_formula_sum") or block.tags.get("_chemical_formula_moiety") or "unknown"
        name = block.tags.get("_chemical_name_common") or block.tags.get("_chemical_name_systematic") or "unknown"
        formulas[formula] = formulas.get(formula, 0) + 1
        names[name] = names.get(name, 0) + 1
    return {
        "blocks": len(blocks),
        "formulas": dict(sorted(formulas.items())),
        "names": dict(sorted(names.items())),
    }
