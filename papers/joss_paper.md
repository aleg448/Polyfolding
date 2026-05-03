# JOSS Paper Draft

## Summary

CrystalProbe provides Python tools for constructing, validating, and evaluating polymorph-pair benchmarks with uncertainty-aware MLIP predictions. The package focuses on pairwise stability ranking, calibrated uncertainty, and explicit out-of-distribution flags for research use.

## Statement of Need

Foundation machine-learned interatomic potentials are increasingly used in crystal structure prediction workflows, but downstream users lack small, transparent tools for checking when a prediction should be trusted. CrystalProbe addresses this gap by pairing a strict benchmark schema with uncertainty-wrapper interfaces and reproducible metrics.

## Current Features

- JSON Lines benchmark schema using Pydantic.
- Manifest validation and summary CLI.
- Pairwise ranking metrics.
- Model-agnostic ensemble uncertainty wrapper.
- Calibration helper functions.

## References To Add

- MACE-OFF paper and model card.
- AIMNet2 paper.
- UMA or fairchem model documentation.
- CPOSS209 dataset paper.
- FastCSP/fairchem paper.

