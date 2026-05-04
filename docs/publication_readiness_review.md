# CrystalProbe Publication Readiness Review

Date: 2026-05-04

This review covers the generated release-boundary report and CPOSS evidence workpack after the AMPETP research reporting suite commit.

## Current Decision

CrystalProbe is ready for a code-and-methods commit, but not yet ready for public release of CCDC-derived scientific artifacts or headline polymorph benchmark claims.

The AMPETP pilot is internally paper-pilot ready. The CPOSS bridge is a curated-work queue, not a verified benchmark.

## Evidence Reviewed

- `outputs/crystalprobe_release_boundary.md`
- `outputs/crystalprobe_release_boundary.json`
- `outputs/cposs_pair_candidate_report.md`
- `outputs/cposs_pair_triage_report.md`
- `outputs/cposs_evidence_workpack.md`
- `outputs/cposs_evidence_workpack.json`
- `outputs/ampetp_readiness_report.md`
- `outputs/crystalprobe_project_status.md`
- `outputs/crystalprobe_roadmap_status.md`

## Release Boundary Findings

- Candidate-public artifacts: `10`.
- License-review-required artifacts: `27`.
- Local-only artifacts: `1`.
- The local-only artifact is the extracted CCDC coordinate CIF. This must not be published unless the applicable CCDC/CSD license explicitly permits redistribution.
- Generated CCDC-derived reports, figures, manifests, and model outputs are correctly classified as `license_review_required`.
- The release-boundary report is conservative enough for internal publication planning, but it is not itself a legal review.

## CPOSS Workpack Findings

- CPOSS evidence work items: `14`.
- Triage priorities: `2` high, `4` medium, `8` low.
- The two high-priority evidence targets are:
  - `ibp_ibp01_psicrys_vs_ibp06_psicrys`
  - `cbz_cbz01_psicrys_vs_cbz03_psicrys`
- Every work item still has blank evidence fields for stability ordering, citation DOI/URL, license decisions, disorder annotations, curator, and reviewer.
- Every candidate remains a local model-relative-energy candidate. None should be promoted to benchmark records until evidence fields are completed and reviewed.

## Go / No-Go

| Area | Decision | Reason |
|---|---|---|
| Source code commit | Go | Tests pass and generated outputs are rebuildable from scripts. |
| AMPETP internal pilot paper draft | Go with guardrails | Readiness checks pass, but CCDC-derived artifacts still need license review before public sharing. |
| Public release of raw or extracted CCDC CIFs | No-go | Coordinate-bearing CCDC/CSD files are local-only unless redistribution is explicitly allowed. |
| Public release of generated CCDC-derived reports | Hold | Release-boundary report marks them license-review-required. |
| CPOSS benchmark claims | No-go | Candidate pairs lack experimental stability evidence and disorder annotations. |
| CPOSS evidence curation | Go | Workpacks are ready for human literature and license review. |
| UMA/OMat24 thermodynamic claims | No-go until configured and bounded | README now records the OMat24/Materials Project energy-reference incompatibility warning. |

## Required Before Public Publication

1. Complete human license review for every CCDC-derived artifact planned for sharing.
2. Keep raw CCDC files and extracted coordinate CIFs out of Git and public archives.
3. Fill CPOSS evidence workpack fields for the selected high-priority pairs.
4. Attach primary stability citations with DOI or durable URLs.
5. Record disorder annotations for both structures in each promoted pair.
6. Re-run the release-boundary report after any artifact list changes.
7. Re-run local tests and Docker verification before tagging or pushing a release.

## Immediate Recommended Order

1. Commit the current code/docs/test suite.
2. Review `outputs/crystalprobe_release_boundary.md` manually for the intended publication package.
3. Fill the two high-priority CPOSS evidence forms first.
4. Convert only evidence-complete CPOSS candidates into draft benchmark records.
5. Re-run readiness, roadmap, release-boundary, and test checks.
