"""Path helpers for cross-platform generated manifests."""

from __future__ import annotations

import re
from pathlib import Path

_UNSAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def safe_filename(name: str, *, fallback: str = "structure") -> str:
    """Return a filesystem-safe single path component.

    Caller-supplied identifiers (for example a ``--structure-id`` argument) are
    interpolated into output paths. Stripping directory components and unusual
    characters prevents a value like ``../../secret`` from escaping the intended
    output directory.
    """

    base = str(name).replace("\\", "/").rsplit("/", 1)[-1]
    cleaned = _UNSAFE_FILENAME_RE.sub("_", base).strip("._")
    if not cleaned or cleaned in {".", ".."}:
        return safe_filename(fallback) if fallback != name else "structure"
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                *(f"LPT{i}" for i in range(1, 10))}
    if cleaned.split(".", 1)[0].upper() in reserved:
        cleaned = "_" + cleaned
    return cleaned


def portable_path(path: str | Path) -> Path:
    """Resolve a path that may have been written with Windows separators."""

    candidate = Path(path)
    if candidate.exists():
        return candidate
    text = str(path)
    if "\\" in text:
        normalized = Path(text.replace("\\", "/"))
        if normalized.exists():
            return normalized
    return candidate
