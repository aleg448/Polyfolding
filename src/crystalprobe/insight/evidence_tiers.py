"""Evidence-tier policy for AGI-assisted CrystalProbe curation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class EvidenceTier:
    """Claim boundary for one target or candidate record."""

    tier: str
    status: str
    allowed_uses: tuple[str, ...]
    blocked_claims: tuple[str, ...]
    required_next_steps: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_uses"] = list(self.allowed_uses)
        data["blocked_claims"] = list(self.blocked_claims)
        data["required_next_steps"] = list(self.required_next_steps)
        return data


def classify_evidence_tier(record: dict[str, Any]) -> EvidenceTier:
    """Classify a CrystalProbe target under conservative evidence rules.

    The classifier deliberately allows AGI-assisted work to continue when human
    validation is absent, but downgrades the permitted claim boundary.
    """

    has_coordinates = bool(record.get("has_atom_coordinates"))
    backend_count = int(record.get("backend_count") or 0)
    has_sensitivity = bool(record.get("has_sensitivity_grid"))
    has_contrast = bool(record.get("has_therapeutic_contrast"))
    has_provenance = bool(record.get("has_source_provenance"))
    license_clean = bool(record.get("license_clean_for_redistribution"))
    human_validated = bool(record.get("human_database_validation"))
    stability_evidence = bool(record.get("experimental_stability_evidence"))

    if not has_coordinates:
        return EvidenceTier(
            tier="blocked_no_coordinates",
            status="blocked",
            allowed_uses=("literature search planning", "negative evidence logging"),
            blocked_claims=(
                "MLIP measurement",
                "crystal-packing inference",
                "polymorph ranking",
                "therapeutic-crystal benchmark inclusion",
            ),
            required_next_steps=("obtain license-compatible atom coordinates or choose a proxy target",),
        )

    if license_clean and human_validated and stability_evidence and backend_count >= 2:
        return EvidenceTier(
            tier="verified_benchmark_candidate",
            status="promotable",
            allowed_uses=(
                "benchmark candidate",
                "paper table with stability caveats",
                "model comparison after normalization checks",
            ),
            blocked_claims=("clinical or therapeutic efficacy inference",),
            required_next_steps=("run release-boundary review before publication",),
        )

    if backend_count >= 2 and has_sensitivity and has_contrast and has_provenance:
        return EvidenceTier(
            tier="agi_assisted_guardrailed_pilot",
            status="usable_with_guardrails",
            allowed_uses=(
                "methods pilot",
                "backend-behavior comparison",
                "local geometry and force diagnostic case study",
                "therapeutic contrast without stability-ranking claims",
            ),
            blocked_claims=(
                "verified polymorph benchmark",
                "experimental stability ranking",
                "redistribution of gated coordinate files",
                "claiming database identity beyond recorded source metadata",
            ),
            required_next_steps=(
                "keep raw or extracted gated coordinates local",
                "label reports as AGI-assisted and not human-validated",
                "preserve release-boundary review before sharing generated artifacts",
            ),
        )

    return EvidenceTier(
        tier="exploratory_local_measurement",
        status="incomplete",
        allowed_uses=("local debugging", "backend smoke testing", "curation triage"),
        blocked_claims=(
            "publication-ready pilot",
            "verified benchmark",
            "experimental stability ranking",
        ),
        required_next_steps=(
            "add source provenance",
            "run at least two independent backends",
            "add deterministic sensitivity or contrast evidence",
        ),
    )


def evidence_tier_report(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Build an evidence-tier report for a list of targets."""

    targets = []
    for record in records:
        tier = classify_evidence_tier(record)
        targets.append(
            {
                "target": record.get("target") or record.get("name") or "unnamed_target",
                "record": record,
                "tier": tier.as_dict(),
            }
        )
    return {
        "schema_version": "0.1.0",
        "status": "evidence_tiers_recorded",
        "targets": targets,
        "policy": [
            "AGI-assisted curation may continue without human validation, but claim boundaries must be explicit.",
            "Missing lisdexamfetamine dimesylate coordinates block crystal MLIP measurements for that target.",
            "Restricted local CCDC/CSD coordinate evidence can support guarded pilots, not redistributable benchmark records.",
            "Verified benchmark promotion requires license-clean coordinates, human/source validation, and experimental stability evidence.",
        ],
    }


def evidence_tier_markdown(report: dict[str, Any]) -> str:
    """Render an evidence-tier report as Markdown."""

    lines = [
        "# CrystalProbe Evidence Tiers",
        "",
        f"- Status: `{report['status']}`",
        "",
        "## Policy",
        "",
    ]
    lines.extend(f"- {item}" for item in report["policy"])
    lines.extend(
        [
            "",
            "## Targets",
            "",
            "| Target | Tier | Status | Allowed Uses | Blocked Claims | Required Next Steps |",
            "|---|---|---|---|---|---|",
        ]
    )
    for target in report["targets"]:
        tier = target["tier"]
        lines.append(
            f"| {target['target']} | `{tier['tier']}` | `{tier['status']}` | "
            f"{'; '.join(tier['allowed_uses'])} | "
            f"{'; '.join(tier['blocked_claims'])} | "
            f"{'; '.join(tier['required_next_steps'])} |"
        )
    return "\n".join(lines).rstrip() + "\n"
