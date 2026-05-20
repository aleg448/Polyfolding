"""Calibration and abstention helpers for claim-gated predictions."""

from __future__ import annotations

from math import ceil
from random import Random
from statistics import fmean
from typing import Iterable


def bootstrap_mean_interval(
    values: Iterable[float],
    *,
    confidence: float = 0.95,
    rounds: int = 1000,
    seed: int = 0,
) -> dict[str, float | int]:
    """Return a deterministic bootstrap interval for the sample mean."""

    samples = [float(value) for value in values]
    if not samples:
        raise ValueError("values are required")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")
    if rounds <= 0:
        raise ValueError("rounds must be positive")
    rng = Random(seed)
    means = []
    for _ in range(rounds):
        draw = [samples[rng.randrange(len(samples))] for _ in samples]
        means.append(fmean(draw))
    means.sort()
    alpha = 1.0 - confidence
    lower_index = max(0, int((alpha / 2) * rounds))
    upper_index = min(rounds - 1, int((1 - alpha / 2) * rounds))
    return {
        "sample_count": len(samples),
        "rounds": rounds,
        "confidence": confidence,
        "mean": fmean(samples),
        "lower": means[lower_index],
        "upper": means[upper_index],
    }


def conformal_abs_error_threshold(errors: Iterable[float], *, coverage: float = 0.9) -> dict[str, float | int | str]:
    """Return a split-conformal absolute-error threshold."""

    absolute_errors = sorted(abs(float(error)) for error in errors)
    if not absolute_errors:
        raise ValueError("errors are required")
    if not 0 < coverage < 1:
        raise ValueError("coverage must be between 0 and 1")
    rank = ceil((len(absolute_errors) + 1) * coverage)
    if rank > len(absolute_errors):
        threshold = absolute_errors[-1]
        status = "finite_sample_max_threshold"
    else:
        threshold = absolute_errors[rank - 1]
        status = "conformal_threshold_recorded"
    return {
        "status": status,
        "sample_count": len(absolute_errors),
        "coverage": coverage,
        "rank": min(rank, len(absolute_errors)),
        "threshold": threshold,
    }


def calibrated_abstention_decision(
    *,
    predicted_gap: float,
    combined_uncertainty: float,
    conformal_threshold: float,
    evidence_status: str,
) -> dict[str, object]:
    """Decide whether a ranking can be used or must abstain under claim gates.

    `predicted_gap` is interpreted as energy_b - energy_a. Positive values mean
    A is lower predicted energy; negative values mean B is lower predicted energy.
    """

    if combined_uncertainty < 0 or conformal_threshold < 0:
        raise ValueError("uncertainty values must be non-negative")
    direction = "tie"
    if predicted_gap > 0:
        direction = "A"
    elif predicted_gap < 0:
        direction = "B"
    safety_margin = abs(predicted_gap) - combined_uncertainty - conformal_threshold
    normalized_status = evidence_status.casefold()
    if normalized_status != "verified":
        decision = "abstain_needs_verified_evidence"
        reason = "record is not verified, so prediction cannot support a headline claim"
    elif direction == "tie" or safety_margin <= 0:
        decision = "abstain_uncertain_ranking"
        reason = "predicted gap does not clear combined uncertainty plus conformal threshold"
    else:
        decision = "claim_direction_allowed"
        reason = "verified evidence and calibrated margin clear the abstention gate"
    return {
        "schema_version": "0.1.0",
        "decision": decision,
        "predicted_winner": direction,
        "predicted_gap": predicted_gap,
        "combined_uncertainty": combined_uncertainty,
        "conformal_threshold": conformal_threshold,
        "safety_margin": safety_margin,
        "evidence_status": evidence_status,
        "reason": reason,
    }
