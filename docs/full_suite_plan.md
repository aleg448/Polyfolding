# CrystalProbe Full-Suite Build Plan

This repository implements the CrystalProbe vertical slice as a dependency-light research suite. The full POLARIS architecture remains the long horizon; CrystalProbe focuses on the trust infrastructure needed first.

## Implemented Locally

- Benchmark schema and curation readiness checks.
- Pairwise prediction file format.
- Ranking and behavioural fingerprint metrics.
- Markdown/JSON report generation with atomic output replacement for report files where practical.
- Quick benchmark runner with provenance ledger output.
- Optional adapter discovery for ASE, MACE-OFF, AIMNet2, UMA, and FastCSP.
- CCDC multi-CIF block extraction and AMPETP/ibuprofen proof measurements.
- Single-structure case-study report generation for AMPETP backend agreement.
- Deterministic AMPETP perturbation-set generation for coordinate-noise and cell-scaling sensitivity probes.
- AGI-assisted evidence-tier policy for work that lacks human database validation or redistributable coordinates.
- Backend-disagreement metrics over deterministic multi-backend sensitivity summaries.
- CPOSS AGI-assisted candidate cards with claim boundaries and follow-up backend commands.
- Medication CIF selection, ingestion, source-acquisition, local measurement, autonomous polymorphism triage, and backend-blocker reporting.
- Environment, execution-unblock, handoff, publication-readiness, and risk-register reports for unattended or long-running work sessions.
- CPOSS promotion gate from evidence workpack entries to canonical benchmark records, with field-completion, curation-queue, block-to-form mapping, promotion burn-down, and chemistry-family summaries.
- Fingerprint artifact readiness gating, including pre-benchmark CBZ/IBP candidate-slice tracking and a generated medication case-study coverage figure.
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

## Positioning Against FastCSP

FastCSP is the closest recent complement to CrystalProbe. It is closer to a complete CSP production workflow: it combines random molecular crystal generation with UMA-powered relaxation, ranking, and free-energy calculations, and reports known experimental structures within 5 kJ/mol on a curated set of mostly rigid molecules.

CrystalProbe should therefore avoid head-to-head positioning as a generator of crystal landscapes. The stronger role is downstream and orthogonal: FastCSP generates and ranks candidate crystal landscapes; CrystalProbe audits, compares, calibrates, curates, and decides which candidate records can become trustworthy benchmark or publication claims.

This positioning sets three release risks:

- Do not overclaim candidate evidence. Current CPOSS outputs remain inspection and curation artifacts until stability evidence, license decisions, disorder annotations, and promotion review produce verified pairs.
- Do not blur licensing boundaries. CCDC/CSD-derived CIFs, coordinate-derived reports, and generated figures stay license-review-required or local-only until human review explicitly clears them.
- Do not compare absolute model energies across backends as if they were a shared thermodynamic scale. MACE, AIMNet2, and UMA are strongest here as within-backend ranking tools, while backend disagreement remains an inspection signal until calibrated.

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

A CPOSS block-to-form mapping report is generated at `outputs/cposs_block_form_mapping.json` and `outputs/cposs_block_form_mapping.md`. It turns the current literature-mapped workpack into a per-block mapping queue, requiring locked experimental form labels, high-confidence cell/space-group/formula/source-label matching, license resolution, and disorder annotation before any pair can become promotion-ready.

The current preliminary findings memo is generated at `outputs/crystalprobe_preliminary_findings_memo.md`. It summarizes AMPETP readiness, AMPETP sensitivity, the CPOSS bridge, and the remaining guardrails in a collaborator-facing format.

A ChemRxiv-style preprint draft scaffold is generated at `outputs/crystalprobe_chemrxiv_preprint_draft.md`. It expands the preliminary memo into abstract, introduction, methods, results, discussion, limitations, and reproducibility sections.

The current project status dashboard is generated at `outputs/crystalprobe_project_status.json` and `outputs/crystalprobe_project_status.md`. It summarizes AMPETP readiness, CPOSS bridge scope, latest local verification, and remaining user-input blockers.

The roadmap-level status report is generated at `outputs/crystalprobe_roadmap_status.json` and `outputs/crystalprobe_roadmap_status.md`. It maps the current artifact set against the full CrystalProbe deliverables: benchmark, fingerprint paper, uncertainty wrapper, FastCSP layer, and software paper. It now consumes CPOSS promotion milestones and fingerprint candidate slices, so the roadmap reports the current 0-promoted state plus CBZ/IBP pre-benchmark coverage directly.

The deterministic CCDC sensitivity generator is now generic via `scripts/build_ccdc_sensitivity_set.py`. It has been applied to ibuprofen CCDC 774097 as a neutral therapeutic contrast. MACE, AIMNet2, and UMA sensitivity summaries now exist locally or through Docker/Linux runs for the AMPETP-vs-ibuprofen pilot contrast.

The AMPETP-vs-ibuprofen MACE contrast report is generated at `outputs/therapeutic_sensitivity_contrast_mace.json` and `outputs/therapeutic_sensitivity_contrast_mace.md`. It records that both targets have `pos_sigma_0p03_seed_1` as the largest MACE response, while AMPETP adds `short_contact` and ibuprofen remains `high_force_atom` only.

The AMPETP-vs-ibuprofen AIMNet2 and UMA contrast reports are generated at `outputs/therapeutic_sensitivity_contrast_aimnet2_linux.json` and `outputs/therapeutic_sensitivity_contrast_uma.json`. Across all three pilot backends, ibuprofen remains a useful neutral therapeutic contrast because the strongest probe is the same coordinate-noise variant but does not trigger AMPETP's `short_contact` flag.

The AMPETP backend-disagreement report is generated at `outputs/ampetp_backend_disagreement.json` and `outputs/ampetp_backend_disagreement.md`. It compares within-backend response rank, largest-response consensus, diagnostic flag Jaccard, and max-delta ratios across MACE, AIMNet2, and UMA. This is the first uncalibrated uncertainty proxy and must not be interpreted as thermodynamic uncertainty.

The evidence-tier report is generated by `scripts/build_evidence_tier_report.py`. It records the practical project reality: crystalline lisdexamfetamine dimesylate is blocked without license-compatible atom coordinates, while AMPETP and ibuprofen are `agi_assisted_guardrailed_pilot` targets. This permits methods and backend-behavior papers, but blocks verified polymorph-benchmark and experimental stability-ranking claims.

The CPOSS candidate-card report is generated at `outputs/cposs_candidate_cards.json` and `outputs/cposs_candidate_cards.md`. Each card records priority, evidence tier, blocked claims, next actions, and exact MACE/AIMNet2/UMA commands for targeted follow-up measurements on the two candidate structures.

The high-priority CPOSS candidate-card commands have been executed for ibuprofen (`IBP01_PsiCrys` vs `IBP06_PsiCrys`) and carbamazepine (`CBZ01_PsiCrys` vs `CBZ03_PsiCrys`) across MACE, AIMNet2, and UMA. The generated report is `outputs/cposs_high_priority_backend_disagreement.json` and `outputs/cposs_high_priority_backend_disagreement.md`. Ibuprofen currently shows cross-backend ordering consensus, while carbamazepine shows a backend-ordering disagreement: MACE and AIMNet2 place `CBZ01_PsiCrys` lower and UMA places `CBZ03_PsiCrys` lower. This is an inspection trigger, not an experimental stability claim.

The carbamazepine disagreement inspection is generated at `outputs/cposs_cbz_disagreement_inspection.json` and `outputs/cposs_cbz_disagreement_inspection.md`. It records the ordering flip, the AIMNet2 gap outlier, and diagnostic-flag mismatch as uncertainty-wrapper and case-selection evidence only.

The source-discovery report is generated at `outputs/crystalprobe_source_discovery.json` and `outputs/crystalprobe_source_discovery.md`. The follow-on source-acquisition report is generated at `outputs/crystalprobe_source_acquisition.json` and `outputs/crystalprobe_source_acquisition.md`. Modafinil, atomoxetine hydrochloride, and methylphenidate hydrochloride now have local CCDC/CSD-derived CIF bundles and are classified as `measured_local_only`, with public redistribution still blocked until license review.

Medication CIF ingestion is generated at `outputs/medication_cif_ingestion.json` and `outputs/medication_cif_ingestion.md` from `data/curation/medication_cif_selection_v0.1.json`. The current selected blocks cover parent-priority modafinil, atomoxetine hydrochloride, methylphenidate hydrochloride, and role-labeled related structures that must not be used as parent medication proof.

The medication measurement summary is generated at `outputs/medication_measurement_summary.json` and `outputs/medication_measurement_summary.md`. It currently records three measured local-only medication targets: modafinil, atomoxetine hydrochloride, and methylphenidate hydrochloride. Each selected proof block now has MACE, AIMNet2, and UMA measurements. `data/curation/medication_backend_blockers_v0.1.json` is therefore in the `medication_backend_blockers_cleared` state with zero pending backend commands.

The medication polymorphism autonomy report is generated at `outputs/medication_polymorphism_autonomy.json` and `outputs/medication_polymorphism_autonomy.md`. It is the first local autonomous triage layer for medication polymorphism detection: it groups eligible same-formula parent-like CIF blocks, checks whether at least two structures share a measured backend, and records blockers for stereochemistry, form-label, license, and measurement coverage. It deliberately emits unverified autonomous candidates rather than verified polymorphism claims.

Medication stereochemistry is now treated as a first-class claim scope rather than only a blocker. Enantiomer-labeled records such as modafinil S/R forms can support enantiomeric crystal comparison, while still being blocked from polymorph promotion until racemate/enantiomer/form-label scope is explicit. This matters for medication crystallography because enantiomers, racemates, salts, solvates, co-crystals, and true polymorphs can each have different stability and pharmacological relevance.

The medication stereochemistry report is generated at `outputs/medication_stereochemistry.json` and `outputs/medication_stereochemistry.md`. It summarizes enantiomer-scope targets, S/R block counts, rankability, and blockers, keeping enantiomeric crystal comparison as a separate evidence lane from polymorph benchmark promotion.

The medication stereochemistry dossier is generated at `outputs/medication_stereochemistry_dossier.json` and `outputs/medication_stereochemistry_dossier.md`. It converts paired S/R evidence into a curator checklist for source racemate/enantiomer scope, local block stereochemistry, solid-form labels, ranking interpretation, and promotion decision.

The medication stereochemistry scope figure is generated at `outputs/figures/medication_stereochemistry_scope.svg` and is tracked by the fingerprint artifact plan as a medication claim-scope panel, not a benchmark ranking or calibration figure.

The medication benchmark evidence gate is generated at `outputs/medication_benchmark_evidence.json` and `outputs/medication_benchmark_evidence.md`, with optional source dossiers stored in `data/curation/medication_polymorphism_evidence_v0.1.json`. This is the bridge toward verified benchmark truth: autonomous candidates stay unverified until citation, stability ordering, form-label map, identity/stereochemistry decisions, contradiction search, disorder, license, curator, reviewer, and promotion decision fields are complete. Without human expert review, the maximum tier remains `source_verified_autonomous_benchmark_candidate`.

The medication polymorph generation readiness report is generated at `outputs/medication_polymorph_generation.json` and `outputs/medication_polymorph_generation.md`. It starts the generation side without overclaiming: selected local CIF blocks are treated as local-only seed structures, source forms are listed from the evidence dossiers, and each target receives a next generation step such as shared-backend measurement, evidence-gate resolution, or later CSP/FastCSP-style candidate generation.

The medication seed ranking report is generated at `outputs/medication_seed_ranking.json` and `outputs/medication_seed_ranking.md`. It ranks only same-backend seed measurements and normalizes energy to the candidate formula unit. This makes modafinil locally inspectable within MACE while preserving the blocker that enantiomer/form-label evidence must be resolved before verified polymorphism claims.

The FAIR Chemistry model guardrail report is generated at `outputs/fairchem_model_guardrails.json` and `outputs/fairchem_model_guardrails.md`. It records that UMA and OMC25 are locally smoke-verified for current CrystalProbe paths, while OMAT24 and OMol25 remain validation-blocked for CrystalProbe scientific claims until task-specific workflows and reference policies are implemented.

The uncertainty proxy v0 report is generated at `outputs/crystalprobe_uncertainty_proxy_v0.json` and `outputs/crystalprobe_uncertainty_proxy_v0.md`. It aggregates AMPETP sensitivity disagreement and CPOSS high-priority disagreement evidence into target-level inspection decisions. It is an uncalibrated backend-behavior proxy, not a thermodynamic uncertainty estimate.

The CPOSS promotion gate is generated at `outputs/cposs_promotion_gate.json` and `outputs/cposs_promotion_gate.md`, with promoted records written to `outputs/cposs_promoted_pairs.jsonl` only after stability evidence, license decisions, disorder annotations, curator/reviewer, and promotion decision are complete. Evidence-populated but not block-verified candidates are classified as `literature_mapped_candidate`, not benchmark records. The gate now includes an evidence field-completion matrix, a priority-sorted curation queue, per-candidate upgrade requirements, and a chemistry-family summary covering ACR, CBZ, FLU, and IBP. The separate block-to-form report records the exact block-level mapping blockers preventing upgrade from literature-mapped candidates to verified benchmark records. The workpack is expanded beyond the first 20-entry curation milestone while remaining at 0 verified benchmark pairs.

The CPOSS promotion burn-down report is generated at `outputs/cposs_promotion_burndown.json` and `outputs/cposs_promotion_burndown.md`. It converts the promotion gate and block-to-form report into a first-20-pair action plan: selected candidate pairs, deduplicated block rows, blocker counts, and acceptance gates. This is the operational bridge between candidate inspection and verified benchmark promotion.

The fingerprint artifact plan is generated at `outputs/crystalprobe_fingerprint_artifact_plan.json` and `outputs/crystalprobe_fingerprint_artifact_plan.md`. It blocks ranking-accuracy and calibration figures until at least 20 verified benchmark pairs exist, while the medication case-study panel is now ready and generated at `outputs/figures/medication_case_study_coverage.svg`. The plan also surfaces the same ACR/CBZ/FLU/IBP candidate-family slices as pre-benchmark planning context without promoting them into paper-facing benchmark metrics.

The substance-profile report is generated at `outputs/crystalprobe_substance_profiles.json` and `outputs/crystalprobe_substance_profiles.md`. It creates a bounded profile for each current medication-priority target, merging the therapeutic queue, local CCDC source records, lisdexamfetamine proof layers, evidence tiers, CPOSS backend disagreement, and next actions. This is now the preferred overview for deciding which substance to measure or curate next.

The measurement and curation queue is generated at `outputs/crystalprobe_measurement_queue.json` and `outputs/crystalprobe_measurement_queue.md`. It converts substance profiles into ranked actions: coordinate acquisition, backend-disagreement inspection, source discovery, guarded pilot maintenance, and source seeding. The queue now consumes the environment-blockers report and records zero active runner blockers when the configured `.venv` and `.venv-fairchem` runners are available.

The queue now has a dedicated `curate_stereochemistry_scope` action for enantiomer-labeled medication evidence. Modafinil currently uses this lane so S/R and racemate/form labels are curated before any polymorph benchmark interpretation.

The local report rebuild order is documented in `docs/report_workflows.md` and mirrored by `data/curation/report_workflows_v0.1.json`. This covers AMPETP, CPOSS, therapeutic contrast, writing/status artifacts, and local verification commands so the generated evidence can be rebuilt before paper or release decisions.

A conservative release-boundary report is generated at `outputs/crystalprobe_release_boundary.json` and `outputs/crystalprobe_release_boundary.md`. It separates candidate public repository artifacts from CCDC-derived artifacts that need human license review and local-only coordinate-bearing CIF files.

The execution-unblock report is generated at `outputs/crystalprobe_execution_unblock_report.json` and `outputs/crystalprobe_execution_unblock_report.md`. It currently reports the execution queue as clear: active dependency visibility, configured runner availability, medication backend blockers, and queue-level runner blockers have no unresolved execution blockers.

The publication-readiness report is generated at `outputs/crystalprobe_publication_readiness.json` and `outputs/crystalprobe_publication_readiness.md`. It remains intentionally blocked for scientific/release reasons: 0 verified CPOSS pairs are promoted, benchmark-grade fingerprint figures require verified pairs, local-only coordinate artifacts need license review, and medication CIF public-reference policy still needs human input.

The risk register is generated at `outputs/crystalprobe_risk_register.json` and `outputs/crystalprobe_risk_register.md`. It turns the three main project risks into tested, generated gates: overclaiming candidate evidence, CCDC/CSD licensing, and cross-backend energy interpretation. It also tracks FastCSP positioning drift so CrystalProbe remains framed as the audit, curation, calibration, and claim-readiness layer around candidate crystal-landscape outputs.

## Scientific Release Criteria

- No headline metric can include `draft` records.
- Every `verified` record must have license, source ID, stability citation, and disorder annotation.
- Every model result must include model name, version/checkpoint, input manifest hash, prediction file hash, and CrystalProbe version.
- Ambiguous stability records are allowed only in exploratory reports.
