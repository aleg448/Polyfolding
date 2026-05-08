# CrystalProbe Report Workflows

This guide records the local rebuild order for the current CrystalProbe research suite. It is meant to keep the AMPETP pilot, CPOSS bridge, therapeutic contrast, and writing artifacts reproducible without relying on memory of the overnight run.

The companion manifest is `data/curation/report_workflows_v0.1.json`; tests check that the scripts named there still exist.

Report scripts bootstrap the repo-local `src/` package path, so the documented `python scripts\...` commands work from an uninstalled source checkout without setting `PYTHONPATH`.

## Guardrails

- Keep raw CCDC exports in `data/sources/` or another ignored local directory.
- Treat `outputs/` as reproducible generated evidence; hash or bundle outputs before using them in a paper draft.
- Report generators write JSON and Markdown outputs through same-directory atomic replacement where practical, so downstream rebuilds should not observe empty or partially written report files.
- Record active Python dependency visibility separately from dependencies installed in `.venv`, Docker, or isolated backend environments.
- Do not interpret perturbation sensitivity results as polymorph stability rankings.
- Record exact backend names, checkpoints, input hashes, and blockers before promoting any claim beyond a pilot result.
- When human database validation is unavailable, rebuild the evidence-tier report and keep the target below benchmark-grade claims.

## AMPETP pilot research bundle

AMPETP is the current proof case because it has local CCDC source evidence, extracted CIF output, MACE and AIMNet2 single-structure measurements, bond/contact diagnostics, sensitivity probes, figures, and a readiness gate.

Rebuild order:

```powershell
python scripts\inspect_ccdc_cif.py data\sources\ccdc\ccdc_amphetamine_phosphate_1036952-978407.cif --json-out outputs\ccdc_amphetamine_bundle_index.json --extract-block AMPETP --extract-out outputs\ccdc_ampetp_extracted.cif
python scripts\run_structure_inference.py data\sources\ccdc\ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend mace --output outputs\ccdc_ampetp_mace.json
python scripts\run_structure_inference.py data\sources\ccdc\ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend aimnet2 --output outputs\ccdc_ampetp_aimnet2.json
docker compose run --rm crystalprobe-fairchem python scripts/run_structure_inference.py data/sources/ccdc/ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend uma --output outputs/ccdc_ampetp_uma.json
python scripts\build_ampetp_case_study.py
python scripts\build_ampetp_sensitivity_set.py
python scripts\run_sensitivity_inference.py outputs\ampetp_sensitivity_manifest.json --backend mace --output outputs\ampetp_sensitivity_mace.jsonl
python scripts\run_sensitivity_inference.py outputs\ampetp_sensitivity_manifest.json --backend aimnet2 --output outputs\ampetp_sensitivity_aimnet2.jsonl --continue-on-error
docker compose run --rm crystalprobe-fairchem python scripts/run_sensitivity_inference.py outputs/ampetp_sensitivity_manifest.json --backend uma --output outputs/ampetp_sensitivity_uma.jsonl --continue-on-error
python scripts\summarize_sensitivity_predictions.py outputs\ampetp_sensitivity_mace.jsonl outputs\ampetp_sensitivity_aimnet2.jsonl outputs\ampetp_sensitivity_uma.jsonl --json-out outputs\ampetp_sensitivity_summary.json --md-out outputs\ampetp_sensitivity_summary.md
python scripts\build_ampetp_figures.py
python scripts\build_ampetp_research_bundle.py
python scripts\build_chemrxiv_preprint_draft.py
python scripts\build_ampetp_readiness_report.py
```

Primary paper-facing outputs:

- `papers/ampetp_case_study.md`
- `outputs/ampetp_case_study_report.md`
- `outputs/ampetp_sensitivity_summary.md`
- `outputs/ampetp_research_bundle_manifest.md`
- `outputs/ampetp_readiness_report.md`
- `outputs/figures/ampetp_provenance_flow.svg`
- `outputs/figures/ampetp_structure_projection.svg`
- `outputs/figures/ampetp_backend_force_diagnostics.svg`
- `outputs/figures/ampetp_sensitivity_energy_deltas.svg`
- `outputs/figures/ampetp_claim_guardrails.svg`

## CPOSS mini-benchmark bridge

The CPOSS bridge keeps the suite connected to polymorph-ranking work while the AMPETP case study remains a single-structure pilot.

```powershell
python scripts\build_cposs_mini_benchmark_report.py
python scripts\build_cposs_pair_candidate_report.py
python scripts\build_cposs_pair_triage_report.py
python scripts\build_cposs_candidate_cards.py
python scripts\build_cposs_evidence_workpack.py
python scripts\seed_cposs_block_form_mapping_manifest.py
python scripts\build_cposs_block_mapping_report.py
python scripts\build_cposs_block_mapping_dossier.py
docker compose run --rm crystalprobe-core python scripts/run_cposs_structure_inference.py --backend mace --block-id IBP01_PsiCrys --block-id IBP06_PsiCrys --block-id CBZ01_PsiCrys --block-id CBZ03_PsiCrys --output outputs/cposs_candidates_high_priority_mace.jsonl --continue-on-error
docker compose run --rm crystalprobe-core python scripts/run_cposs_structure_inference.py --backend aimnet2 --block-id IBP01_PsiCrys --block-id IBP06_PsiCrys --block-id CBZ01_PsiCrys --block-id CBZ03_PsiCrys --output outputs/cposs_candidates_high_priority_aimnet2.jsonl --continue-on-error
docker compose run --rm crystalprobe-fairchem python scripts/run_cposs_structure_inference.py --backend uma --block-id IBP01_PsiCrys --block-id IBP06_PsiCrys --block-id CBZ01_PsiCrys --block-id CBZ03_PsiCrys --output outputs/cposs_candidates_high_priority_uma.jsonl --continue-on-error
python scripts\build_cposs_backend_disagreement_report.py
python scripts\build_cposs_disagreement_inspection.py
```

Primary outputs:

- `outputs/cposs_mini_benchmark_report.json`
- `outputs/cposs_mini_benchmark_report.md`
- `outputs/cposs_pair_candidate_report.json`
- `outputs/cposs_pair_candidate_report.md`
- `outputs/cposs_pair_triage_report.json`
- `outputs/cposs_pair_triage_report.md`
- `outputs/cposs_candidate_cards.json`
- `outputs/cposs_candidate_cards.md`
- `outputs/cposs_evidence_workpack.json`
- `outputs/cposs_evidence_workpack.md`
- `outputs/cposs_block_form_mapping.json`
- `outputs/cposs_block_form_mapping.md`
- `outputs/cposs_block_mapping_dossier.json`
- `outputs/cposs_block_mapping_dossier.md`
- `outputs/cposs_high_priority_backend_disagreement.json`
- `outputs/cposs_high_priority_backend_disagreement.md`
- `outputs/cposs_cbz_disagreement_inspection.json`
- `outputs/cposs_cbz_disagreement_inspection.md`

The candidate cards include exact MACE, AIMNet2, and UMA commands for follow-up measurements on each pair. They remain AGI-assisted planning artifacts, not benchmark records.

`scripts\build_cposs_evidence_workpack.py` reads optional curation overlays from `data/curation/cposs_evidence_overrides_v0.1.json`. The current default CPOSS bridge uses ACR, CBZ, FLU, and IBP MACE summaries, expanding the workpack past the first 20-entry milestone while retaining family-level literature/source-review metadata and `do_not_promote` decisions. It does not create verified benchmark records.

`scripts\seed_cposs_block_form_mapping_manifest.py` fills missing block rows in `data/curation/cposs_block_form_mapping_v0.1.json` from the current evidence workpack while preserving any existing curation. `scripts\build_cposs_block_mapping_report.py` reads that manifest and converts the workpack into a block-to-experimental-form mapping queue. `scripts\build_cposs_block_mapping_dossier.py` then creates a focused checklist for the top block target, or for a named `--block-id`. This is the next gate after family-level literature mapping: each CPOSS block needs a locked form label, high-confidence cell/space-group/formula/source-label checks, license resolution, and disorder annotation before a pair can be promoted.

The high-priority disagreement report compares the current ibuprofen and carbamazepine CPOSS candidate pairs across MACE, AIMNet2, and UMA. It is a backend-behavior inspection report, not an experimental stability result.

The CBZ inspection report focuses that disagreement into findings and follow-up actions for carbamazepine.

## Source discovery

Use this report for medication-priority targets that need coordinates before measurement.

```powershell
python scripts\build_source_discovery_report.py
python scripts\build_source_acquisition_report.py
python scripts\build_medication_cif_ingestion_report.py --extract
python scripts\build_medication_figures.py
python scripts\build_medication_research_bundle.py
```

Primary outputs:

- `outputs/crystalprobe_source_discovery.json`
- `outputs/crystalprobe_source_discovery.md`
- `outputs/crystalprobe_source_acquisition.json`
- `outputs/crystalprobe_source_acquisition.md`
- `outputs/medication_cif_ingestion.json`
- `outputs/medication_cif_ingestion.md`
- `outputs/medication_measurement_summary.json`
- `outputs/medication_measurement_summary.md`
- `outputs/figures/medication_case_study_coverage.svg`
- `outputs/medication_research_bundle_manifest.json`
- `outputs/medication_research_bundle_manifest.md`

The current reports classify modafinil, atomoxetine hydrochloride, and methylphenidate hydrochloride as measured local-only targets after the user-provided CIF downloads. These sources remain local-only until redistribution terms are reviewed.

Medication single-structure measurements use selected block IDs from `data/curation/medication_cif_selection_v0.1.json`. Run MACE first, then AIMNet2 and UMA only for selected blocks that parse cleanly.

Medication backend runs are tracked in `data/curation/medication_backend_blockers_v0.1.json` and rendered into `outputs/medication_measurement_summary.md`. The current blocker file is cleared: the selected modafinil, atomoxetine hydrochloride, and methylphenidate hydrochloride proof blocks each have MACE, AIMNet2, and UMA measurements. Do not reintroduce a blocker unless the corresponding backend output is missing or fails validation.

## CPOSS benchmark promotion

Use this gate to keep CPOSS candidates below benchmark status until stability evidence is attached.

```powershell
python scripts\seed_cposs_block_form_mapping_manifest.py
python scripts\build_cposs_block_mapping_report.py
python scripts\build_cposs_block_mapping_dossier.py
python scripts\build_cposs_promoted_pairs.py --block-mapping outputs\cposs_block_form_mapping.json
```

Primary outputs:

- `outputs/cposs_promotion_gate.json`
- `outputs/cposs_promotion_gate.md`
- `outputs/cposs_block_form_mapping.json`
- `outputs/cposs_block_form_mapping.md`
- `outputs/cposs_block_mapping_dossier.json`
- `outputs/cposs_block_mapping_dossier.md`
- `outputs/cposs_promoted_pairs.jsonl`

The promotion gate only emits canonical `PolymorphPair` records for candidates with experimental stability ordering, citation, license decisions, disorder annotations, curator, reviewer, and a promote decision. When `outputs\cposs_block_form_mapping.json` exists, `scripts\build_cposs_promoted_pairs.py` enforces it as an additional hard gate, so a `promote` decision still remains blocked until both structures in the candidate pair are mapping-ready.

## Therapeutic sensitivity contrast

The current neutral contrast is ibuprofen CCDC 774097. It uses the same deterministic perturbation protocol as AMPETP so the report can compare local response profiles while keeping claims narrow.

```powershell
python scripts\build_ccdc_sensitivity_set.py data\sources\ccdc\ccdc_ibuprofen_bundle_1041369-776185.cif --block-id ibuprofen --title "Ibuprofen CCDC 774097 deterministic perturbation sensitivity set" --output-dir outputs\ibuprofen_sensitivity --manifest outputs\ibuprofen_sensitivity_manifest.json
python scripts\run_sensitivity_inference.py outputs\ibuprofen_sensitivity_manifest.json --backend mace --output outputs\ibuprofen_sensitivity_mace.jsonl
python scripts\summarize_sensitivity_predictions.py outputs\ibuprofen_sensitivity_mace.jsonl --json-out outputs\ibuprofen_sensitivity_summary_mace.json --md-out outputs\ibuprofen_sensitivity_summary_mace.md --title "Ibuprofen CCDC 774097 MACE perturbation sensitivity summary"
docker compose run --rm crystalprobe-core python scripts/run_sensitivity_inference.py outputs/ibuprofen_sensitivity_manifest.json --backend aimnet2 --output outputs/ibuprofen_sensitivity_aimnet2_linux.jsonl --continue-on-error
python scripts\summarize_sensitivity_predictions.py outputs\ibuprofen_sensitivity_aimnet2_linux.jsonl --json-out outputs\ibuprofen_sensitivity_summary_aimnet2_linux.json --md-out outputs\ibuprofen_sensitivity_summary_aimnet2_linux.md --title "Ibuprofen CCDC 774097 AIMNet2 Linux perturbation sensitivity summary"
docker compose run --rm crystalprobe-fairchem python scripts/run_sensitivity_inference.py outputs/ibuprofen_sensitivity_manifest.json --backend uma --output outputs/ibuprofen_sensitivity_uma.jsonl --continue-on-error
python scripts\summarize_sensitivity_predictions.py outputs\ibuprofen_sensitivity_uma.jsonl --json-out outputs\ibuprofen_sensitivity_summary_uma.json --md-out outputs\ibuprofen_sensitivity_summary_uma.md --title "Ibuprofen CCDC 774097 UMA perturbation sensitivity summary"
python scripts\build_sensitivity_contrast_report.py
python scripts\build_sensitivity_contrast_report.py --ibuprofen outputs\ibuprofen_sensitivity_summary_aimnet2_linux.json --backend aimnet2 --json-out outputs\therapeutic_sensitivity_contrast_aimnet2_linux.json --md-out outputs\therapeutic_sensitivity_contrast_aimnet2_linux.md
python scripts\build_sensitivity_contrast_report.py --ibuprofen outputs\ibuprofen_sensitivity_summary_uma.json --backend uma --json-out outputs\therapeutic_sensitivity_contrast_uma.json --md-out outputs\therapeutic_sensitivity_contrast_uma.md
python scripts\build_backend_disagreement_report.py
python scripts\build_uncertainty_proxy_report.py
```

Primary outputs:

- `outputs/ibuprofen_sensitivity_summary_mace.md`
- `outputs/ibuprofen_sensitivity_summary_aimnet2_linux.md`
- `outputs/ibuprofen_sensitivity_summary_uma.md`
- `outputs/therapeutic_sensitivity_contrast_mace.md`
- `outputs/therapeutic_sensitivity_contrast_aimnet2_linux.md`
- `outputs/therapeutic_sensitivity_contrast_uma.md`
- `outputs/ampetp_backend_disagreement.md`
- `outputs/crystalprobe_uncertainty_proxy_v0.md`

The uncertainty proxy is deliberately uncalibrated. It uses backend ranking and diagnostic-flag disagreement as an inspection trigger, not as a thermodynamic confidence interval.

## Model validation guardrails

Use this report before routing new FAIR Chemistry checkpoints into CrystalProbe claims.

```powershell
python scripts\build_model_guardrails_report.py
```

Primary outputs:

- `outputs/fairchem_model_guardrails.json`
- `outputs/fairchem_model_guardrails.md`

OMAT24 and OMol25 access are accepted locally, but these models remain validation-blocked for CrystalProbe scientific claims until task-specific calculation paths and reference policies are implemented.

## Active Python dependency blockers

Use this report before interpreting a failed local command as a missing project capability. It records which optional scientific dependencies are visible to the active `python` executable and which configured project runners can satisfy backend-specific dependency groups.

```powershell
python scripts\build_environment_blockers_report.py
```

Primary outputs:

- `outputs/crystalprobe_environment_blockers.json`
- `outputs/crystalprobe_environment_blockers.md`

## Execution unblock checklist

Use this report to bring active Python dependency blockers, medication backend blockers, and queue-level runner blockers into one approval-ready checklist.

```powershell
python scripts\build_execution_unblock_report.py
```

Primary outputs:

- `outputs/crystalprobe_execution_unblock_report.json`
- `outputs/crystalprobe_execution_unblock_report.md`

The current execution-unblock state is clear when the configured `.venv` and `.venv-fairchem` runners are present. Remaining blockers are publication and curation gates, not local execution blockers.

## Handoff summary

Use this report as the first artifact to open after a long unattended run. It distills project status, roadmap status, measurement queue, and the execution unblock checklist into one compact local handoff.

```powershell
python scripts\build_handoff_report.py
```

Primary outputs:

- `outputs/crystalprobe_handoff_summary.json`
- `outputs/crystalprobe_handoff_summary.md`

## Publication readiness

Use this report as a conservative release gate before treating local artifacts as paper- or public-release-ready. It combines CPOSS promotion status, fingerprint figure readiness, release-boundary categories, execution blockers, and remaining human-input items.
When `outputs/cposs_block_form_mapping.json` exists, publication readiness also blocks on locked block-to-experimental-form mappings for all CPOSS candidate pairs.

```powershell
python scripts\build_publication_readiness_report.py
```

Primary outputs:

- `outputs/crystalprobe_publication_readiness.json`
- `outputs/crystalprobe_publication_readiness.md`

## Substance research profiles

Use this report to consolidate the medication-priority queue, local measurements, evidence tiers, CPOSS disagreement, and claim boundaries into one substance-by-substance view.

```powershell
python scripts\build_substance_profiles.py
```

Primary outputs:

- `outputs/crystalprobe_substance_profiles.json`
- `outputs/crystalprobe_substance_profiles.md`

The profiles are research-catalog records, not medical advice. They currently cover ADHD-priority substances, everyday foundation medicines, ibuprofen, carbamazepine, lisdexamfetamine dimesylate, and the measured AMPETP proxy target.

## Measurement and curation queue

Use this report after rebuilding substance profiles. It ranks the next measurement, source-discovery, and backend-inspection tasks by project utility.

```powershell
python scripts\build_measurement_queue.py
```

Primary outputs:

- `outputs/crystalprobe_measurement_queue.json`
- `outputs/crystalprobe_measurement_queue.md`

The queue priority is not a clinical or medical priority ranking. It is a CrystalProbe roadmap utility ranking.

The queue also records active-runner blockers from `outputs/crystalprobe_environment_blockers.json`, so a dependency-heavy action can be scientifically ready while still requiring `.venv`, Docker, or another Python environment to execute.

## AGI-assisted evidence-tier policy

Use this report when lisdexamfetamine coordinates or human validation are unavailable. It keeps AGI-assisted evidence usable while preventing automatic promotion into benchmark claims.

```powershell
python scripts\build_evidence_tier_report.py
```

Primary outputs:

- `outputs/crystalprobe_evidence_tiers.json`
- `outputs/crystalprobe_evidence_tiers.md`

## Writing and roadmap artifacts

These commands rebuild the current manuscript-facing layer from the generated evidence reports.

```powershell
python scripts\build_preliminary_findings_memo.py
python scripts\build_chemrxiv_preprint_draft.py
python scripts\build_project_status_dashboard.py --test-summary "CURRENT_TEST_SUMMARY"
python scripts\build_roadmap_status_report.py
python scripts\build_release_boundary_report.py
python scripts\build_source_discovery_report.py
python scripts\build_source_acquisition_report.py
python scripts\build_medication_cif_ingestion_report.py
python scripts\seed_cposs_block_form_mapping_manifest.py
python scripts\build_cposs_block_mapping_report.py
python scripts\build_cposs_block_mapping_dossier.py
python scripts\build_cposs_promoted_pairs.py
python scripts\build_fingerprint_artifact_plan.py
python scripts\build_evidence_tier_report.py
python scripts\build_substance_profiles.py
python scripts\build_measurement_queue.py
python scripts\build_model_guardrails_report.py
python scripts\build_environment_blockers_report.py
python scripts\build_execution_unblock_report.py
python scripts\build_handoff_report.py
python scripts\build_publication_readiness_report.py
python scripts\build_uncertainty_proxy_report.py
```

Replace `CURRENT_TEST_SUMMARY` with the latest local pytest result, for example `151 passed, 3 skipped`.

Primary outputs:

- `outputs/crystalprobe_preliminary_findings_memo.md`
- `outputs/crystalprobe_chemrxiv_preprint_draft.md`
- `outputs/crystalprobe_project_status.md`
- `outputs/crystalprobe_roadmap_status.md`
- `outputs/crystalprobe_release_boundary.md`
- `outputs/crystalprobe_source_discovery.md`
- `outputs/crystalprobe_source_acquisition.md`
- `outputs/medication_cif_ingestion.md`
- `outputs/medication_measurement_summary.md`
- `outputs/cposs_block_form_mapping.md`
- `outputs/cposs_block_mapping_dossier.md`
- `outputs/cposs_promotion_gate.md`
- `outputs/crystalprobe_fingerprint_artifact_plan.md`
- `outputs/crystalprobe_evidence_tiers.md`
- `outputs/crystalprobe_substance_profiles.md`
- `outputs/crystalprobe_measurement_queue.md`
- `outputs/fairchem_model_guardrails.md`
- `outputs/crystalprobe_environment_blockers.md`
- `outputs/crystalprobe_execution_unblock_report.md`
- `outputs/crystalprobe_handoff_summary.md`
- `outputs/crystalprobe_publication_readiness.md`
- `outputs/crystalprobe_uncertainty_proxy_v0.md`

## Verification

Run local verification after changing scripts, modules, tests, or paper-facing report logic:

```powershell
python -B -m pytest -q -p no:cacheprovider
python -B -m compileall -q src scripts tests
```

For dependency-heavy verification, use the Linux/Docker path in `docs/linux_environment.md` and record any blocked backend, missing checkpoint, or gated dataset access in `BLOCKERS.md`.
