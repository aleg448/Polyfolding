# CrystalProbe

CrystalProbe is an interpretability-first research suite for trustworthy polymorph prediction.

For a public-facing walkthrough of the project motivation, architecture, demo, result boundaries, and drug-discovery reliability thesis, see [`CASE_STUDY.md`](CASE_STUDY.md).
For the reviewer-facing visual demo gallery, see [`docs/public_demo.md`](docs/public_demo.md).
For the public demo checklist and one stronger unverified example, see [`docs/public_demo_checklist.md`](docs/public_demo_checklist.md) and [`docs/cases/cposs_ibp_candidate.md`](docs/cases/cposs_ibp_candidate.md).
For the queryable database and static explorer, see [`docs/evidence_atlas.md`](docs/evidence_atlas.md) and [`docs/evidence_atlas.html`](docs/evidence_atlas.html).
For many-molecule software stress testing, see [`docs/molecule_bug_hunt.md`](docs/molecule_bug_hunt.md).
For optional SMILES-to-conformer generation, see [`docs/conformer_generation.md`](docs/conformer_generation.md).
For hashed backend-ready generated-conformer inputs and the tiny backend smoke benchmark, see [`docs/backend_ready_inputs.md`](docs/backend_ready_inputs.md) and [`docs/backend_smoke.md`](docs/backend_smoke.md).
For the first backend result table and joined molecule QA dashboard, see [`docs/backend_result_table.md`](docs/backend_result_table.md) and [`docs/molecule_bug_dashboard.md`](docs/molecule_bug_dashboard.md).
For the tentative molecule benchmark and bug signatures, see [`docs/tentative_molecule_benchmark.md`](docs/tentative_molecule_benchmark.md).
For candidate-safe molecule/crystal viewers that open source-hosted COD/JSmol pages without embedding coordinates, see [`docs/molecule_viewers.md`](docs/molecule_viewers.md).
For the publication-path research spine mapping historical simulation, CSP, uncertainty, and reproducible-research ideas to modern CrystalProbe modules, see [`docs/historical_research_opportunities.md`](docs/historical_research_opportunities.md).
To rebuild the first implemented historical-method report, run `python scripts\build_historical_research_modules_report.py`.
To run the current research loop and first evidence packet, run `python scripts\run_research_cycle.py --pair-id paracetamol_form_i_vs_form_ii_seed`.
To rebuild the evidence database and static explorer, run `python scripts\build_evidence_atlas.py`.
To rebuild the molecule stress database and energy verification layer, run `python scripts\build_molecule_bug_hunt_database.py` and `python scripts\build_energy_verification_report.py`.
To rebuild the optional conformer-generation bridge from the RDKit-enabled project runtime, run `.\.venv\Scripts\python.exe scripts\build_conformer_generation_report.py`.
To hash generated-conformer backend inputs and run the all-molecule backend smoke slice, run `.\.venv\Scripts\python.exe scripts\build_backend_ready_inputs.py` and `.\.venv\Scripts\python.exe scripts\build_backend_smoke_report.py --all --backends mace aimnet2`.
To build the first backend result table and joined molecule QA dashboard, run `.\.venv\Scripts\python.exe scripts\build_backend_result_table.py` and `.\.venv\Scripts\python.exe scripts\build_molecule_bug_dashboard.py`.
To rebuild the tentative molecule benchmark with conformer rows, run `.\.venv\Scripts\python.exe scripts\build_tentative_molecule_benchmark.py`.
To rebuild the candidate-safe molecule viewers, run `python scripts\build_molecule_viewer_report.py`.

The near-term goal is to make polymorph-pair evaluation reproducible before building larger CSP automation on top of it. This repository currently contains the source-controlled research suite for:

- A Pydantic schema for polymorph-pair benchmark records.
- Dataset loading, validation, slicing, and summary utilities.
- Ranking metrics for pairwise stability evaluation.
- A dependency-light uncertainty wrapper interface for MLIP adapters.
- Quick benchmark reporting with provenance ledger output.
- Optional backend discovery for CIF parsing, MLIPs, and FastCSP.
- Draft benchmark curation records, guarded promotion gates, and paper outlines.
- Local-only medication CIF ingestion, measurement summaries, and case-study figures.
- Medication stereochemistry claim-scope reports for enantiomer, racemate, and form-label guardrails.
- CPOSS candidate triage, evidence workpacks, and publication-readiness gates.
- Historical opportunity mapping for claim-gated modules inspired by CSP blind tests, statistical simulation, active learning, calibration, and reproducible research.
- Historical method implementations for motif priors, active evidence triage, landscape auditing, free-energy probes, and calibrated abstention.
- Research-cycle, evidence-packet, and evidence-resolution reports that turn those method surfaces into concrete promotion worklists without auto-promoting candidate evidence.
- A SQLite Evidence Atlas and static explorer for molecules, polymorph pairs, predictions, evidence, blockers, viewer links, and release-boundary artifacts.
- Energy-layer verification reports for prediction units, lower-energy winner semantics, OOD/uncertainty behavior, verified-calibration availability, and non-verified abstention.
- A many-molecule bug-hunt database for salts, charges, stereochemistry, hydrates, fused rings, tautomer-like cases, large molecules, and duplicate-connectivity traps.
- An optional RDKit ETKDG conformer-generation bridge for turning SMILES fixtures into local generated inputs without promoting them to experimental structures.
- A backend-ready input manifest and tiny backend smoke benchmark that hash local generated XYZ files, execute optional backends when available, and record blockers without comparing cross-backend absolute energies.
- A first backend result table and molecule bug dashboard that join parser status, conformer status, backend status, energy/force sanity, and issue signatures across the 85-molecule QA panel.
- A tentative molecule benchmark that ingests a larger CSV panel, runs SMILES checks, optional RDKit parsing/conformer generation, preflights scientific backends, and records structured bug signatures without creating scientific claims.
- Candidate-safe molecule viewer pages that route reviewers to source-hosted COD/JSmol visualizers without redistributing coordinates.

The repository is intentionally structured so benchmark curation, model inference, uncertainty calibration, and paper generation can progress independently while sharing one tested contract.

## Positioning

FastCSP is the closest recent complement and comparison point. It is a full CSP workflow that combines random molecular crystal generation with UMA-powered relaxation, ranking, and free-energy calculations, reporting recovery of known experimental structures within 5 kJ/mol on a curated set of mostly rigid molecules.

CrystalProbe should not compete head-on as another crystal-landscape generator. Its role is narrower and more evidence-focused: FastCSP generates and ranks candidate crystal landscapes; CrystalProbe audits, compares, calibrates, curates, and decides which records are trustworthy enough for benchmark or publication claims.

## Current Research State

- AMPETP is the first paper-ready single-structure pilot, with MACE, AIMNet2, UMA, sensitivity, figures, and research-bundle reports generated locally.
- Modafinil, atomoxetine hydrochloride, and methylphenidate hydrochloride have local-only CCDC/CSD-derived CIF proof blocks selected and measured with MACE, AIMNet2, and UMA.
- Modafinil has S/R enantiomer-labeled records available for local enantiomeric crystal comparison, but its stereochemistry dossier is still claim-scope blocked until racemate/enantiomer scope, solid-form labels, and promotion decision are curated.
- The local execution queue is clear when the configured `.venv` and `.venv-fairchem` runners are available: dependency visibility, medication backend blockers, and queue runner blockers report no active execution blockers.
- CPOSS records remain candidate-only. Verified benchmark and fingerprint-paper claims are blocked until experimental stability evidence, license decisions, disorder annotations, and promotion review produce at least 20 verified pairs.
- Raw CCDC/CSD-derived CIFs and extracted coordinate-bearing blocks are not release artifacts unless license review explicitly permits redistribution.

## Claim Risks

- Overclaiming is the largest risk. Current CPOSS outputs are candidate and inspection evidence, not benchmark truth.
- Licensing is the second risk. CCDC/CSD-derived CIFs and coordinate-derived reports are not automatically redistributable; release-boundary reports must be reviewed before public sharing.
- Model-energy interpretation is the third risk. MACE, AIMNet2, and UMA absolute energies are not automatically comparable across backends. CrystalProbe should compare rankings within a backend and use backend disagreement as an inspection signal unless calibration evidence says otherwise.
- Stereochemistry scope confusion is an additional medication-specific risk. Enantiomer-labeled, racemic, salt, solvate, co-crystal, and true polymorph records can answer different questions; S/R rankings must not be collapsed into polymorph benchmark claims without the stereochemistry dossier passing its required fields.

## Quick Start

```powershell
python scripts\build_public_artifact.py
python scripts\check_public_artifact.py
python scripts\run_public_demo.py --backend-smoke auto
python -m pytest -q
$env:PYTHONPATH='src'
python -m crystalprobe.benchmark.cli validate data\benchmark\v0.1\manifest.jsonl
python -m crystalprobe.benchmark.cli summarize data\benchmark\v0.1\manifest.jsonl
python -m crystalprobe.benchmark.cli score-ranking data\benchmark\v0.1\manifest.jsonl examples\demo_predictions.jsonl
python -m crystalprobe.benchmark.cli curation-report data\benchmark\v0.1\manifest.jsonl
python -m crystalprobe.benchmark.cli calibration data\benchmark\v0.1\manifest.jsonl examples\demo_predictions.jsonl
python -m crystalprobe.benchmark.cli quick-benchmark data\benchmark\v0.1\manifest.jsonl examples\demo_predictions.jsonl outputs\quick --ledger outputs\ledger.jsonl
python -m crystalprobe.benchmark.cli run-config examples\quick_config.json
python -m crystalprobe.benchmark.cli doctor
python -m crystalprobe.benchmark.cli sources
python -m crystalprobe.benchmark.cli cposs-index data\sources\cposs209\cg5c00255_si_004 --no-atoms
python -m crystalprobe.benchmark.cli cposs-pairs data\sources\cposs209\cg5c00255_si_004\All_Psi_Crys.cif
python scripts\run_cposs_structure_inference.py --backend mace --limit 2
```

The included `data/benchmark/v0.1/manifest.jsonl` file is a curation seed, not a verified scientific benchmark. Records marked `draft` may contain `TODO` placeholders and must not be used for claims.

## Repository Map

- `src/crystalprobe/benchmark`: benchmark schema, loader, validation, metrics, and CLI.
- `src/crystalprobe/core`: provenance ledger and hashing utilities.
- `src/crystalprobe/datahub`: source registry for data/model acquisition planning.
- `src/crystalprobe/foundry`: optional scientific backend discovery and MLIP adapter interfaces.
- `src/crystalprobe/insight`: behavioural fingerprint analysis and report generation.
- `src/crystalprobe/openbench`: runnable benchmark pipelines.
- `src/crystalprobe/structures`: optional CIF structure loading.
- `src/crystalprobe/uncertainty`: common prediction types, ensemble aggregation, calibration helpers, and OOD detector interfaces.
- `data/benchmark/v0.1`: draft curation seed for the first anchor molecules.
- `docs`: implementation notes and project architecture.
- `docs/index.md`: documentation entry point.
- `docs/measurement_log.md`: checked-in source-level measurement summaries.
- `docker-compose.yml` and `docker/`: clean Linux container environments for core and fairchem stacks.
- `papers`: living outlines for the fingerprint, data descriptor, and JOSS papers.
- `tests`: unit tests for the current research contract.
- `BLOCKERS.md`: current approval/dependency queue.

## Model Energy Caution

UMA models and legacy inorganic bulk models trained with OMat24 use DFT and DFT+U total-energy labels. These labels are not directly compatible with Materials Project calculations.

If using UMA or OMat24-trained models for formation energies, energy above hull, reference-compound calculations, or related thermodynamic comparisons, use the OMat24-specific reference unary compounds and MP2020-style anion and GGA/GGA+U mixing corrections from the OMat24 Hugging Face repository. Do not apply Materials Project MP2020 corrections or Materials Project reference compounds directly to OMat24-trained model outputs.

Additional care is required when computing energy differences or comparing with Materials Project calculations because DFT pseudopotentials and magnetic ground states can differ. CrystalProbe reports that use UMA or OMat24-derived models must record this compatibility boundary before making thermodynamic claims.

## Licensing

Code is licensed under Apache-2.0. Dataset records must carry per-source licensing metadata; redistributable benchmark releases should use CC-BY-4.0 where allowed.
