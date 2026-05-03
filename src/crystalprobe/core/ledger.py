"""Provenance ledger utilities."""

from __future__ import annotations

import hashlib
import json
import platform
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import crystalprobe


def file_sha256(path: str | Path) -> str:
    """Return the SHA-256 digest for one file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_sha256(payload: Any) -> str:
    """Return a stable SHA-256 digest for a JSON-serializable object."""

    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class LedgerEntry:
    """Append-only provenance record for a computation."""

    action: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    parameters: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    software: dict[str, Any] = field(
        default_factory=lambda: {
            "crystalprobe_version": crystalprobe.__version__,
            "python": platform.python_version(),
            "platform": platform.platform(),
        }
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "created_at": self.created_at,
            "action": self.action,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "parameters": self.parameters,
            "metrics": self.metrics,
            "software": self.software,
        }


def record_ledger_entry(entry: LedgerEntry, path: str | Path) -> None:
    """Append an entry to a JSON Lines ledger file."""

    ledger_path = Path(path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry.as_dict(), sort_keys=True, separators=(",", ":")))
        handle.write("\n")

