"""Small file-writing helpers for generated research artifacts."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any
from uuid import uuid4


def atomic_write_text(path: str | Path, text: str) -> None:
    """Write text through a same-directory temp file before replacing the target."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(f".{output.name}.{uuid4().hex}.tmp")
    try:
        tmp.write_text(text, encoding="utf-8", newline="\n")
        _replace_with_retry(tmp, output)
    finally:
        if tmp.exists():
            tmp.unlink()


def atomic_write_json(path: str | Path, payload: dict[str, Any] | list[Any]) -> None:
    """Write stable JSON atomically."""

    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True))


def _replace_with_retry(source: Path, target: Path, *, attempts: int = 5, delay_seconds: float = 0.05) -> None:
    for attempt in range(attempts):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay_seconds)
