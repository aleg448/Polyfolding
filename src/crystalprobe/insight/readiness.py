"""Readiness checks for research-pilot artifact bundles."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from crystalprobe.insight.claims import manuscript_guardrail_checks


@dataclass(frozen=True)
class ReadinessCheck:
    """One paper-readiness check."""

    name: str
    status: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def ampetp_readiness_report(
    *,
    bundle_manifest: dict[str, Any],
    case_study: dict[str, Any],
    sensitivity_summary: dict[str, Any],
    manuscript_text: str | None = None,
) -> dict[str, Any]:
    """Assess whether the AMPETP pilot has the expected reproducibility artifacts."""

    artifact_roles = {artifact["role"] for artifact in bundle_manifest.get("artifacts", [])}
    checks = [
        _check(
            "source_provenance",
            "extracted_cif" in artifact_roles,
            "Extracted AMPETP CIF is present in the research bundle.",
            "Missing extracted AMPETP CIF artifact.",
        ),
        _check(
            "two_backend_reference_measurements",
            _backend_count(case_study) >= 2,
            "Case-study report includes at least two backend reference predictions.",
            "Case-study report needs at least two backend reference predictions.",
        ),
        _check(
            "local_diagnostics_present",
            all(int(row.get("bond_count") or 0) > 0 for row in case_study.get("backend_predictions", [])),
            "All reference backend predictions include bond-level local diagnostics.",
            "One or more reference backend predictions lacks bond-level diagnostics.",
        ),
        _check(
            "sensitivity_predictions_present",
            {"mace_sensitivity_predictions", "aimnet2_sensitivity_predictions"} <= artifact_roles,
            "MACE and AIMNet2 sensitivity prediction artifacts are present.",
            "Missing MACE or AIMNet2 sensitivity prediction artifact.",
        ),
        _check(
            "sensitivity_summary_complete",
            set(sensitivity_summary.get("backends", {})) >= {"mace", "aimnet2"},
            "Sensitivity summary includes MACE and AIMNet2.",
            "Sensitivity summary does not include both MACE and AIMNet2.",
        ),
        _check(
            "figures_present",
            {
                "figure_provenance",
                "figure_structure_projection",
                "figure_backend_diagnostics",
                "figure_sensitivity_deltas",
                "figure_claim_guardrails",
            }
            <= artifact_roles,
            "All expected AMPETP SVG figure artifacts are present.",
            "One or more expected AMPETP SVG figure artifacts is missing.",
        ),
        _check(
            "manifest_hash_present",
            bool(bundle_manifest.get("manifest_sha256")),
            "Research-bundle manifest has a stable SHA-256 digest.",
            "Research-bundle manifest is missing its digest.",
        ),
        _check(
            "guardrails_recorded",
            bool(case_study.get("agreement", {}).get("notes")) and bool(sensitivity_summary.get("interpretation")),
            "Case-study and sensitivity guardrails are recorded.",
            "Missing case-study or sensitivity interpretation guardrails.",
        ),
    ]
    if manuscript_text is not None:
        checks.extend(
            ReadinessCheck(
                name=f"manuscript_{check.name}",
                status=check.status,
                detail=check.detail,
            )
            for check in manuscript_guardrail_checks(manuscript_text)
        )
    passed = sum(check.status == "pass" for check in checks)
    failed = sum(check.status == "fail" for check in checks)
    return {
        "schema_version": "0.1.0",
        "target": "AMPETP CCDC 1102740",
        "status": "paper_pilot_ready" if failed == 0 else "blocked",
        "passed": passed,
        "failed": failed,
        "checks": [check.as_dict() for check in checks],
        "remaining_blockers": _remaining_blockers(failed),
    }


def readiness_markdown(report: dict[str, Any]) -> str:
    """Render a readiness report as Markdown."""

    lines = [
        f"# {report['target']} Readiness Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Passed: `{report['passed']}`",
        f"- Failed: `{report['failed']}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for check in report["checks"]:
        lines.append(f"| {check['name']} | {check['status']} | {check['detail']} |")
    lines.extend(["", "## Remaining Blockers", ""])
    if report["remaining_blockers"]:
        lines.extend(f"- {blocker}" for blocker in report["remaining_blockers"])
    else:
        lines.append("- None for the AMPETP pilot artifact bundle. Broader roadmap blockers remain separate.")
    return "\n".join(lines).rstrip() + "\n"


def _check(name: str, condition: bool, pass_detail: str, fail_detail: str) -> ReadinessCheck:
    return ReadinessCheck(name=name, status="pass" if condition else "fail", detail=pass_detail if condition else fail_detail)


def _backend_count(case_study: dict[str, Any]) -> int:
    return len({row.get("backend") for row in case_study.get("backend_predictions", [])})


def _remaining_blockers(failed: int) -> list[str]:
    if failed:
        return ["Resolve failed readiness checks before treating AMPETP as a paper pilot artifact bundle."]
    return []
