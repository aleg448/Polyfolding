"""Active evidence triage inspired by active learning and query-by-committee."""

from __future__ import annotations

from typing import Any, Iterable

from crystalprobe.benchmark.curation import curation_issues


def triage_items_from_pairs(pairs: Iterable[Any]) -> list[dict[str, Any]]:
    """Create triage items from PolymorphPair objects."""

    items: list[dict[str, Any]] = []
    for pair in pairs:
        issues = curation_issues(pair)
        structure_licenses = [str(pair.structure_a.license), str(pair.structure_b.license)]
        blockers = [f"{issue.field}: {issue.message}" for issue in issues]
        items.append(
            {
                "item_id": pair.pair_id,
                "molecule": pair.molecule.common_name or pair.molecule.smiles,
                "evidence_status": pair.curation_status.value,
                "stability_ordering": pair.evidence.stability_ordering,
                "license_status": "unknown" if "unknown" in structure_licenses else "recorded",
                "issue_count": len(issues),
                "blockers": blockers,
                "backend_disagreement": False,
                "uncertainty_score": 0.0,
                "publication_value": 3,
            }
        )
    return items


def active_evidence_triage_report(
    items: Iterable[dict[str, Any]],
    *,
    title: str = "CrystalProbe active evidence triage",
    next_batch_size: int = 5,
) -> dict[str, Any]:
    """Rank evidence tasks by expected reduction in claim uncertainty."""

    scored = [_score_item(item) for item in items]
    ordered = sorted(scored, key=lambda row: (-int(row["priority_score"]), str(row["item_id"])))
    return {
        "schema_version": "0.1.0",
        "title": title,
        "status": "active_evidence_triage_recorded",
        "item_count": len(ordered),
        "next_batch": ordered[:next_batch_size],
        "items": ordered,
        "policy": [
            "Triage priority is not a scientific claim.",
            "High priority means the task may reduce claim uncertainty or unblock publication review.",
            "Candidate and draft records must remain visibly unverified until evidence promotion passes.",
        ],
    }


def active_evidence_triage_markdown(report: dict[str, Any]) -> str:
    """Render active evidence triage as Markdown."""

    lines = [
        f"# {report['title']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Items: `{report['item_count']}`",
        "",
        "## Next Batch",
        "",
        "| Rank | Item | Molecule | Status | Priority | Action | Why |",
        "|---:|---|---|---|---:|---|---|",
    ]
    for rank, row in enumerate(report["next_batch"], start=1):
        lines.append(
            f"| {rank} | `{row['item_id']}` | {row['molecule']} | `{row['evidence_status']}` | "
            f"{row['priority_score']} | `{row['recommended_action']}` | {row['rationale']} |"
        )
    lines.extend(
        [
            "",
            "## Full Queue",
            "",
            "| Item | Status | Ordering | License | Issues | Priority |",
            "|---|---|---|---|---:|---:|",
        ]
    )
    for row in report["items"]:
        lines.append(
            f"| `{row['item_id']}` | `{row['evidence_status']}` | `{row['stability_ordering']}` | "
            f"`{row['license_status']}` | {row['issue_count']} | {row['priority_score']} |"
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _score_item(item: dict[str, Any]) -> dict[str, Any]:
    status = str(item.get("evidence_status") or "candidate").casefold()
    ordering = str(item.get("stability_ordering") or "ambiguous").casefold()
    license_status = str(item.get("license_status") or "unknown").casefold()
    issue_count = int(item.get("issue_count") or len(item.get("blockers", [])))
    uncertainty_score = max(0.0, min(1.0, float(item.get("uncertainty_score") or 0.0)))
    publication_value = max(1, min(5, int(item.get("publication_value") or 3)))

    base = 20 + (publication_value * 8)
    if status in {"draft", "candidate", "candidate_unverified"}:
        base += 20
    elif status == "reviewed":
        base += 12
    elif status == "verified":
        base -= 12

    if ordering == "ambiguous":
        base += 16
    if license_status in {"unknown", "license_review_required", "local_only"}:
        base += 12
    if bool(item.get("backend_disagreement")):
        base += 10
    base += round(uncertainty_score * 12)
    base += min(issue_count * 2, 18)

    action, rationale = _action_and_rationale(status, ordering, license_status, issue_count, item)
    row = dict(item)
    row.update(
        {
            "priority_score": int(base),
            "recommended_action": action,
            "rationale": rationale,
            "claim_boundary": "prioritization only; do not promote without reviewed or verified evidence",
        }
    )
    return row


def _action_and_rationale(
    status: str,
    ordering: str,
    license_status: str,
    issue_count: int,
    item: dict[str, Any],
) -> tuple[str, str]:
    if status == "verified":
        return "maintain_regression_fixture", "verified evidence should be protected as a regression and calibration fixture"
    if ordering == "ambiguous":
        return "resolve_stability_evidence", "ambiguous stability ordering blocks ranking and calibration claims"
    if license_status in {"unknown", "license_review_required", "local_only"}:
        return "resolve_release_boundary", "source licensing or coordinate release status blocks public evidence use"
    if bool(item.get("backend_disagreement")):
        return "inspect_backend_disagreement", "backend disagreement can identify uncertainty and model-scope failure modes"
    if issue_count > 0:
        return "close_curation_blockers", "curation blockers prevent promotion to reviewed or verified status"
    if status == "reviewed":
        return "seek_verification", "reviewed records need independent stability evidence before headline use"
    return "review_for_promotion", "record has no obvious blocker but still needs human promotion review"
