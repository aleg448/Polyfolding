# CrystalProbe Tentative Molecule Benchmark

- Status: `tentative_molecule_benchmark_recorded`
- Molecules: `85`
- Tool rows: `260`
- Passed rows: `253`
- Failed rows: `0`
- Blocked rows: `2`
- Warning rows: `2`
- Claim-ready rows: `0`
- Generated conformers: `83`
- Candidate payload enabled: `True`
- Claim boundary: `tentative_software_benchmark_not_scientific_evidence`

## Source Sets

| Source set | Molecules |
|---|---:|
| `molecule_bug_hunt_stress_v0.1` | `37` |
| `synthetic_software_fixture` | `48` |

## Tool Summary

| Tool | Rows |
|---|---:|
| `aimnet2` | `1` |
| `ase_cif` | `1` |
| `fastcsp` | `1` |
| `mace_off` | `1` |
| `rdkit_conformer` | `85` |
| `rdkit_smiles` | `85` |
| `smiles_lexical` | `85` |
| `uma` | `1` |

## Bug Signatures

| Signature | Severity | Count | Examples | Detail |
|---|---|---:|---|---|
| `backend_execution_not_requested` | `skipped` | `3` | aimnet2, ase_cif, mace_off | aimnet2 is importable and 83 generated conformer inputs are available; backend execution is intentionally not run by this tentative benchmark. |
| `optional_backend_missing_dependency` | `blocked` | `2` | fastcsp, uma | fastcsp unavailable: missing Python module(s): fairchem. Clone/install facebookresearch/fairchem with FastCSP extras. |
| `rdkit_uff_not_converged` | `warning` | `2` | cholesterol, peg_long_fragment | Conformer generated, but UFFOptimizeMolecule returned code 1. |

## Sample Benchmark Rows

| Molecule | Tool | Status | Signature | Detail |
|---|---|---|---|---|
| `water` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `carbon_dioxide` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `benzene` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `pyridine` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `phenol` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `ethanol` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `acetic_acid` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `dimethyl_sulfoxide` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `urea` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `glycine_neutral` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `glycine_zwitterion` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `l_alanine` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `lactic_acid` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `betaine` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `sodium_chloride` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `methylammonium_chloride` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `choline_chloride` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `imidazole` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `acetylacetone` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `naphthalene` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `anthracene` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `polyethylene_glycol_fragment` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `caffeine` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `caffeine_monohydrate_fixture` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `aspirin` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `paracetamol` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `ibuprofen` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `naproxen` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `carbamazepine` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |
| `nicotinamide` | `smiles_lexical` | `passed` | `none` | Lexical SMILES checks passed. |

## Policy

- This is a tentative software benchmark, not a scientific validation benchmark.
- Rows may show parser, dependency, or input-readiness failures; those are bug-hunt signals.
- RDKit conformer generation is used when available, but generated conformers are software inputs, not experimental structures.
- Optional scientific backends are preflighted, but conformer-ready rows do not prove MLIP execution.
- No molecule-panel row can support stability, formulation, or drug-discovery claims.
- A verified calibration slice is still required before headline benchmark claims.
