"""Uncertainty-aware MLIP wrapper primitives."""

from crystalprobe.uncertainty.base import EnergyForcePrediction, ModelAdapter, StructureInput
from crystalprobe.uncertainty.calibrated_abstention import (
    bootstrap_mean_interval,
    calibrated_abstention_decision,
    conformal_abs_error_threshold,
)
from crystalprobe.uncertainty.demo import DeterministicHashModel
from crystalprobe.uncertainty.ensemble import EnsembleMLIPWrapper
from crystalprobe.uncertainty.proxy import disagreement_uncertainty_proxy, uncertainty_proxy_markdown

__all__ = [
    "DeterministicHashModel",
    "EnergyForcePrediction",
    "EnsembleMLIPWrapper",
    "ModelAdapter",
    "StructureInput",
    "bootstrap_mean_interval",
    "calibrated_abstention_decision",
    "conformal_abs_error_threshold",
    "disagreement_uncertainty_proxy",
    "uncertainty_proxy_markdown",
]
