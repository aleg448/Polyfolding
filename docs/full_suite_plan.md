# CrystalProbe Full-Suite Build Plan

This repository implements the CrystalProbe vertical slice as a dependency-light research suite. The full POLARIS architecture remains the long horizon; CrystalProbe focuses on the trust infrastructure needed first.

## Implemented Locally

- Benchmark schema and curation readiness checks.
- Pairwise prediction file format.
- Ranking and behavioural fingerprint metrics.
- Markdown/JSON report generation.
- Quick benchmark runner with provenance ledger output.
- Optional adapter discovery for ASE, MACE-OFF, AIMNet2, UMA, and FastCSP.
- CCDC multi-CIF block extraction and AMPETP/ibuprofen proof measurements.
- Single-structure case-study report generation for AMPETP backend agreement.
- Deterministic AMPETP perturbation-set generation for coordinate-noise and cell-scaling sensitivity probes.
- AGI-assisted evidence-tier policy for work that lacks human database validation or redistributable coordinates.
- Paper outlines for the fingerprint, data descriptor, and JOSS outputs.

## Adapter Strategy

Heavy scientific dependencies are isolated behind `crystalprobe.foundry`. The core package stays installable on a plain Python environment; real MLIP execution is enabled by installing optional backends and configuring model assets.

The next adapter implementations should land in this order:

1. ASE CIF reader, because every MLIP backend needs a structure object.
2. MACE-OFF single-point energy adapter.
3. MACE-OFF pairwise ranking runner.
4. AIMNet2 adapter.
5. Ensemble wrapper over MACE-OFF/AIMNet2.
6. FastCSP quick-mode integration.

## AMPETP Pilot Role

AMPETP, CCDC 1102740, is now the first research-grade pilot target. It is not a polymorph-pair benchmark record, but it proves the vertical slice needed before the full benchmark paper: local CCDC source handling, block extraction, ASE parsing, MACE/AIMNet execution, bond-level diagnostics, backend-agreement reporting, and a paper-ready case-study draft.

UMA access is now accepted and Docker/fairchem initializes `uma-s-1p2`. The AMPETP structure inference workflow can run UMA with `--backend uma`, producing `outputs/ccdc_ampetp_uma.json` as an optional third backend reference measurement.

The AMPETP pilot now also has a generated perturbation grid under `outputs/ampetp_sensitivity/` with a manifest at `outputs/ampetp_sensitivity_manifest.json`. MACE-OFF23 small, AIMNet2, and UMA all run across the six generated probes. The strongest response for all three backends is the `pos_sigma_0p03_seed_1` coordinate-noise probe, which all three backends flag with `short_contact` and `high_force_atom`.

Deterministic AMPETP SVG figures are generated under `outputs/figures/` from the extracted CIF plus case-study and sensitivity JSON outputs. These cover provenance, a 2D structure projection, backend force diagnostics, sensitivity energy deltas, and claim guardrails.

The AMPETP pilot now has a research-bundle manifest at `outputs/ampetp_research_bundle_manifest.json` and a Markdown companion at `outputs/ampetp_research_bundle_manifest.md`. The manifest hashes 15 generated artifacts and records the rebuild command chain from CCDC block extraction through figures.

The AMPETP pilot readiness report is generated at `outputs/ampetp_readiness_report.json` and `outputs/ampetp_readiness_report.md`. Current status is `paper_pilot_ready` with 13 checks passed and 0 failed.

A CPOSS local mini-benchmark bridge report is generated at `outputs/cposs_mini_benchmark_report.json` and `outputs/cposs_mini_benchmark_report.md`. It currently summarizes MACE local measurements for IBP and CBZ across 16 structures, with formula-unit-normalized relative energies and local diagnostic rates.

The CPOSS bridge now also produces an adjacent pair-candidate queue at `outputs/cposs_pair_candidate_report.json` and `outputs/cposs_pair_candidate_report.md`. These records are explicitly marked `needs_experimental_evidence` and are not benchmark records until stability evidence, source-license review, and disorder annotations are attached.

A CPOSS candidate triage report is generated at `outputs/cposs_pair_triage_report.json` and `outputs/cposs_pair_triage_report.md`. It prioritizes small-gap and first-adjacent family candidates for human evidence review without converting them into stability claims.

A curator-fillable CPOSS evidence workpack is generated at `outputs/cposs_evidence_workpack.json` and `outputs/cposs_evidence_workpack.md`. It turns the triage queue into structured forms for stability citations, source-license decisions, disorder annotations, and promotion review.

The current preliminary findings memo is generated at `outputs/crystalprobe_preliminary_findings_memo.md`. It summarizes AMPETP readiness, AMPETP sensitivity, the CPOSS bridge, and the remaining guardrails in a collaborator-facing format.

A ChemRxiv-style preprint draft scaffold is generated at `outputs/crystalprobe_chemrxiv_preprint_draft.md`. It expands the preliminary memo into abstract, introduction, methods, results, discussion, limitations, and reproducibility sections.

The current project status dashboard is generated at `outputs/crystalprobe_project_status.json` and `outputs/crystalprobe_project_status.md`. It summarizes AMPETP readiness, CPOSS bridge scope, latest local verification, and remaining user-input blockers.

The roadmap-level status report is generated at `outputs/crystalprobe_roadmap_status.json` and `outputs/crystalprobe_roadmap_status.md`. It maps the current artifact set against the full CrystalProbe deliverables: benchmark, fingerprint paper, uncertainty wrapper, FastCSP layer, and software paper.

The deterministic CCDC sensitivity generator is now generic via `scripts/build_ccdc_sensitivity_set.py`. It has been applied to ibuprofen CCDC 774097 as a neutral therapeutic contrast. MACE, AIMNet2, and UMA sensitivity summaries now exist locally or through Docker/Linux runs for the AMPETP-vs-ibuprofen pilot contrast.

The AMPETP-vs-ibuprofen MACE contrast report is generated at `outputs/therapeutic_sensitivity_contrast_mace.json` and `outputs/therapeutic_sensitivity_contrast_mace.md`. It records that both targets have `pos_sigma_0p03_seed_1` as the largest MACE response, while AMPETP adds `short_contact` and ibuprofen remains `high_force_atom` only.

The AMPETP-vs-ibuprofen AIMNet2 and UMA contrast reports are generated at `outputs/therapeutic_sensitivity_contrast_aimnet2_linux.json` and `outputs/therapeutic_sensitivity_contrast_uma.json`. Across all three pilot backends, ibuprofen remains a useful neutral therapeutic contrast because the strongest probe is the same coordinate-noise variant but does not trigger AMPETP's `short_contact` flag.

The evidence-tier report is generated by `scripts/build_evidence_tier_report.py`. It records the practical project reality: crystalline lisdexamfetamine dimesylate is blocked without license-compatible atom coordinates, while AMPETP and ibuprofen are `agi_assisted_guardrailed_pilot` targets. This permits methods and backend-behavior papers, but blocks verified polymorph-benchmark and experimental stability-ranking claims.

The local report rebuild order is documented in `docs/report_workflows.md` and mirrored by `data/curation/report_workflows_v0.1.json`. This covers AMPETP, CPOSS, therapeutic contrast, writing/status artifacts, and local verification commands so the generated evidence can be rebuilt before paper or release decisions.

A conservative release-boundary report is generated at `outputs/crystalprobe_release_boundary.json` and `outputs/crystalprobe_release_boundary.md`. It separates candidate public repository artifacts from CCDC-derived artifacts that need human license review and local-only coordinate-bearing CIF files.

## Scientific Release Criteria

- No headline metric can include `draft` records.
- Every `verified` record must have license, source ID, stability citation, and disorder annotation.
- Every model result must include model name, version/checkpoint, input manifest hash, prediction file hash, and CrystalProbe version.
- Ambiguous stability records are allowed only in exploratory reports.
