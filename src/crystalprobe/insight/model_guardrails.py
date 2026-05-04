"""Model-scope validation guardrails for FAIR Chemistry assets."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ModelGuardrail:
    repo_id: str
    status: str
    allowed_uses: tuple[str, ...]
    blocked_uses: tuple[str, ...]
    required_validation: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_uses"] = list(self.allowed_uses)
        data["blocked_uses"] = list(self.blocked_uses)
        data["required_validation"] = list(self.required_validation)
        return data


def fairchem_model_guardrail(repo_id: str) -> ModelGuardrail:
    """Return conservative CrystalProbe guardrails for a FAIR Chemistry model repo."""

    normalized = repo_id.casefold()
    if normalized == "facebook/omat24":
        return ModelGuardrail(
            repo_id=repo_id,
            status="access_verified_validation_blocked",
            allowed_uses=("repository inventory", "license review", "inorganic smoke-test design"),
            blocked_uses=(
                "organic molecular crystal ranking",
                "Materials Project correction mixing",
                "formation energy or energy-above-hull claims",
                "CrystalProbe therapeutic contrast claims",
            ),
            required_validation=(
                "define an OMat24-specific inorganic calculation target",
                "use OMat24-compatible reference energies and corrections only",
                "record pseudopotential and magnetic-state caveats",
                "keep OMat24 separate from organic CPOSS/CCDC claims",
            ),
        )
    if normalized == "facebook/omol25":
        return ModelGuardrail(
            repo_id=repo_id,
            status="access_verified_validation_blocked",
            allowed_uses=("repository inventory", "molecular smoke-test design", "future isolated molecule or MD validation"),
            blocked_uses=(
                "periodic organic crystal ranking without a validated adapter",
                "CPOSS polymorph benchmark claims",
                "AMPETP/ibuprofen crystal-packing claims",
            ),
            required_validation=(
                "define an OMol25-specific molecule or molecular-dynamics task",
                "verify checkpoint task semantics and reference conventions",
                "compare against a small molecule-level fixture before crystal use",
                "document why a non-periodic or MD model output is applicable before using it in CrystalProbe reports",
            ),
        )
    if normalized in {"facebook/uma", "facebook/omc25"}:
        return ModelGuardrail(
            repo_id=repo_id,
            status="locally_smoke_verified",
            allowed_uses=("guardrailed OMC/organic-crystal inference", "backend-behaviour diagnostics"),
            blocked_uses=("experimental stability claims", "cross-backend thermodynamic calibration"),
            required_validation=(
                "keep outputs within backend-specific interpretation boundaries",
                "record checkpoint alias and task name",
                "review release boundary before sharing CCDC-derived artifacts",
            ),
        )
    return ModelGuardrail(
        repo_id=repo_id,
        status="unknown_model_requires_review",
        allowed_uses=("repository inventory",),
        blocked_uses=("scientific claims",),
        required_validation=("create an explicit model-scope guardrail before use",),
    )


def fairchem_guardrail_report(repo_ids: list[str]) -> dict[str, Any]:
    guardrails = [fairchem_model_guardrail(repo_id).as_dict() for repo_id in repo_ids]
    return {
        "schema_version": "0.1.0",
        "status": "model_guardrails_recorded",
        "models": guardrails,
        "interpretation": [
            "Accepted repository access is not sufficient for scientific use.",
            "OMAT24 and OMol25 remain blocked for CrystalProbe claims until task-specific validation is added.",
            "UMA/OMC25 outputs remain guardrailed behavioural evidence, not experimental stability labels.",
        ],
    }


def fairchem_guardrail_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# FAIR Chemistry Model Guardrails",
        "",
        f"- Status: `{report['status']}`",
        "",
        "| Model | Status | Allowed Uses | Blocked Uses | Required Validation |",
        "|---|---|---|---|---|",
    ]
    for model in report["models"]:
        lines.append(
            f"| `{model['repo_id']}` | `{model['status']}` | "
            f"{'; '.join(model['allowed_uses'])} | "
            f"{'; '.join(model['blocked_uses'])} | "
            f"{'; '.join(model['required_validation'])} |"
        )
    lines.extend(["", "## Guardrails", ""])
    lines.extend(f"- {note}" for note in report["interpretation"])
    return "\n".join(lines).rstrip() + "\n"
