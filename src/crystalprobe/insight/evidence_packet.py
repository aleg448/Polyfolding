"""Evidence packets that turn research-cycle signals into promotion work."""

from __future__ import annotations

from math import sqrt
from typing import Any

from crystalprobe.benchmark.curation import curation_issues
from crystalprobe.benchmark.predictions import PairEnergyPredictionRecord
from crystalprobe.benchmark.schema import PolymorphPair
from crystalprobe.insight.active_evidence_triage import active_evidence_triage_report, triage_items_from_pairs
from crystalprobe.insight.motif_prior import motif_prior_for_pair
from crystalprobe.uncertainty.calibrated_abstention import calibrated_abstention_decision


def evidence_packet_report(
    pair: PolymorphPair,
    *,
    prediction: PairEnergyPredictionRecord | None = None,
    triage_item: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a single-pair evidence packet for curation and publication review."""

    issues = curation_issues(pair)
    triage = triage_item or active_evidence_triage_report(triage_items_from_pairs([pair]))["items"][0]
    prediction_section = _prediction_section(pair, prediction)
    blocker_fields = sorted({issue.field for issue in issues})
    status = "evidence_packet_review_ready" if not issues else "evidence_packet_blocked"
    return {
        "schema_version": "0.1.0",
        "status": status,
        "pair_id": pair.pair_id,
        "molecule": pair.molecule.common_name or pair.molecule.smiles,
        "curation_status": pair.curation_status.value,
        "headline_claim_gate": "allowed_verified_record" if pair.curation_status.value == "verified" else "blocked_until_verified",
        "stability_ordering": pair.evidence.stability_ordering,
        "experimental_winner": pair.experimental_winner,
        "structures": {
            "A": _structure_summary(pair.structure_a),
            "B": _structure_summary(pair.structure_b),
        },
        "evidence": {
            "citation_doi": pair.evidence.citation_doi,
            "citation_url": pair.evidence.citation_url,
            "temperature_K": pair.evidence.temperature_K,
            "free_energy_diff_kJ_per_mol": pair.evidence.free_energy_diff_kJ_per_mol,
            "notes": pair.evidence.notes,
        },
        "motif_prior": motif_prior_for_pair(pair),
        "active_triage": triage,
        "prediction_and_abstention": prediction_section,
        "promotion_gate": {
            "current_status": pair.curation_status.value,
            "target_next_status": "reviewed" if pair.curation_status.value == "draft" else "verified",
            "blocker_count": len(issues),
            "blocker_fields": blocker_fields,
            "blockers": [issue.__dict__ for issue in issues],
            "can_promote_without_edits": len(issues) == 0,
        },
        "next_research_actions": _next_actions(pair, triage, issues, prediction_section),
        "policy": [
            "An evidence packet is a promotion worklist, not a scientific result.",
            "Draft and candidate records remain unverified even when motif, triage, and prediction sections are populated.",
            "Headline ranking claims require verified stability evidence and passing release-boundary review.",
        ],
    }


def evidence_packet_markdown(report: dict[str, Any]) -> str:
    """Render an evidence packet as Markdown."""

    prediction = report["prediction_and_abstention"]
    gate = report["promotion_gate"]
    motif = report["motif_prior"]
    triage = report["active_triage"]
    lines = [
        f"# CrystalProbe Evidence Packet: {report['pair_id']}",
        "",
        f"- Status: `{report['status']}`",
        f"- Molecule: {report['molecule']}",
        f"- Curation status: `{report['curation_status']}`",
        f"- Stability ordering: `{report['stability_ordering']}`",
        f"- Headline claim gate: `{report['headline_claim_gate']}`",
        "",
        "## Structures",
        "",
        "| Side | Structure ID | Label | Source | Source ID | License |",
        "|---|---|---|---|---|---|",
    ]
    for side, structure in report["structures"].items():
        lines.append(
            f"| {side} | `{structure['structure_id']}` | {structure['label']} | "
            f"`{structure['source']}` | `{structure['source_id']}` | `{structure['license']}` |"
        )
    lines.extend(
        [
            "",
            "## Motif Prior",
            "",
            f"- Classification: `{motif['network_classification']}`",
            f"- Donor prior count: `{motif['donor_prior_count']}`",
            f"- Acceptor prior count: `{motif['acceptor_prior_count']}`",
            f"- Signals: {', '.join(motif['motif_signals']) or 'none'}",
            f"- Boundary: {motif['claim_boundary']}",
            "",
            "## Active Evidence Triage",
            "",
            f"- Priority: `{triage['priority_score']}`",
            f"- Recommended action: `{triage['recommended_action']}`",
            f"- Rationale: {triage['rationale']}",
            "",
            "## Prediction And Abstention",
            "",
            f"- Prediction status: `{prediction['status']}`",
            f"- Model: `{prediction.get('model_name', 'not_recorded')}`",
            f"- Predicted winner: `{prediction.get('predicted_winner', 'not_recorded')}`",
            f"- Abstention decision: `{prediction['abstention']['decision']}`",
            f"- Abstention reason: {prediction['abstention']['reason']}",
            "",
            "## Promotion Gate",
            "",
            f"- Target next status: `{gate['target_next_status']}`",
            f"- Blockers: `{gate['blocker_count']}`",
            "",
            "| Field | Message |",
            "|---|---|",
        ]
    )
    if gate["blockers"]:
        for issue in gate["blockers"]:
            lines.append(f"| `{issue['field']}` | {issue['message']} |")
    else:
        lines.append("| `none` | No curation blockers recorded. |")
    lines.extend(["", "## Next Research Actions", ""])
    lines.extend(f"- {action}" for action in report["next_research_actions"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def select_pair_for_packet(pairs: list[PolymorphPair], pair_id: str | None = None) -> PolymorphPair:
    """Select a requested pair or the highest-priority active-triage pair."""

    if pair_id:
        for pair in pairs:
            if pair.pair_id == pair_id:
                return pair
        raise ValueError(f"pair_id not found: {pair_id}")
    triage = active_evidence_triage_report(triage_items_from_pairs(pairs))
    selected_id = triage["next_batch"][0]["item_id"]
    return select_pair_for_packet(pairs, str(selected_id))


def _prediction_section(
    pair: PolymorphPair,
    prediction: PairEnergyPredictionRecord | None,
) -> dict[str, Any]:
    if prediction is None:
        return {
            "status": "prediction_not_available",
            "abstention": {
                "decision": "abstain_no_prediction",
                "reason": "no prediction record was supplied for this pair",
            },
            "claim_boundary": "no model-output claim is possible without a prediction record",
        }
    predicted_gap = prediction.energy_b - prediction.energy_a
    uncertainty_a = prediction.energy_uncertainty_a or 0.0
    uncertainty_b = prediction.energy_uncertainty_b or 0.0
    combined_uncertainty = sqrt((uncertainty_a**2) + (uncertainty_b**2))
    abstention = calibrated_abstention_decision(
        predicted_gap=predicted_gap,
        combined_uncertainty=combined_uncertainty,
        conformal_threshold=0.0,
        evidence_status=pair.curation_status.value,
    )
    return {
        "status": "prediction_recorded",
        "pair_id": prediction.pair_id,
        "model_name": prediction.model_name,
        "model_version": prediction.model_version,
        "energy_unit": prediction.energy_unit,
        "energy_a": prediction.energy_a,
        "energy_b": prediction.energy_b,
        "predicted_gap_energy_b_minus_a": predicted_gap,
        "predicted_winner": abstention["predicted_winner"],
        "combined_uncertainty": combined_uncertainty,
        "ood_flag_a": prediction.ood_flag_a,
        "ood_flag_b": prediction.ood_flag_b,
        "calibration_status": "not_calibrated_no_verified_records",
        "abstention": abstention,
        "claim_boundary": "prediction is a demo signal until the record is verified and calibration evidence exists",
    }


def _structure_summary(structure: Any) -> dict[str, Any]:
    return {
        "structure_id": structure.structure_id,
        "label": structure.label,
        "source": structure.source.value,
        "source_id": structure.source_id,
        "license": str(structure.license),
        "cif_path": structure.cif_path,
        "space_group": structure.space_group,
    }


def _next_actions(
    pair: PolymorphPair,
    triage: dict[str, Any],
    issues: list[Any],
    prediction_section: dict[str, Any],
) -> list[str]:
    actions = [str(triage["rationale"]).rstrip(".") + "."]
    fields = {issue.field for issue in issues}
    if "evidence.stability_ordering" in fields:
        actions.append("Find and cite primary experimental evidence for relative stability, or keep the record ambiguous.")
    if "evidence.citation" in fields:
        actions.append("Add a DOI or URL citation for the stability evidence before promotion.")
    if "record" in fields:
        actions.append("Remove TODO placeholders from InChI, source IDs, CIF paths, disorder notes, and evidence notes.")
    if "has_disorder" in fields:
        actions.append("Record an explicit disorder annotation, even if the value is false.")
    if any(field.endswith(".license") for field in fields):
        actions.append("Resolve source licenses for both structures and keep restricted coordinates out of public artifacts.")
    if prediction_section["status"] == "prediction_not_available":
        actions.append("Attach a prediction record if a model-output abstention decision is needed.")
    elif pair.curation_status.value != "verified":
        actions.append("Keep the prediction abstained until the evidence status reaches verified.")
    return actions
