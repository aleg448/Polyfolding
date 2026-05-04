"""Claim-boundary checks for manuscript-facing CrystalProbe text."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable


@dataclass(frozen=True)
class ClaimGuardrail:
    """One manuscript claim-boundary requirement."""

    name: str
    status: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def manuscript_guardrail_checks(text: str) -> list[ClaimGuardrail]:
    """Check that AMPETP pilot manuscripts state the main claim boundaries."""

    normalized = _normalize(text)
    checks = [
        _contains_all(
            normalized,
            name="ampetp_single_structure_scope",
            terms=["ampetp", "single crystal structure", "polymorph ranking"],
            pass_detail="Manuscript states that AMPETP is a single-structure pilot, not a polymorph-ranking result.",
            fail_detail="Manuscript must state that AMPETP is a single-structure pilot, not a polymorph-ranking result.",
        ),
        _contains_all(
            normalized,
            name="not_lisdexamfetamine_proxy",
            terms=["ampetp", "not lisdexamfetamine"],
            pass_detail="Manuscript states that AMPETP is not lisdexamfetamine dimesylate.",
            fail_detail="Manuscript must state that AMPETP is not lisdexamfetamine dimesylate.",
        ),
        _contains_all(
            normalized,
            name="perturbations_are_generated_probes",
            terms=["generated perturbation", "probes", "not experimentally observed"],
            pass_detail="Manuscript states that generated perturbations are sensitivity probes, not observed forms.",
            fail_detail="Manuscript must state that generated perturbations are probes, not observed crystal forms.",
        ),
        _contains_all(
            normalized,
            name="cross_backend_energy_guardrail",
            terms=["cross-backend", "not calibrated thermodynamic"],
            pass_detail="Manuscript states that cross-backend energy differences are not calibrated thermodynamic uncertainty.",
            fail_detail="Manuscript must bound cross-backend energy differences as non-calibrated thermodynamic uncertainty.",
        ),
        _contains_all(
            normalized,
            name="cposs_bridge_guardrail",
            terms=["cposs bridge", "experimental stability"],
            pass_detail="Manuscript states that CPOSS bridge results still need curated experimental stability evidence.",
            fail_detail="Manuscript must state that CPOSS bridge results still need curated experimental stability evidence.",
        ),
        _contains_all(
            normalized,
            name="agi_assisted_validation_guardrail",
            terms=["agi-assisted", "not human-validated"],
            pass_detail="Manuscript states that the current pilot evidence is AGI-assisted and not human-validated.",
            fail_detail="Manuscript must state when pilot evidence is AGI-assisted and not human-validated.",
        ),
    ]
    return checks


def claim_guardrail_summary(checks: Iterable[ClaimGuardrail]) -> dict[str, int | str]:
    """Summarize manuscript claim-boundary checks."""

    materialized = list(checks)
    failed = sum(check.status == "fail" for check in materialized)
    passed = sum(check.status == "pass" for check in materialized)
    return {
        "status": "pass" if failed == 0 else "fail",
        "passed": passed,
        "failed": failed,
    }


def _contains_all(
    text: str,
    *,
    name: str,
    terms: list[str],
    pass_detail: str,
    fail_detail: str,
) -> ClaimGuardrail:
    missing = [term for term in terms if term not in text]
    if missing:
        return ClaimGuardrail(name=name, status="fail", detail=f"{fail_detail} Missing: {', '.join(missing)}.")
    return ClaimGuardrail(name=name, status="pass", detail=pass_detail)


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())
