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

## Interpretation Guardrails

- These measurements are useful for backend behavior and curation triage.
- They are not experimental stability rankings.
- Total crystal energies must be normalized before comparing structures with different cell contents.
- Any publication-facing ranking number still requires verified form labels and experimental stability evidence.
