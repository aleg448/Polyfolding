# CrystalProbe Molecule Bug Dashboard

- Status: `molecule_bug_dashboard_recorded`
- Molecules: `85`
- Claim-ready rows: `0`
- Claim boundary: `molecule_bug_dashboard_software_qa_not_scientific_evidence`

## Status Counts

| Surface | Counts |
|---|---|
| Parser | `passed`: `85` |
| Conformer | `ready`: `83`, `warning`: `2` |
| Backend | `failed`: `2`, `partial_backend_blocker`: `83` |
| Energy/force sanity | `blocked`: `2`, `passed`: `82`, `warning`: `1` |

## Issue Signatures

| Signature | Severity | Count | Examples | Detail |
|---|---|---:|---|---|
| `backend_execution_exception` | `failure` | `2` | sodium_acetate, sodium_chloride | A backend raised an execution exception on this generated input. |
| `backend_missing_windows_cpp_compiler` | `blocked` | `85` | acetate, acetic_acid, acetylacetone, adamantane, adenine, ammonia, ammonium, ammonium_nitrate | Backend execution reached AIMNet2/PyTorch Inductor, but the Windows C++ compiler `cl` was unavailable. |
| `max_force_above_smoke_threshold` | `warning` | `1` | ammonium_nitrate | A passed backend row returned a maximum force above the smoke sanity threshold. |
| `rdkit_uff_not_converged` | `warning` | `2` | cholesterol, peg_long_fragment | RDKit generated a conformer, but UFF optimization did not converge. |

## Molecule Rows

| Molecule | Parser | Conformer | Backend | Energy/Force | Issue |
|---|---|---|---|---|---|
| `acetate` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `acetic_acid` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `acetylacetone` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `adamantane` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `adenine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `ammonia` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `ammonium` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `ammonium_nitrate` | `passed` | `ready` | `partial_backend_blocker` | `warning` | `backend_missing_windows_cpp_compiler;max_force_above_smoke_threshold` |
| `aniline` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `anthracene` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `aspirin` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `benzene` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `benzocaine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `betaine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `butane` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `caffeine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `caffeine_monohydrate_fixture` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `carbamazepine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `carbon_dioxide` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `chloroform` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `cholesterol` | `passed` | `warning` | `partial_backend_blocker` | `passed` | `rdkit_uff_not_converged;backend_missing_windows_cpp_compiler` |
| `choline_chloride` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `cyclohexane` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `d_serine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `decane` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `dichloromethane` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `dimethyl_sulfoxide` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `dipeptide_gly_gly` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `ethane` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `ethanol` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `ethylamine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `ethylene_glycol` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `fluorobenzene` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `formic_acid` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `fumaric_acid` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `furan` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `glucose_open_chain` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `glucose_pyranose` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `glycerol` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `glycine_neutral` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `glycine_zwitterion` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `hexane` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `ibuprofen` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `imidazole` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `isopropanol` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `l_alanine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `l_serine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `lactic_acid` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `lidocaine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `maleic_acid` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `malonic_acid` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `menthol` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `metformin` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `methane` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `methanol` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `methylamine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `methylammonium_chloride` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `morpholine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `naphthalene` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `naproxen` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `nicotinamide` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `nicotinic_acid` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `oxalic_acid` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `paracetamol` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `peg_long_fragment` | `passed` | `warning` | `partial_backend_blocker` | `passed` | `rdkit_uff_not_converged;backend_missing_windows_cpp_compiler` |
| `phenol` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `piperidine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `polyethylene_glycol_fragment` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `propane` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `propanol` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `propionic_acid` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `pyridine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `pyrrole` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `sodium_acetate` | `passed` | `ready` | `failed` | `blocked` | `backend_execution_exception;backend_missing_windows_cpp_compiler` |
| `sodium_chloride` | `passed` | `ready` | `failed` | `blocked` | `backend_execution_exception;backend_missing_windows_cpp_compiler` |
| `succinic_acid` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `tartaric_acid` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `tetramethylammonium` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `theobromine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `thiophene` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `triethylamine` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `tripeptide_gly_gly_gly` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `uracil` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `urea` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |
| `water` | `passed` | `ready` | `partial_backend_blocker` | `passed` | `backend_missing_windows_cpp_compiler` |

## Policy

- This dashboard is a software QA artifact for parser, conformer, and backend readiness.
- A passed parser or backend smoke row does not make a molecule scientifically verified.
- Backend-not-run rows are explicit coverage gaps, not failed chemistry.
- Energy/force sanity checks only test finite outputs and coarse force thresholds on generated inputs.
