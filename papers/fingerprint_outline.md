# Behavioural Fingerprint Paper Outline

## Working Title

Behavioural fingerprints of foundation ML interatomic potentials for organic polymorph ranking

## Core Claim

The paper should not claim state-of-the-art prediction. It should show where current MLIPs are reliable, where they fail, and how future models can be benchmarked against the same behavioural surface.

## Figure List

1. Benchmark composition: molecules, functional groups, hydrogen-bond motifs, Z prime, disorder flags.
2. Overall pairwise ranking accuracy by model.
3. Ranking accuracy stratified by chemistry class.
4. Signed energy-gap error distributions.
5. Conformational sensitivity under small perturbations.
6. OOD score versus ranking failure.
7. Calibration curves for uncertainty estimates.
8. Failure-mode catalog with representative structures.

## Methods Skeleton

- Benchmark construction and curation criteria.
- MLIP model versions and inference settings.
- Pairwise energy ranking protocol.
- Chemistry slicing and multiple-comparison control.
- Uncertainty and OOD methods.
- Reproducibility package and manifest hashes.

