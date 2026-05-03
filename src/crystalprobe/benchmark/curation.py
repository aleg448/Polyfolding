"""Curation readiness reports for benchmark manifests."""

from __future__ import annotations

from dataclasses import dataclass

from crystalprobe.benchmark.dataset import BenchmarkDataset
from crystalprobe.benchmark.schema import CurationStatus, PolymorphPair


@dataclass(frozen=True)
class PairCurationIssue:
    pair_id: str
    severity: str
    field: str
    message: str


def curation_issues(pair: PolymorphPair) -> list[PairCurationIssue]:
    """Return issues that block promotion from draft to reviewed/verified."""

    issues: list[PairCurationIssue] = []
    serialized = pair.model_dump_json().upper()
    if "TODO" in serialized:
        issues.append(PairCurationIssue(pair.pair_id, "blocker", "record", "record contains TODO placeholders"))
    if pair.evidence.stability_ordering == "ambiguous":
        issues.append(PairCurationIssue(pair.pair_id, "blocker", "evidence.stability_ordering", "stability ordering is ambiguous"))
    if not pair.evidence.citation_doi and not pair.evidence.citation_url:
        issues.append(PairCurationIssue(pair.pair_id, "blocker", "evidence.citation", "missing DOI or URL citation"))
    if pair.has_disorder is None:
        issues.append(PairCurationIssue(pair.pair_id, "blocker", "has_disorder", "missing explicit disorder annotation"))
    for side, structure in (("A", pair.structure_a), ("B", pair.structure_b)):
        if structure.license == "unknown":
            issues.append(PairCurationIssue(pair.pair_id, "blocker", f"structure_{side}.license", "structure license is unknown"))
        if structure.source_id.upper() == "TODO":
            issues.append(PairCurationIssue(pair.pair_id, "blocker", f"structure_{side}.source_id", "source identifier is missing"))
    return issues


def readiness_report(dataset: BenchmarkDataset) -> dict[str, object]:
    """Summarize curation readiness for a dataset."""

    all_issues = [issue for pair in dataset for issue in curation_issues(pair)]
    verified = sum(pair.curation_status == CurationStatus.VERIFIED for pair in dataset)
    reviewed = sum(pair.curation_status == CurationStatus.REVIEWED for pair in dataset)
    draft = sum(pair.curation_status == CurationStatus.DRAFT for pair in dataset)
    return {
        "pairs": len(dataset),
        "verified": verified,
        "reviewed": reviewed,
        "draft": draft,
        "blocking_issues": len([issue for issue in all_issues if issue.severity == "blocker"]),
        "issues": [issue.__dict__ for issue in all_issues],
    }

