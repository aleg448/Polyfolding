"""Utilities for locally downloaded CCDC/CSD CIF exports."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DATA_RE = re.compile(r"^data_(?P<block_id>\S+)")
TAG_RE = re.compile(r"^(?P<tag>_[A-Za-z0-9_.-]+)\s+(?P<value>.+?)\s*$")

SPACE_GROUP_REPLACEMENTS = {
    "P2(1)": "P 21",
    "P2(1)/c": "P 21/c",
    "P21/c": "P 21/c",
    "P21/a": "P 21/a",
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
    for line in text.splitlines():
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

    for line in source.read_text(encoding="utf-8", errors="replace").splitlines(True):
        match = DATA_RE.match(line)
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
    """Normalize common CSD space-group spellings that ASE cannot parse."""

    sanitized = text
    for old, new in SPACE_GROUP_REPLACEMENTS.items():
        pattern = rf"(?m)^(_(?:symmetry_space_group_name_H-M|space_group_name_H-M_alt)\s+)'?{re.escape(old)}'?\s*$"
        sanitized = re.sub(pattern, lambda match, value=new: f"{match.group(1)}'{value}'", sanitized)
    return sanitized


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
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8", newline="\n")
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
