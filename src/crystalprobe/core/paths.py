"""Path helpers for cross-platform generated manifests."""

from __future__ import annotations

from pathlib import Path


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
