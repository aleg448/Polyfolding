"""Audit candidate crystal landscapes without claiming to generate them."""

from __future__ import annotations

from collections import defaultdict
from statistics import fmean
from typing import Any, Iterable


def landscape_audit_report(candidates: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Audit candidate structures for diversity, duplicates, and backend disagreement."""

    rows = [_normalize_candidate(row) for row in candidates]
    families = sorted({row["family_id"] for row in rows})
    family_reports = [_family_report(family, [row for row in rows if row["family_id"] == family]) for family in families]
    duplicate_count = sum(len(family["duplicate_groups"]) for family in family_reports)
    disagreement_count = sum(1 for family in family_reports if family["backend_winner_disagreement"])
    status = "landscape_audit_recorded"
    if not rows:
        status = "landscape_audit_empty"
    elif disagreement_count or duplicate_count:
        status = "landscape_audit_review_required"
    return {
        "schema_version": "0.1.0",
        "status": status,
        "candidate_count": len({(row["family_id"], row["candidate_id"]) for row in rows}),
        "backend_observation_count": len(rows),
        "family_count": len(family_reports),
        "duplicate_group_count": duplicate_count,
        "backend_winner_disagreement_count": disagreement_count,
        "families": family_reports,
        "policy": [
            "Landscape audit accepts candidate structures from external generators; it does not create CSP claims by itself.",
            "Duplicate and backend-disagreement findings are inspection signals.",
            "Ranking claims still require source evidence, calibration, and verified records.",
        ],
    }


def landscape_audit_markdown(report: dict[str, Any]) -> str:
    """Render landscape audit as Markdown."""

    lines = [
        "# CrystalProbe Landscape Audit",
        "",
        f"- Status: `{report['status']}`",
        f"- Candidate structures: `{report['candidate_count']}`",
        f"- Backend observations: `{report['backend_observation_count']}`",
        "",
        "| Family | Candidates | Basins | Duplicate Groups | Backend Winners | Review Required |",
        "|---|---:|---:|---:|---|---|",
    ]
    for family in report["families"]:
        winner_text = ", ".join(f"{backend}:{winner}" for backend, winner in family["backend_winners"].items())
        lines.append(
            f"| `{family['family_id']}` | {family['candidate_count']} | {family['basin_count']} | "
            f"{len(family['duplicate_groups'])} | {winner_text or 'none'} | "
            f"`{family['review_required']}` |"
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _family_report(family_id: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_ids = sorted({row["candidate_id"] for row in rows})
    fingerprints: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        fingerprints[row["fingerprint"]].append(row["candidate_id"])
    duplicate_groups = [
        {"fingerprint": fingerprint, "candidate_ids": sorted(set(ids))}
        for fingerprint, ids in sorted(fingerprints.items())
        if len(set(ids)) > 1 and fingerprint != "unknown"
    ]
    backend_winners = _backend_winners(rows)
    unique_winners = {winner for winner in backend_winners.values() if winner is not None}
    spans = _energy_spans(rows)
    disagreement = len(unique_winners) > 1
    return {
        "family_id": family_id,
        "candidate_count": len(candidate_ids),
        "basin_count": len({row["fingerprint"] for row in rows if row["fingerprint"] != "unknown"}),
        "duplicate_groups": duplicate_groups,
        "backend_winners": backend_winners,
        "backend_winner_disagreement": disagreement,
        "energy_spans_by_backend": spans,
        "mean_energy_by_backend": _mean_energies(rows),
        "review_required": bool(duplicate_groups or disagreement),
    }


def _backend_winners(rows: list[dict[str, Any]]) -> dict[str, str | None]:
    by_backend: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["energy"] is not None:
            by_backend[row["backend"]].append(row)
    winners: dict[str, str | None] = {}
    for backend, backend_rows in sorted(by_backend.items()):
        if not backend_rows:
            winners[backend] = None
            continue
        winners[backend] = min(backend_rows, key=lambda row: (float(row["energy"]), row["candidate_id"]))["candidate_id"]
    return winners


def _energy_spans(rows: list[dict[str, Any]]) -> dict[str, float]:
    spans: dict[str, float] = {}
    by_backend: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row["energy"] is not None:
            by_backend[row["backend"]].append(float(row["energy"]))
    for backend, energies in sorted(by_backend.items()):
        spans[backend] = max(energies) - min(energies) if energies else 0.0
    return spans


def _mean_energies(rows: list[dict[str, Any]]) -> dict[str, float]:
    by_backend: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row["energy"] is not None:
            by_backend[row["backend"]].append(float(row["energy"]))
    return {backend: fmean(values) for backend, values in sorted(by_backend.items()) if values}


def _normalize_candidate(row: dict[str, Any]) -> dict[str, Any]:
    fingerprint = row.get("fingerprint", "unknown")
    if isinstance(fingerprint, (list, tuple)):
        fingerprint = "|".join(str(item) for item in fingerprint)
    return {
        "family_id": str(row.get("family_id") or row.get("molecule") or "unknown"),
        "candidate_id": str(row.get("candidate_id") or row.get("structure_id") or "unknown"),
        "backend": str(row.get("backend") or "unknown"),
        "energy": None if row.get("energy") is None else float(row["energy"]),
        "fingerprint": str(fingerprint),
        "source": str(row.get("source") or "unknown"),
    }
