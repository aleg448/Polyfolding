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
- CCDC multi-CIF block inspection and extraction.
- Single-structure case-study reports for backend agreement diagnostics.
- Deterministic perturbation-set generation for sensitivity studies.
- Deterministic SVG figure generation for provenance, structure projection, diagnostics, sensitivity, and claim guardrails.
- Hashed research-bundle manifests for reproducible artifact trails.
- Automated pilot-readiness reports for artifact completeness and paper guardrails.
- Local CPOSS mini-benchmark reports that bridge single-structure pilots to polymorph-ranking workflows.
- CPOSS pair-candidate reports that convert local bridge summaries into reviewable adjacent-pair curation queues.
- CPOSS candidate triage reports that prioritize evidence-review work while preserving benchmark guardrails.
- CPOSS evidence workpacks with curator-fillable fields for stability evidence, source-license decisions, disorder annotations, and promotion review.
- Preliminary findings memo generation from local readiness, sensitivity, bundle, and bridge reports.
- ChemRxiv-style draft scaffolding from local CrystalProbe reports.
- Project status dashboards that summarize readiness, verification state, and remaining blockers.
- Generic CCDC sensitivity-set generation for applying the same perturbation protocol to additional crystal targets.
- Sensitivity contrast reports across therapeutic crystal targets.
- Roadmap status reports that map local artifacts to benchmark, fingerprint, uncertainty, FastCSP, and software-paper deliverables.
- Documented report workflows with manifest-backed tests for local rebuild order.
- Conservative release-boundary reports that separate candidate public artifacts from CCDC-derived review-required and local-only coordinate artifacts.

## References To Add

- MACE-OFF paper and model card.
- AIMNet2 paper.
- UMA or fairchem model documentation.
- CPOSS209 dataset paper.
- FastCSP/fairchem paper.
