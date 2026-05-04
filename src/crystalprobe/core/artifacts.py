"""Artifact manifest helpers for reproducible research bundles."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from crystalprobe.core.ledger import file_sha256, object_sha256


@dataclass(frozen=True)
class ArtifactRecord:
    """One file included in a research bundle."""

    path: str
    role: str
    sha256: str
    bytes: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def artifact_record(path: str | Path, *, role: str) -> ArtifactRecord:
    """Create a hashed artifact record for one existing file."""

    artifact_path = Path(path)
    return ArtifactRecord(
        path=str(artifact_path),
        role=role,
        sha256=file_sha256(artifact_path),
        bytes=artifact_path.stat().st_size,
    )


def build_artifact_manifest(
    *,
    title: str,
    artifacts: list[ArtifactRecord],
    rebuild_commands: list[str],
    notes: list[str] | None = None,
) -> dict[str, Any]:
    """Build a stable JSON-serializable research artifact manifest."""

    manifest = {
        "schema_version": "0.1.0",
        "title": title,
        "artifacts": [artifact.as_dict() for artifact in artifacts],
        "rebuild_commands": rebuild_commands,
        "notes": notes or [],
    }
    manifest["manifest_sha256"] = object_sha256(manifest)
    return manifest


def write_artifact_manifest(path: str | Path, manifest: dict[str, Any]) -> None:
    """Write a manifest as sorted, indented JSON."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8", newline="\n")


def artifact_manifest_markdown(manifest: dict[str, Any]) -> str:
    """Render an artifact manifest as Markdown."""

    lines = [
        f"# {manifest['title']}",
        "",
        f"- Manifest SHA-256: `{manifest['manifest_sha256']}`",
        f"- Artifact count: `{len(manifest['artifacts'])}`",
        "",
        "## Artifacts",
        "",
        "| Role | Path | Bytes | SHA-256 |",
        "|---|---|---:|---|",
    ]
    for artifact in manifest["artifacts"]:
        lines.append(
            f"| {artifact['role']} | `{artifact['path']}` | {artifact['bytes']} | `{artifact['sha256']}` |"
        )
    lines.extend(["", "## Rebuild Commands", ""])
    lines.extend(f"```powershell\n{command}\n```" for command in manifest["rebuild_commands"])
    if manifest.get("notes"):
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in manifest["notes"])
    return "\n".join(lines).rstrip() + "\n"
