# Measurement Log

This log records source-level CrystalProbe measurements that are useful for steering curation. These are not benchmark ranking claims until experimental stability labels are verified.

## 2026-05-03: Therapeutic Priority Source Measurements

Backend: MACE-OFF23 small through the CrystalProbe `MACEOffAdapter`.

Source: CPOSS209 `All_Psi_Crys.cif`.

### Ibuprofen (`IBP`)

Command:

```powershell
python scripts\run_cposs_structure_inference.py --backend mace --family IBP --output outputs\cposs_ibp_mace.jsonl
python scripts\summarize_structure_predictions.py outputs\cposs_ibp_mace.jsonl --json-out outputs\cposs_ibp_mace_summary.json
```

Result:

- Completed 7 of 7 structures.
- Common CPOSS structural unit inferred from formulas: `C26H36O4`.
- Lowest normalized MACE structure: `IBP01_PsiCrys`.
- Next structure: `IBP06_PsiCrys`, `1.28 kJ/mol` above `IBP01_PsiCrys` per common structural unit.
- Highest measured relative structure: `IBP03_PsiCrys`, `45.27 kJ/mol` above `IBP01_PsiCrys` per common structural unit.
- Local diagnostics: most IBP structures trigger `high_force_atom`; top force hot spots localize on oxygen atoms. No severe short-contact flags were reported by the covalent-radius contact screen.
- Leading bond-geometry outliers are O-C distances in the carboxylate/carbonyl region, with covalent-radius ratios around `0.87`.

### Carbamazepine (`CBZ`)

Command:

```powershell
python scripts\run_cposs_structure_inference.py --backend mace --family CBZ --output outputs\cposs_cbz_mace.jsonl
python scripts\summarize_structure_predictions.py outputs\cposs_cbz_mace.jsonl --json-out outputs\cposs_cbz_mace_summary.json
```

Result:

- Completed 9 of 9 structures.
- Common CPOSS structural unit inferred from formulas: `C30H24N4O2`.
- Lowest normalized MACE structure: `CBZ01_PsiCrys`.
- Next structure: `CBZ03_PsiCrys`, `2.23 kJ/mol` above `CBZ01_PsiCrys` per common structural unit.
- Highest measured relative structure: `CBZ08_PsiCrys`, `28.74 kJ/mol` above `CBZ01_PsiCrys` per common structural unit.
- Local diagnostics: all measured CBZ structures trigger `high_force_atom`; top force hot spots are mostly carbon atoms in the current atom indexing. No severe short-contact flags were reported.
- Leading bond-geometry outliers are C-O distances, with covalent-radius ratios around `0.88`.

## Interpretation Guardrails

- These measurements are useful for backend behavior and curation triage.
- They are not experimental stability rankings.
- Total crystal energies must be normalized before comparing structures with different cell contents.
- Local bond/contact/force diagnostics should be inspected before attributing an energy gap to molecular identity.
- Any publication-facing ranking number still requires verified form labels and experimental stability evidence.

## 2026-05-03: Local CCDC Crystal Measurements

Source files are local CCDC/CSD exports under ignored `data/sources/ccdc/`. Raw coordinates are not redistributed in git.

The source-ingestion path now measures selected blocks directly from multi-block CCDC CIF exports using `--cif-block`. Inspection reports are written to:

- `outputs/ccdc_amphetamine_bundle_index.json`
- `outputs/ccdc_ibuprofen_bundle_index.json`

### Amphetamine Dihydrogen Phosphate (`AMPETP`, CCDC 1102740)

Selected block: `AMPETP`.

Identity:

- Systematic name: `(+)-Amphetamine dihydrogen phosphate`.
- Formula moiety: `C9 H14 N1 1+,H2 O4 P1 1-`.
- ASE-read crystal formula: `C18H32N2O8P2`.
- Atoms: `62`.
- PBC: `true,true,true`.

Commands:

```powershell
python scripts\run_structure_inference.py data\sources\ccdc\ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend mace --output outputs\ccdc_ampetp_mace.json
python scripts\run_structure_inference.py data\sources\ccdc\ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend aimnet2 --output outputs\ccdc_ampetp_aimnet2.json
```

Result:

- MACE-OFF23 small energy: `-57155.287154708 eV`.
- MACE max force: `13.700041629526446 eV/Ang`; mean force: `4.960498200876906 eV/Ang`.
- AIMNet2 energy: `-57100.65066873132 eV`.
- AIMNet2 max force: `16.209012494432024 eV/Ang`; mean force: `5.491289741943641 eV/Ang`.
- Bond diagnostics: `60` covalent-radius candidate bonds.
- Shared local flag: `high_force_atom`.
- Leading geometric bond outlier: O-H at `0.8030833515834079 Ang`, covalent-radius ratio `0.8279209810138226`.
- Severe short contacts: none reported.

This is amphetamine-family crystal evidence, not lisdexamfetamine dimesylate evidence.

### AMPETP UMA Reference Measurement

Command:

```powershell
docker compose run --rm crystalprobe-fairchem python scripts/run_structure_inference.py data/sources/ccdc/ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend uma --output outputs/ccdc_ampetp_uma.json
```

Result:

- UMA checkpoint alias: `uma-s-1p2`.
- Task name: `omc`.
- Device: `cuda`.
- Energy: `-363.8153716439631 eV`.
- Max force: `17.192061172123992 eV/Ang`; mean force: `5.299576569577903 eV/Ang`.
- Bond diagnostics: `60` covalent-radius candidate bonds.
- Diagnostic flags: `high_force_atom`.
- Severe short contacts: none reported.

Interpretation: UMA now works as a third AMPETP backend reference in the Docker/fairchem environment. Its absolute energy scale must not be compared directly to MACE or AIMNet2 as a physical stability gap.

### AMPETP Perturbation Sensitivity

Command:

```powershell
python scripts\build_ampetp_sensitivity_set.py
python scripts\run_sensitivity_inference.py outputs\ampetp_sensitivity_manifest.json --backend mace --output outputs\ampetp_sensitivity_mace.jsonl
python scripts\run_sensitivity_inference.py outputs\ampetp_sensitivity_manifest.json --backend aimnet2 --output outputs\ampetp_sensitivity_aimnet2.jsonl --continue-on-error
docker compose run --rm crystalprobe-fairchem python scripts/run_sensitivity_inference.py outputs/ampetp_sensitivity_manifest.json --backend uma --output outputs/ampetp_sensitivity_uma.jsonl --continue-on-error
python scripts\summarize_sensitivity_predictions.py outputs\ampetp_sensitivity_mace.jsonl outputs\ampetp_sensitivity_aimnet2.jsonl outputs\ampetp_sensitivity_uma.jsonl --json-out outputs\ampetp_sensitivity_summary.json --md-out outputs\ampetp_sensitivity_summary.md
```

Result:

- Generated 6 deterministic perturbation probes: reference, two coordinate-noise variants, two cell-scale variants, and one combined cell-scale plus coordinate-noise variant.
- MACE-OFF23 small completed 6 of 6 probes.
- AIMNet2 completed 6 of 6 probes locally with `needs_dispersion=False`.
- UMA `uma-s-1p2` completed 6 of 6 probes in the Docker/fairchem CUDA environment.
- MACE maximum absolute energy delta relative to its own reference: `6.103903788149182 eV`.
- AIMNet2 maximum absolute energy delta relative to its own reference: `5.327166408751509 eV`.
- UMA maximum absolute energy delta relative to its own reference: `5.916418284348879 eV`.
- The largest-response variant for all three backends was `pos_sigma_0p03_seed_1`.
- All three backends flagged that largest-response variant with `short_contact` and `high_force_atom`.

Interpretation: this is a sensitivity-probe result, not a polymorph ranking. Energy deltas are within-backend deltas relative to each backend's own reference prediction.

### Ibuprofen (`ibuprofen`, CCDC 774097)

Selected block: `ibuprofen`.

Identity:

- Common name: `ibuprofen`.
- Formula: `C13 H18 O2`.
- ASE-read crystal formula: `C52H72O8`.
- Atoms: `132`.
- PBC: `true,true,true`.

Commands:

```powershell
python scripts\run_structure_inference.py data\sources\ccdc\ccdc_ibuprofen_bundle_1041369-776185.cif --cif-block ibuprofen --structure-id ccdc_774097_ibuprofen --backend mace --output outputs\ccdc_ibuprofen_774097_mace.json
docker compose run --rm crystalprobe-core python scripts/run_structure_inference.py data/sources/ccdc/ccdc_ibuprofen_bundle_1041369-776185.cif --cif-block ibuprofen --structure-id ccdc_774097_ibuprofen --backend aimnet2 --output outputs/ccdc_ibuprofen_774097_aimnet2_linux.json
```

Result:

- MACE-OFF23 small energy: `-71492.39595945076 eV`.
- MACE max force: `9.67071040963126 eV/Ang`; mean force: `4.717689571590105 eV/Ang`.
- AIMNet2 Linux energy: `-71408.09825360133 eV`.
- AIMNet2 Linux max force: `13.707494859673373 eV/Ang`; mean force: `5.027964111771895 eV/Ang`.
- Bond diagnostics: `132` covalent-radius candidate bonds.
- Shared local flag: `high_force_atom`.
- Leading geometric bond outlier: C-O at `1.2112225125261484 Ang`, covalent-radius ratio `0.852973600370527`.
- Severe short contacts: none reported.

The AIMNet2 ibuprofen run was executed in the Linux Docker core environment to avoid the Windows Torch/Triton backend issue.

### Ibuprofen Perturbation Sensitivity

Command:

```powershell
python scripts\build_ccdc_sensitivity_set.py data\sources\ccdc\ccdc_ibuprofen_bundle_1041369-776185.cif --block-id ibuprofen --title "Ibuprofen CCDC 774097 deterministic perturbation sensitivity set" --output-dir outputs\ibuprofen_sensitivity --manifest outputs\ibuprofen_sensitivity_manifest.json
python scripts\run_sensitivity_inference.py outputs\ibuprofen_sensitivity_manifest.json --backend mace --output outputs\ibuprofen_sensitivity_mace.jsonl
python scripts\summarize_sensitivity_predictions.py outputs\ibuprofen_sensitivity_mace.jsonl --json-out outputs\ibuprofen_sensitivity_summary_mace.json --md-out outputs\ibuprofen_sensitivity_summary_mace.md --title "Ibuprofen CCDC 774097 MACE perturbation sensitivity summary"
docker compose run --rm crystalprobe-core python scripts/run_sensitivity_inference.py outputs/ibuprofen_sensitivity_manifest.json --backend aimnet2 --output outputs/ibuprofen_sensitivity_aimnet2_linux.jsonl --continue-on-error
python scripts\summarize_sensitivity_predictions.py outputs\ibuprofen_sensitivity_aimnet2_linux.jsonl --json-out outputs\ibuprofen_sensitivity_summary_aimnet2_linux.json --md-out outputs\ibuprofen_sensitivity_summary_aimnet2_linux.md --title "Ibuprofen CCDC 774097 AIMNet2 Linux perturbation sensitivity summary"
python scripts\build_sensitivity_contrast_report.py --ibuprofen outputs\ibuprofen_sensitivity_summary_aimnet2_linux.json --backend aimnet2 --json-out outputs\therapeutic_sensitivity_contrast_aimnet2_linux.json --md-out outputs\therapeutic_sensitivity_contrast_aimnet2_linux.md
docker compose run --rm crystalprobe-fairchem python scripts/run_sensitivity_inference.py outputs/ibuprofen_sensitivity_manifest.json --backend uma --output outputs/ibuprofen_sensitivity_uma.jsonl --continue-on-error
python scripts\summarize_sensitivity_predictions.py outputs\ibuprofen_sensitivity_uma.jsonl --json-out outputs\ibuprofen_sensitivity_summary_uma.json --md-out outputs\ibuprofen_sensitivity_summary_uma.md --title "Ibuprofen CCDC 774097 UMA perturbation sensitivity summary"
python scripts\build_sensitivity_contrast_report.py --ibuprofen outputs\ibuprofen_sensitivity_summary_uma.json --backend uma --json-out outputs\therapeutic_sensitivity_contrast_uma.json --md-out outputs\therapeutic_sensitivity_contrast_uma.md
```

Result:

- Generated 6 deterministic perturbation probes for ibuprofen CCDC 774097.
- MACE-OFF23 small completed 6 of 6 probes locally.
- AIMNet2 completed 6 of 6 probes in the Docker core CUDA environment.
- UMA `uma-s-1p2` completed 6 of 6 probes in the Docker/fairchem CUDA environment.
- MACE maximum absolute energy delta relative to its own reference: `8.757581262339954 eV`.
- MACE mean absolute energy delta relative to its own reference: `3.08479521132831 eV`.
- AIMNet2 maximum absolute energy delta relative to its own reference: `6.826863078574068 eV`.
- AIMNet2 mean absolute energy delta relative to its own reference: `2.5049964639202766 eV`.
- UMA maximum absolute energy delta relative to its own reference: `8.672648645601143 eV`.
- UMA mean absolute energy delta relative to its own reference: `3.2832498728584766 eV`.
- Largest-response variant for MACE, AIMNet2, and UMA: `pos_sigma_0p03_seed_1`.
- Diagnostic flags on the largest-response variant: `high_force_atom`.
- AIMNet2 therapeutic contrast report now covers AMPETP and ibuprofen. AMPETP has maximum absolute AIMNet2 delta `5.327166408751509 eV` and flags `short_contact, high_force_atom`; ibuprofen has maximum absolute AIMNet2 delta `6.826863078574068 eV` and flags `high_force_atom`.
- UMA therapeutic contrast report now covers AMPETP and ibuprofen. AMPETP has maximum absolute UMA delta `5.916418284348879 eV` and flags `short_contact, high_force_atom`; ibuprofen has maximum absolute UMA delta `8.672648645601143 eV` and flags `high_force_atom`.

Interpretation: ibuprofen gives a neutral therapeutic contrast for the AMPETP sensitivity workflow. The same coordinate-noise probe is the strongest MACE, AIMNet2, and UMA response, but unlike AMPETP it did not trigger a `short_contact` flag in the local MACE run, Docker AIMNet2 run, or Docker UMA run.

## 2026-05-03: Lisdexamfetamine Parent Conformer

Target: lisdexamfetamine parent conformer from PubChem CID `11597698`.

Source file: `data/sources/pubchem/lisdexamfetamine_11597698_3d.sdf`.

This is a molecule-level diagnostic measurement. It is not a dimesylate crystal-packing measurement.

### MACE-OFF23 Small

Command:

```powershell
python scripts\run_structure_inference.py data\sources\pubchem\lisdexamfetamine_11597698_3d.sdf --structure-id lisdexamfetamine_parent_pubchem_11597698 --backend mace --output outputs\lisdexamfetamine_parent_mace.json
```

Result:

- Formula: `C15H25N3O`.
- Atoms: 44.
- Energy: `-22496.379770707095 eV`.
- Max force: `1.3198525597858526 eV/Ang`.
- Diagnostic flags: `high_force_atom`.
- Top force hotspot: atom `0`, oxygen, `1.3198525597858526 eV/Ang`.
- Top bond-geometry outlier: O-C, `1.2294253495027667 Ang`, covalent-radius ratio `0.8657924996498357`.
- Severe short contacts: none reported.

### AIMNet2

Command:

```powershell
python scripts\run_structure_inference.py data\sources\pubchem\lisdexamfetamine_11597698_3d.sdf --structure-id lisdexamfetamine_parent_pubchem_11597698 --backend aimnet2 --output outputs\lisdexamfetamine_parent_aimnet2.json
```

Result:

- Formula: `C15H25N3O`.
- Atoms: 44.
- Energy: `-22494.29040775406 eV`.
- Max force: `1.247026870117706 eV/Ang`.
- Diagnostic flags: `high_force_atom`.
- Top force hotspot: atom `0`, oxygen, `1.247026870117706 eV/Ang`.
- Top bond-geometry outlier: O-C, `1.2294253495027667 Ang`, covalent-radius ratio `0.8657924996498357`.
- Severe short contacts: none reported.

### Interpretation

Both backends identify the same local region as the main diagnostic hotspot: the amide/carbonyl O-C environment in the parent conformer. This is exactly the kind of local agreement we want before moving to the dimesylate crystal. The current blocker remains coordinate access for the crystalline dimesylate salt.

## 2026-05-04: High-Priority CPOSS Candidate Multi-Backend Measurements

Source: CPOSS209 `All_Psi_Crys.cif`.

Targets:

- Ibuprofen adjacent pair: `IBP01_PsiCrys` and `IBP06_PsiCrys`.
- Carbamazepine adjacent pair: `CBZ01_PsiCrys` and `CBZ03_PsiCrys`.

Commands:

```powershell
docker compose run --rm crystalprobe-core python scripts/run_cposs_structure_inference.py --backend mace --block-id IBP01_PsiCrys --block-id IBP06_PsiCrys --block-id CBZ01_PsiCrys --block-id CBZ03_PsiCrys --output outputs/cposs_candidates_high_priority_mace.jsonl --continue-on-error
docker compose run --rm crystalprobe-core python scripts/run_cposs_structure_inference.py --backend aimnet2 --block-id IBP01_PsiCrys --block-id IBP06_PsiCrys --block-id CBZ01_PsiCrys --block-id CBZ03_PsiCrys --output outputs/cposs_candidates_high_priority_aimnet2.jsonl --continue-on-error
docker compose run --rm crystalprobe-fairchem python scripts/run_cposs_structure_inference.py --backend uma --block-id IBP01_PsiCrys --block-id IBP06_PsiCrys --block-id CBZ01_PsiCrys --block-id CBZ03_PsiCrys --output outputs/cposs_candidates_high_priority_uma.jsonl --continue-on-error
python scripts\build_cposs_backend_disagreement_report.py
python scripts\build_uncertainty_proxy_report.py
```

Result:

- MACE, AIMNet2, and UMA each completed 4 of 4 high-priority CPOSS structures.
- The backend-disagreement report is written to `outputs/cposs_high_priority_backend_disagreement.json` and `outputs/cposs_high_priority_backend_disagreement.md`.
- Ibuprofen has cross-backend ordering consensus: all three backends place `IBP01_PsiCrys` below `IBP06_PsiCrys` after common structural-unit normalization.
- Carbamazepine has a true backend-ordering disagreement: MACE and AIMNet2 place `CBZ01_PsiCrys` below `CBZ03_PsiCrys`, while UMA places `CBZ03_PsiCrys` below `CBZ01_PsiCrys`.
- Diagnostic-flag agreement is also incomplete: UMA does not reproduce the high-force flags reported by MACE and AIMNet2 on this high-priority subset.
- The uncertainty proxy v0 marks the CPOSS report for inspection while keeping the AMPETP sensitivity disagreement report in the high-confidence behavioral category.

Interpretation: this is the first intentionally found CPOSS backend disagreement in the suite. It is backend-behavior evidence for inspection and case selection, not an experimental polymorph stability claim.
