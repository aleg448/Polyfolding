# Source Registry

CrystalProbe should prefer open, redistributable sources and keep license status explicit at record level.

## CPOSS209

CPOSS209 is the first benchmark spine. The paper is "One Size Fits All? Development of the CPOSS209 Data Set of Experimental and Hypothetical Polymorphs for Testing Computational Modeling Methods" in *Crystal Growth & Design*.

- Paper DOI: https://doi.org/10.1021/acs.cgd.5c00255
- ACS page: https://pubs.acs.org/doi/10.1021/acs.cgd.5c00255
- Figshare dataset page: https://acs.figshare.com/articles/dataset/28883051

Before redistributing derived records, verify the license terms of the Figshare files and preserve attribution.

CrystalProbe keeps raw source archives under `data/sources/`, which is ignored by git. Checked-in benchmark manifests should only contain curated, license-audited records.

The CPOSS209 supplemental ZIP is the current benchmark spine. After download and extraction, inspect it with:

```powershell
python scripts\inspect_cposs209.py
python -m crystalprobe.benchmark.cli cposs-index data\sources\cposs209\cg5c00255_si_004 --no-atoms
python -m crystalprobe.benchmark.cli cposs-pairs data\sources\cposs209\cg5c00255_si_004\All_Psi_Crys.cif
```

The local archive currently indexes as 20 molecule families and 422 CIF data blocks: 209 `PsiCrys`, 209 `PsiMol`, and 4 additional molecule blocks. This is source inventory, not a curated stability benchmark. Experimental stability labels and source-specific redistribution decisions still gate promotion into checked-in benchmark manifests.

The adjacent-form curation queue from `All_Psi_Crys.cif` contains 189 candidate pairs across 20 families. The all-pairs queue contains 1127 candidates and is useful for exploratory analysis, not initial v0.1 curation.

Single-structure backend smoke inference can be run without creating benchmark claims:

```powershell
python scripts\run_cposs_structure_inference.py --backend mace --limit 2
docker compose run --rm crystalprobe-core python scripts/run_cposs_structure_inference.py --backend mace --limit 1
```

The output is written under `outputs/`, which is ignored by git.

## OMC25

OMC25 is a large molecular-crystal DFT dataset for model development and OOD context, not the primary experimental stability benchmark.

- Hugging Face dataset: https://huggingface.co/datasets/facebook/OMC25
- FAIR Chemistry docs: https://fair-chem.github.io/molecules/datasets/omc25.html
- Scientific Data paper: https://www.nature.com/articles/s41597-026-06628-2

The data is described as CC-BY-4.0, but Hugging Face access approval may be required.

## CCDC/CSD Local Exports

CCDC/CSD exports are treated as local, license-controlled source files. Raw CIFs must remain under ignored `data/sources/ccdc/` and should not be redistributed through this repository.

Current local proof exports:

- Amphetamine-family bundle: `ccdc_amphetamine_phosphate_1036952-978407.cif`, selected block `AMPETP`, CCDC `1102740`.
- Ibuprofen bundle: `ccdc_ibuprofen_bundle_1041369-776185.cif`, selected block `ibuprofen`, CCDC `774097`.

Use:

```powershell
python scripts\inspect_ccdc_cif.py data\sources\ccdc\ccdc_ibuprofen_bundle_1041369-776185.cif --json-out outputs\ccdc_ibuprofen_bundle_index.json
```

The checked-in record of these sources is `data/curation/ccdc_therapeutic_sources_v0.1.json`; derived measurements are logged in `docs/measurement_log.md`.

## Medication Source Acquisition

Medication-priority source discovery is split into two layers:

- `data/curation/source_discovery_targets_v0.1.json` records public identity and structure leads.
- `data/curation/source_acquisition_attempts_v0.1.json` records concrete download/access attempts and exact manual input still needed.

Current acquisition status:

- Modafinil: a local CCDC/CSD-derived CIF bundle is available at `data/sources/modafinil/1415719-969516.cif`; selected parent blocks are recorded in `data/curation/medication_cif_selection_v0.1.json`.
- Atomoxetine hydrochloride: a local CCDC/CSD-derived bundle is available at `data/sources/ccdc/1302784-1519130.cif`; CCDC `1519130` is the primary selected block.
- Methylphenidate hydrochloride: a local CCDC/CSD-derived bundle is available at `data/sources/ccdc/121320-2256172.cif`; CCDC `1453371` is the parent-salt priority block and analogue blocks remain role-labeled.

Use:

```powershell
python scripts\build_source_acquisition_report.py
python scripts\build_medication_cif_ingestion_report.py --extract
python scripts\build_medication_research_bundle.py
```

The current selected medication proof blocks have local MACE, AIMNet2, and UMA measurements. Do not use medication analogue CIFs as parent-medication benchmark proof, and do not redistribute CCDC/CSD-derived coordinates without an explicit license decision.

## MACE-OFF

MACE-OFF23 is exposed through the MACE ASE calculator.

- Foundation model docs: https://mace-docs.readthedocs.io/en/latest/guide/foundation_models.html
- ASE calculator docs: https://mace-docs.readthedocs.io/en/latest/guide/ase.html

Checkpoint licensing is not the same as this repository license; verify before packaging workflows around downloaded models.

## fairchem, UMA, and FastCSP

fairchem is the current integration point for Meta FAIR Chemistry models and molecular-crystal tasks.

- GitHub: https://github.com/facebookresearch/fairchem
- OMC25 model page: https://huggingface.co/facebook/OMC25
- OMC25 dataset page: https://huggingface.co/datasets/facebook/OMC25
- UMA model page: https://huggingface.co/facebook/UMA
- OMAT24 model page: https://huggingface.co/facebook/OMAT24
- OMol25 model page: https://huggingface.co/facebook/OMol25

Local access is accepted for OMC25, UMA, OMAT24, and OMol25. The verification note is `docs/facebook_model_access.md`, with machine-readable details in `data/curation/facebook_model_access_v0.1.json`.

UMA and OMat24-trained model energies must not be mixed directly with Materials Project reference energies or MP2020 corrections. Use the OMat24-specific reference and correction assets for OMat24 thermodynamic work.
