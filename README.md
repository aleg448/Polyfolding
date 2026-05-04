# CrystalProbe

CrystalProbe is an interpretability-first research suite for trustworthy polymorph prediction.

The near-term goal is to make polymorph-pair evaluation reproducible before building larger CSP automation on top of it. This repository currently contains the Week 1 foundation:

- A Pydantic schema for polymorph-pair benchmark records.
- Dataset loading, validation, slicing, and summary utilities.
- Ranking metrics for pairwise stability evaluation.
- A dependency-light uncertainty wrapper interface for MLIP adapters.
- Quick benchmark reporting with provenance ledger output.
- Optional backend discovery for CIF parsing, MLIPs, and FastCSP.
- Draft benchmark curation records and paper outlines.

The repository is intentionally structured so benchmark curation, model inference, uncertainty calibration, and paper generation can progress independently while sharing one tested contract.

## Quick Start

```powershell
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
