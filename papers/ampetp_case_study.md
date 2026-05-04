# AMPETP as a Pilot CrystalProbe Case Study

## Working Title

CrystalProbe pilot: cross-MLIP diagnostic agreement on the CCDC AMPETP amphetamine phosphate crystal

## Status

Preliminary research memo. This is not yet a full polymorph-ranking paper because AMPETP is a single crystal structure, not a verified pair of polymorphs with experimental relative stability. Its role is to prove the source-ingestion, backend-measurement, local-diagnostic, and reproducibility layers that the full CrystalProbe roadmap requires.

## Abstract Draft

Machine-learned interatomic potentials are increasingly used for organic crystal modelling, but practical workflows still need explicit evidence trails that show when a prediction should be trusted. We present an initial CrystalProbe pilot on the CCDC AMPETP structure, `(+)-amphetamine dihydrogen phosphate` (CCDC 1102740), selected as a medication-adjacent charged organic salt. CrystalProbe extracts the AMPETP block from a local multi-block CCDC CIF export, measures the periodic crystal with MACE-OFF23 small and AIMNet2, and produces backend-agreement diagnostics over energies, forces, geometric bond outliers, and severe short contacts. Both backends complete inference on the same `C18H32N2O8P2` periodic cell, agree on the presence of a high-force local diagnostic, report no severe short-contact flags, and identify the same top five bond-geometry outliers. The leading shared geometric outlier is an O-H contact at `0.8030833515834079 Ang` with covalent-radius ratio `0.8279209810138226`. The top-force atom overlap across backends has Jaccard agreement `0.667`, while top bond-outlier agreement is `1.000`. We treat cross-backend absolute energy spread as a provenance diagnostic rather than as a physical stability gap. This pilot establishes the minimal research-grade vertical slice for CrystalProbe: licensed-source separation, reproducible block extraction, backend execution, local bond/force diagnostics, and paper-ready reporting.

## Rationale

The full CrystalProbe plan targets polymorph-pair benchmarking, behavioural fingerprinting of MLIPs, uncertainty-aware wrappers, and FastCSP usability. A credible early paper needs a smaller proof object that is real, reproducible, and honest about scope. AMPETP is suitable for this role because it is:

- A real CCDC/CSD crystal export rather than a toy molecule.
- A charged organic salt, which is harder and more relevant than a neutral gas-phase conformer.
- Medication-adjacent to the amphetamine-family target class the project cares about.
- Small enough for repeated local and Docker inference runs.

AMPETP is not lisdexamfetamine dimesylate and should not be described as proof for that API. It is the validated pilot crystal for the research suite.

## Source and Reproducibility

Source record:

- CCDC deposition: `CCDC 1102740`.
- CSD refcode: `AMPETP`.
- Name: `(+)-Amphetamine dihydrogen phosphate`.
- Formula moiety: `C9 H14 N1 1+,H2 O4 P1 1-`.
- Space group: `P 21`.
- Local source path: `data/sources/ccdc/ccdc_amphetamine_phosphate_1036952-978407.cif`.
- Local source SHA-256: `9d8692b5f8921c6f1493b49960c766c6629721d9e8ffd4e0c085025dc56c6018`.

Raw CCDC coordinates remain local and ignored by git. The repository records metadata, commands, and derived measurements only.

Rebuild commands:

```powershell
python scripts\inspect_ccdc_cif.py data\sources\ccdc\ccdc_amphetamine_phosphate_1036952-978407.cif --json-out outputs\ccdc_amphetamine_bundle_index.json --extract-block AMPETP --extract-out outputs\ccdc_ampetp_extracted.cif
python scripts\run_structure_inference.py data\sources\ccdc\ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend mace --output outputs\ccdc_ampetp_mace.json
python scripts\run_structure_inference.py data\sources\ccdc\ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend aimnet2 --output outputs\ccdc_ampetp_aimnet2.json
python scripts\build_ampetp_case_study.py
python scripts\build_ampetp_sensitivity_set.py
python scripts\run_sensitivity_inference.py outputs\ampetp_sensitivity_manifest.json --backend mace --output outputs\ampetp_sensitivity_mace.jsonl
python scripts\run_sensitivity_inference.py outputs\ampetp_sensitivity_manifest.json --backend aimnet2 --output outputs\ampetp_sensitivity_aimnet2.jsonl --continue-on-error
python scripts\summarize_sensitivity_predictions.py outputs\ampetp_sensitivity_mace.jsonl outputs\ampetp_sensitivity_aimnet2.jsonl --json-out outputs\ampetp_sensitivity_summary.json --md-out outputs\ampetp_sensitivity_summary.md
python scripts\build_ampetp_figures.py
python scripts\build_ampetp_research_bundle.py
```

Research-bundle manifest:

- JSON: `outputs/ampetp_research_bundle_manifest.json`.
- Markdown: `outputs/ampetp_research_bundle_manifest.md`.
- Current manifest SHA-256: `fbba43d534e62cf7d9cfbe32d75c27bc5b52345cb6ff2ed7113defa3613b00d2`.
- Artifact count: `15`.

Readiness report:

- JSON: `outputs/ampetp_readiness_report.json`.
- Markdown: `outputs/ampetp_readiness_report.md`.
- Status: `paper_pilot_ready`.
- Checks: `8` passed, `0` failed.

CPOSS bridge report:

- JSON: `outputs/cposs_mini_benchmark_report.json`.
- Markdown: `outputs/cposs_mini_benchmark_report.md`.
- Current scope: `2` CPOSS families, `16` structures.
- Families: ibuprofen (`IBP`) and carbamazepine (`CBZ`).

## Methods Draft

The source export is first split into individual CIF data blocks with `crystalprobe.datahub.ccdc.split_ccdc_cif`. The selected `AMPETP` block is extracted and lightly sanitized for common CSD space-group spellings before ASE reads the periodic structure. MACE-OFF23 small and AIMNet2 are executed through CrystalProbe optional adapters. Each prediction records backend metadata, total energy, force summary, periodic boundary flags, and local geometry diagnostics.

Local geometry diagnostics use covalent-radius-scaled distances to identify candidate bonds, leading geometric outliers, and severe short contacts. Force diagnostics rank atoms by force norm. These diagnostics are intended to identify local regions that deserve inspection. They are not a unique decomposition of MLIP energy into individual bond energies.

The case-study report compares backend outputs for the same structure. Agreement metrics include shared diagnostic flags, Jaccard overlap of top force-hotspot atoms, Jaccard overlap of top bond-geometry outliers, and severe short-contact agreement. The absolute energy spread between MACE-OFF and AIMNet2 is recorded for provenance but is not interpreted as a thermodynamic quantity because different MLIPs can use different reference conventions.

Perturbation sensitivity is prepared as a deterministic generated structure set. The set includes the unmodified AMPETP reference, two coordinate-noise variants, two cell-scaling variants, and one combined cell-scaling plus coordinate-noise variant. These CIFs are generated under `outputs/ampetp_sensitivity/` and indexed by `outputs/ampetp_sensitivity_manifest.json`. They are not experimentally observed forms; they are probes for later backend sensitivity analysis.

To connect the single-structure AMPETP pilot to the polymorph-ranking roadmap, CrystalProbe also summarizes existing CPOSS local MACE measurements for ibuprofen (`IBP`) and carbamazepine (`CBZ`). This bridge report normalizes energies by inferred formula unit within each family and records local diagnostic flag rates. It is not yet a curated experimental stability benchmark.

## Results Draft

Both MACE-OFF23 small and AIMNet2 completed inference on the extracted AMPETP periodic crystal. ASE reads the cell as formula `C18H32N2O8P2`, `62` atoms, with periodic boundary conditions in all three directions.

| Backend | Energy (eV) | Max force (eV/Ang) | Mean force (eV/Ang) | Bonds | Flags |
|---|---:|---:|---:|---:|---|
| MACE-OFF23 small | -57155.287155 | 13.700042 | 4.960498 | 60 | high_force_atom |
| AIMNet2 | -57100.650669 | 16.209012 | 5.491290 | 60 | high_force_atom |

Agreement diagnostics:

- Energy range across backends: `54.636486 eV`, recorded only as cross-backend spread.
- Top-force atom Jaccard agreement: `0.667`.
- Top bond-outlier Jaccard agreement: `1.000`.
- Shared diagnostic flag: `high_force_atom`.
- Severe short contacts: none reported by either backend.

The top bond-geometry outlier is identical across backends because it is computed from the input structure: O-H at `0.8030833515834079 Ang`, covalent-radius ratio `0.8279209810138226`, strain score `0.18883756270913438`. The force-hotspot overlap indicates that both models focus on overlapping local regions while still differing in the exact force ranking, which is the expected type of signal for later behavioural-fingerprint work.

## Perturbation Sensitivity Results

CrystalProbe generates a six-structure AMPETP sensitivity set:

| Variant | RMS position delta (Ang) | Max position delta (Ang) | Cell Frobenius delta (Ang) |
|---|---:|---:|---:|
| reference | 0.000000 | 0.000000 | 0.000000 |
| pos_sigma_0p01_seed_1 | 0.016659 | 0.029375 | 0.000000 |
| pos_sigma_0p03_seed_1 | 0.049976 | 0.088126 | 0.000000 |
| cell_scale_0p995 | 0.043430 | 0.066762 | 0.081945 |
| cell_scale_1p005 | 0.043430 | 0.066762 | 0.081945 |
| cell_scale_1p005_pos_sigma_0p01_seed_2 | 0.043582 | 0.065993 | 0.081945 |

MACE-OFF23 small and AIMNet2 both completed inference across this perturbation set.

| Backend | Max abs energy delta (eV) | Mean abs energy delta (eV) | Largest-response variant | Largest-response flags |
|---|---:|---:|---|---|
| MACE-OFF23 small | 6.103904 | 1.859283 | pos_sigma_0p03_seed_1 | short_contact, high_force_atom |
| AIMNet2 | 5.327166 | 1.627483 | pos_sigma_0p03_seed_1 | short_contact, high_force_atom |

The strongest response for both backends is the `0.03 Ang` coordinate-noise variant. Both backends also add a `short_contact` diagnostic flag for that variant while retaining `high_force_atom`. This is the first concrete sensitivity result: when deterministic coordinate noise pushes AMPETP into a locally implausible geometry, both independent MLIPs and the local geometry screen identify the same perturbation as the most unstable probe in the grid.

## CPOSS Bridge Mini-Benchmark

The local CPOSS bridge report currently covers two therapeutic-relevant families:

| Family | Formula unit | Structures | Lowest MACE structure | Second structure | Second gap (kJ/mol) | Energy span (kJ/mol) | Flagged fraction |
|---|---|---:|---|---|---:|---:|---:|
| CBZ | `C30H24N4O2` | 9 | CBZ01_PsiCrys | CBZ03_PsiCrys | 2.232 | 28.743 | 1.000 |
| IBP | `C26H36O4` | 7 | IBP01_PsiCrys | IBP06_PsiCrys | 1.277 | 45.269 | 0.857 |

This report supplies the immediate route from AMPETP's single-crystal diagnostic workflow to the full benchmark objective: normalized within-family ranking, chemistry-specific slicing, and local diagnostic review before headline stability claims.

## Neutral Contrast: Ibuprofen Sensitivity

The same deterministic CCDC sensitivity workflow has now been applied to ibuprofen CCDC 774097 as a neutral therapeutic contrast. The current contrast result is MACE-only locally:

| Target | Backend | Probes completed | Max abs delta (eV) | Mean abs delta (eV) | Largest-response variant | Largest-response flags |
|---|---|---:|---:|---:|---|---|
| AMPETP | MACE-OFF23 small | 6 | 6.103904 | 1.859283 | pos_sigma_0p03_seed_1 | short_contact, high_force_atom |
| Ibuprofen | MACE-OFF23 small | 6 | 8.757581 | 3.084795 | pos_sigma_0p03_seed_1 | high_force_atom |

The shared largest-response probe suggests that `0.03 Ang` coordinate noise is a useful stress test across charged and neutral therapeutic crystals. The contrast is also informative: AMPETP develops a `short_contact` flag under that perturbation, while the ibuprofen MACE run remains at `high_force_atom` only. AIMNet2 ibuprofen sensitivity remains a Linux/Docker follow-up.

Generated contrast report:

- JSON: `outputs/therapeutic_sensitivity_contrast_mace.json`.
- Markdown: `outputs/therapeutic_sensitivity_contrast_mace.md`.

## Claims We Can Make

- CrystalProbe can ingest a real local CCDC multi-block CIF export without committing raw coordinates.
- CrystalProbe can extract a selected CCDC block and run two independent MLIP backends on the same periodic crystal.
- CrystalProbe can report local bond/force diagnostics at the bond and atom level, not only molecule-level totals.
- CrystalProbe can generate deterministic perturbation probes for conformational and cell-scaling sensitivity studies.
- CrystalProbe can summarize local CPOSS multi-structure families as a bridge toward polymorph ranking work.
- CrystalProbe can reuse the same deterministic sensitivity protocol on a neutral therapeutic contrast crystal.
- AMPETP is a valid pilot for the research suite and a plausible first case-study figure in the fingerprint paper.

## Claims We Cannot Make Yet

- This is not a polymorph ranking.
- This is not an experimental stability benchmark.
- This is not lisdexamfetamine dimesylate.
- Cross-backend absolute energy spread is not a calibrated free-energy uncertainty.
- The current two-model agreement is a pilot signal, not a validated uncertainty calibration.
- The generated perturbation structures are probes, not real polymorphs or experimentally observed structures.
- Sensitivity energy deltas are relative to each backend's own reference prediction and should not be compared across backends as absolute thermodynamic quantities.
- The CPOSS bridge report is not yet a verified experimental stability benchmark.
- Ibuprofen sensitivity is currently MACE-only locally; AIMNet2 contrast still needs a Linux/Docker run.

## Figure Plan

Generated SVG figures:

1. `outputs/figures/ampetp_provenance_flow.svg`: CCDC multi-CIF export to extracted AMPETP block to backend outputs.
2. `outputs/figures/ampetp_structure_projection.svg`: deterministic 2D projection of the AMPETP cell and atom positions.
3. `outputs/figures/ampetp_backend_force_diagnostics.svg`: MACE-OFF23 and AIMNet2 force-diagnostic comparison.
4. `outputs/figures/ampetp_sensitivity_energy_deltas.svg`: signed within-backend energy deltas across coordinate-noise and cell-scaling probes.
5. `outputs/figures/ampetp_claim_guardrails.svg`: supported and blocked claim boundaries.

The structure projection is a documentation figure only. Quantitative crystallographic analysis should use the source CIF and ASE-readable structure, not the 2D projection.

## Next Experiments

1. Add a neutral therapeutic contrast case using the ibuprofen CCDC 774097 crystal already measured by the suite.
2. Promote the CPOSS bridge report into curated pair records with experimental stability evidence.
3. Add UMA once Hugging Face access is granted.
4. Run AIMNet2 on the ibuprofen sensitivity grid in Linux/Docker.
5. Promote the neutral contrast into the ChemRxiv-style draft once both backends are available.

## References To Use

- Kovacs et al., MACE-OFF, *Journal of the American Chemical Society*, 2025, DOI `10.1021/jacs.4c07099`.
- Anstine, Zubatyuk, and Isayev, AIMNet2, *Chemical Science*, 2025, DOI `10.1039/D4SC08572H`.
- Price, Paloni, Salvalaglio et al., CPOSS209, *Crystal Growth & Design*, 2025, DOI `10.1021/acs.cgd.5c00255`.
