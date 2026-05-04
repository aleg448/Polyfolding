"""Release-boundary reports for CrystalProbe research artifacts."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class ReleaseRecord:
    """One artifact classified by release boundary."""

    path: str
    category: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def release_boundary_report(
    *,
    artifact_paths: Iterable[str],
    workflow_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify local artifacts by conservative publication boundary."""

    paths = {_normalize_path(path) for path in artifact_paths}
    if workflow_manifest:
        for workflow in workflow_manifest.get("workflows", []):
            paths.update(_normalize_path(path) for path in workflow.get("primary_outputs", []))
    records = [_classify(path) for path in sorted(paths)]
    counts = Counter(record.category for record in records)
    return {
        "schema_version": "0.1.0",
        "status": "release_boundary_recorded",
        "counts": dict(sorted(counts.items())),
        "records": [record.as_dict() for record in records],
        "policy": [
            "candidate_public artifacts are source, documentation, tests, and manuscript scaffolds that do not embed gated coordinates.",
            "license_review_required artifacts are CCDC-derived reports, figures, manifests, or model measurements that need human license review before sharing.",
            "local_only artifacts include raw, extracted, or generated coordinate files from gated CCDC/CSD sources.",
        ],
    }


def release_boundary_markdown(report: dict[str, Any]) -> str:
    """Render a release-boundary report as Markdown."""

    lines = [
        "# CrystalProbe Release Boundary Report",
        "",
        f"- Status: `{report['status']}`",
        "",
        "## Counts",
        "",
    ]
    for category, count in sorted(report["counts"].items()):
        lines.append(f"- `{category}`: `{count}`")
    lines.extend(
        [
            "",
            "## Policy",
            "",
        ]
    )
    lines.extend(f"- {line}" for line in report["policy"])
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "| Category | Path | Reason |",
            "|---|---|---|",
        ]
    )
    for record in report["records"]:
        lines.append(f"| `{record['category']}` | `{record['path']}` | {record['reason']} |")
    return "\n".join(lines).rstrip() + "\n"


def _classify(path: str) -> ReleaseRecord:
    normalized = _normalize_path(path)
    suffix = Path(normalized).suffix.lower()
    name = Path(normalized).name.lower()
    if _is_local_only_coordinate(normalized, suffix):
        return ReleaseRecord(
            path=path,
            category="local_only",
            reason="Coordinate-bearing gated CCDC/CSD source or extracted/generated CIF; keep local unless the license explicitly permits redistribution.",
        )
    if normalized.startswith(("src/", "scripts/", "tests/", "docs/", "data/curation/")) or normalized in {
        "README.md",
        "BLOCKERS.md",
    }:
        return ReleaseRecord(
            path=path,
            category="candidate_public",
            reason="Repository source, documentation, test, or curation metadata path intended for publication review.",
        )
    if normalized.startswith("papers/"):
        return ReleaseRecord(
            path=path,
            category="candidate_public",
            reason="Manuscript scaffold with claim guardrails and no raw CCDC coordinate file.",
        )
    if normalized.startswith("outputs/"):
        if name.endswith((".svg", ".md")):
            return ReleaseRecord(
                path=path,
                category="license_review_required",
                reason="Generated CCDC-derived report or figure; review source-license implications before public sharing.",
            )
        return ReleaseRecord(
                path=path,
            category="license_review_required",
            reason="Generated CCDC-derived machine-readable artifact; review source-license implications before public sharing.",
        )
    return ReleaseRecord(
        path=path,
        category="review_required",
        reason="Unrecognized artifact path; classify manually before sharing.",
    )


def _is_local_only_coordinate(path: str, suffix: str) -> bool:
    if path.startswith("data/sources/ccdc/"):
        return True
    if suffix == ".cif" and path.startswith("outputs/"):
        return True
    if "/ampetp_sensitivity/" in path and suffix == ".cif":
        return True
    if "/ibuprofen_sensitivity/" in path and suffix == ".cif":
        return True
    return False


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/")
