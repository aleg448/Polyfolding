"""Historical research opportunity matrix for CrystalProbe modules."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class HistoricalOpportunity:
    opportunity_id: str
    historical_thread: str
    older_source: str
    old_blocker: str
    modern_enabler: str
    implementation_target: str
    publication_value: int
    implementation_readiness: int
    claim_risk: int
    claim_gate: str

    def score(self) -> int:
        """Rank work that is publishable, feasible, and claim-safe."""

        return (2 * self.publication_value) + (2 * self.implementation_readiness) + (6 - self.claim_risk)

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["priority_score"] = self.score()
        return data


def historical_opportunity_report(matrix: dict[str, Any]) -> dict[str, Any]:
    """Normalize and rank the historical opportunity matrix."""

    opportunities = [_opportunity(row) for row in matrix.get("opportunities", [])]
    ranked = sorted(opportunities, key=lambda row: (-row.score(), row.opportunity_id))
    return {
        "schema_version": "0.1.0",
        "status": "historical_opportunities_ranked",
        "opportunity_count": len(ranked),
        "top_targets": [row.implementation_target for row in ranked[:5]],
        "opportunities": [row.as_dict() for row in ranked],
        "policy": list(matrix.get("policy", []))
        or [
            "Historical methods are implementation opportunities, not validation evidence.",
            "Only verified CrystalProbe records can support headline benchmark claims.",
        ],
    }


def historical_opportunity_markdown(report: dict[str, Any]) -> str:
    """Render the historical opportunity report as Markdown."""

    lines = [
        "# CrystalProbe Historical Opportunity Matrix",
        "",
        f"- Status: `{report['status']}`",
        f"- Opportunities: `{report['opportunity_count']}`",
        "",
        "## Top Targets",
        "",
    ]
    lines.extend(f"- `{target}`" for target in report["top_targets"])
    lines.extend(
        [
            "",
            "## Ranked Opportunities",
            "",
            "| Score | Target | Historical Thread | Modern Enabler | Claim Gate |",
            "|---:|---|---|---|---|",
        ]
    )
    for row in report["opportunities"]:
        lines.append(
            f"| {row['priority_score']} | `{row['implementation_target']}` | "
            f"{row['historical_thread']} | {row['modern_enabler']} | `{row['claim_gate']}` |"
        )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def implementation_targets(report: dict[str, Any], *, limit: int | None = None) -> list[str]:
    """Return ranked implementation target names."""

    targets = [str(row["implementation_target"]) for row in report.get("opportunities", [])]
    return targets if limit is None else targets[:limit]


def _opportunity(row: dict[str, Any]) -> HistoricalOpportunity:
    return HistoricalOpportunity(
        opportunity_id=str(row["opportunity_id"]),
        historical_thread=str(row["historical_thread"]),
        older_source=str(row["older_source"]),
        old_blocker=str(row["old_blocker"]),
        modern_enabler=str(row["modern_enabler"]),
        implementation_target=str(row["implementation_target"]),
        publication_value=_bounded_score(row.get("publication_value"), "publication_value"),
        implementation_readiness=_bounded_score(row.get("implementation_readiness"), "implementation_readiness"),
        claim_risk=_bounded_score(row.get("claim_risk"), "claim_risk"),
        claim_gate=str(row["claim_gate"]),
    )


def _bounded_score(value: Any, field: str) -> int:
    score = int(value)
    if not 1 <= score <= 5:
        raise ValueError(f"{field} must be between 1 and 5")
    return score


def top_dependency_light_targets(opportunities: Iterable[dict[str, Any]]) -> list[str]:
    """Return targets that are both ready and lower claim-risk."""

    selected = [
        _opportunity(row)
        for row in opportunities
        if int(row.get("implementation_readiness", 0)) >= 4 and int(row.get("claim_risk", 6)) <= 3
    ]
    return [row.implementation_target for row in sorted(selected, key=lambda row: (-row.score(), row.opportunity_id))]
