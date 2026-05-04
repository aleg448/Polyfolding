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
