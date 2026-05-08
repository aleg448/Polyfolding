# CrystalProbe Release Boundary Review

Date: 2026-05-06

## Decision

The pushed branch is suitable for a draft code-and-methods PR, but the GitHub connector could not open the PR from this session because the integration returned `403 Resource not accessible by integration` and the local GitHub CLI is not installed.

Publication remains blocked for benchmark and CCDC-derived evidence artifacts. The current release boundary is conservative and should remain in force.

## Reviewed Files

- `outputs/crystalprobe_release_boundary.md`
- `outputs/crystalprobe_publication_readiness.md`
- `outputs/cposs_promotion_gate.md`
- `data/curation/cposs_evidence_overrides_v0.1.json`

## Release Boundary Findings

- Candidate-public artifacts: `91`.
- License-review-required artifacts: `50`.
- Local-only artifacts: `1`.
- The local-only artifact is `outputs/ccdc_ampetp_extracted.cif`; it must stay out of Git and public archives unless the CCDC/CSD license explicitly permits redistribution.
- Generated CCDC-derived reports, figures, manifests, and local measurement summaries remain `license_review_required`.
- Execution status reports are candidate-public because they describe environment and blocker state rather than embedding gated coordinates.

## CPOSS Evidence Findings

- The active CPOSS workpack has been expanded from `14` to `25` entries by adding local MACE ACR and FLU family summaries to the CBZ/IBP bridge.
- A curation overlay now fills citation, source-license, disorder, curator, reviewer, and promotion-decision fields for those `25` entries.
- All `25` entries are classified as `literature_mapped_candidate`, not verified benchmark pairs, because block-level mapping to experimentally verified form labels and stability conditions is not yet complete.
- Reaching the first 20-entry curation scale is now complete; reaching the first 20 verified benchmark pairs is still blocked.

## Next Actions

1. Open the draft PR manually at `https://github.com/aleg448/Polyfolding/pull/new/codex-crystalprobe-docs-readiness`, or install/authenticate GitHub CLI and run PR creation from the branch.
2. Lock CPOSS block IDs to experimental form labels before any `promotion_decision: promote`.
3. Promote only evidence-complete, block-mapped records.
4. Keep calibrated uncertainty blocked until promoted verified pairs exist.
