# Behavioural Fingerprint Paper Outline

## Working Title

Behavioural fingerprints of foundation ML interatomic potentials for organic polymorph ranking

## Core Claim

The paper should not claim state-of-the-art prediction. It should show where current MLIPs are reliable, where they fail, and how future models can be benchmarked against the same behavioural surface.

## Current Preliminary Memo

The current collaborator-facing memo is generated at `outputs/crystalprobe_preliminary_findings_memo.md`. It should be the seed for the first ChemRxiv-style preliminary findings draft.

The current ChemRxiv-style draft scaffold is generated at `outputs/crystalprobe_chemrxiv_preprint_draft.md`.

## Figure List

0. AMPETP pilot vertical slice: CCDC source export, extracted block, MACE/AIMNet backend outputs, local force and bond diagnostics, perturbation sensitivity grid.
1. CPOSS bridge mini-benchmark: IBP and CBZ formula-unit-normalized MACE rankings and diagnostic flag rates.
2. Benchmark composition: molecules, functional groups, hydrogen-bond motifs, Z prime, disorder flags.
3. Overall pairwise ranking accuracy by model.
4. Ranking accuracy stratified by chemistry class.
5. Signed energy-gap error distributions.
6. Conformational sensitivity under small perturbations.
7. OOD score versus ranking failure.
8. Calibration curves for uncertainty estimates.
9. Failure-mode catalog with representative structures.

## Methods Skeleton

- AMPETP pilot case-study protocol for validating source ingestion and local diagnostics before pairwise benchmarking.
- Deterministic perturbation protocol for coordinate-noise and cell-scaling sensitivity probes.
- CPOSS bridge mini-benchmark protocol for formula-unit-normalized local structure rankings before curated experimental stability labels.
- Benchmark construction and curation criteria.
- MLIP model versions and inference settings.
- Pairwise energy ranking protocol.
- Chemistry slicing and multiple-comparison control.
- Uncertainty and OOD methods.
- Reproducibility package and manifest hashes.
