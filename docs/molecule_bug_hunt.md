# CrystalProbe Molecule Bug-Hunt Database

- Status: `molecule_bug_hunt_ready`
- Molecules: `37`

## Coverage Checks

| Check | Status | Detail |
|---|---|---|
| `charged_molecules` | `passed` | 5 charged rows |
| `salt_or_dot_components` | `passed` | dot components present |
| `stereochemistry` | `passed` | 4 chiral rows |
| `tautomer_cases` | `passed` | 2 tautomer rows |
| `large_or_fused_cases` | `passed` | 5 fused-ring rows |
| `duplicate_connectivity_cases` | `passed` | duplicate SMILES group present |
| `expected_bug_surface_diversity` | `passed` | 49 expected bug-surface labels |

## Molecules

| Molecule | SMILES | Tags | Bug Surfaces | Flags | Claim Boundary |
|---|---|---|---|---|---|
| water | `O` | tiny; hydrogen_bonding | tiny_formula; viewer_minimal_atoms | baseline | `software_stress_fixture_not_scientific_evidence` |
| carbon dioxide | `O=C=O` | tiny; linear | linear_geometry; no_hydrogen_atoms | baseline | `software_stress_fixture_not_scientific_evidence` |
| benzene | `c1ccccc1` | aromatic; rigid | aromatic_lowercase_atoms | baseline | `software_stress_fixture_not_scientific_evidence` |
| pyridine | `n1ccccc1` | aromatic; heteroaromatic | aromatic_heteroatom | baseline | `software_stress_fixture_not_scientific_evidence` |
| phenol | `Oc1ccccc1` | aromatic; hydrogen_bonding | phenol_hbond | baseline | `software_stress_fixture_not_scientific_evidence` |
| ethanol | `CCO` | small_flexible; hydrogen_bonding | rotatable_bond_minimal | baseline | `software_stress_fixture_not_scientific_evidence` |
| acetic acid | `CC(=O)O` | acid; hydrogen_bonding | carboxylic_acid | baseline | `software_stress_fixture_not_scientific_evidence` |
| dimethyl sulfoxide | `CS(=O)C` | sulfoxide; polar | sulfur_valence | baseline | `software_stress_fixture_not_scientific_evidence` |
| urea | `NC(N)=O` | hydrogen_bonding; rigid | multiple_donors_acceptors | baseline | `software_stress_fixture_not_scientific_evidence` |
| glycine neutral | `NCC(=O)O` | amino_acid; flexible | neutral_amino_acid | baseline | `software_stress_fixture_not_scientific_evidence` |
| glycine zwitterion | `[NH3+]CC(=O)[O-]` | amino_acid; zwitterion; charged | formal_charge; zwitterion | charged | `software_stress_fixture_not_scientific_evidence` |
| L-alanine | `C[C@H](N)C(=O)O` | amino_acid; chiral | stereochemistry | stereo | `software_stress_fixture_not_scientific_evidence` |
| lactic acid | `C[C@H](O)C(=O)O` | acid; chiral | stereochemistry; acid_alcohol | stereo | `software_stress_fixture_not_scientific_evidence` |
| betaine | `C[N+](C)(C)CC(=O)[O-]` | zwitterion; charged | quaternary_ammonium; zwitterion | charged | `software_stress_fixture_not_scientific_evidence` |
| sodium chloride | `[Na+].[Cl-]` | salt; inorganic; charged | dot_disconnected_components; metal_ion | dot-components, charged | `software_stress_fixture_not_scientific_evidence` |
| methylammonium chloride | `C[NH3+].[Cl-]` | salt; charged | dot_disconnected_components; protonated_amine | dot-components, charged | `software_stress_fixture_not_scientific_evidence` |
| choline chloride | `C[N+](C)(C)CCO.[Cl-]` | salt; charged; hydrogen_bonding | quaternary_ammonium; dot_disconnected_components | dot-components, charged | `software_stress_fixture_not_scientific_evidence` |
| imidazole | `c1ncc[nH]1` | heteroaromatic; tautomer | aromatic_nh; tautomer_annotation | baseline | `software_stress_fixture_not_scientific_evidence` |
| acetylacetone | `CC(=O)CC(=O)C` | tautomer; flexible | keto_enol_tautomer | baseline | `software_stress_fixture_not_scientific_evidence` |
| naphthalene | `c1ccc2ccccc2c1` | fused_ring; aromatic | fused_aromatic_ring | baseline | `software_stress_fixture_not_scientific_evidence` |
| anthracene | `c1ccc2cc3ccccc3cc2c1` | fused_ring; aromatic | larger_fused_aromatic_ring | baseline | `software_stress_fixture_not_scientific_evidence` |
| polyethylene glycol fragment | `OCCOCCOCCO` | flexible; polyether | many_rotatable_bonds; repeated_substructure | baseline | `software_stress_fixture_not_scientific_evidence` |
| caffeine | `Cn1cnc2c1c(=O)n(C)c(=O)n2C` | heteroaromatic; polyfunctional | fused_heterocycle; multiple_carbonyls | baseline | `software_stress_fixture_not_scientific_evidence` |
| caffeine monohydrate fixture | `Cn1cnc2c1c(=O)n(C)c(=O)n2C.O` | hydrate; dot_components | hydrate_component; dot_disconnected_components | dot-components | `software_stress_fixture_not_scientific_evidence` |
| aspirin | `CC(=O)Oc1ccccc1C(=O)O` | drug_like; acid; ester | manifest_overlap; acid_ester | baseline | `software_stress_fixture_not_scientific_evidence` |
| paracetamol | `CC(=O)Nc1ccc(O)cc1` | drug_like; amide; phenol | manifest_overlap; amide_phenol | baseline | `software_stress_fixture_not_scientific_evidence` |
| ibuprofen | `CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O` | drug_like; chiral; acid | stereochemistry; flexible_aryl_acid | stereo | `software_stress_fixture_not_scientific_evidence` |
| naproxen | `COc1ccc2cc(ccc2c1)[C@@H](C)C(=O)O` | drug_like; chiral; fused_ring | stereochemistry; fused_aromatic_drug_like | stereo | `software_stress_fixture_not_scientific_evidence` |
| carbamazepine | `NC(=O)N1C2=CC=CC=C2C=CC3=CC=CC=C31` | drug_like; amide; fused_ring | manifest_overlap; large_rigid_amide | baseline | `software_stress_fixture_not_scientific_evidence` |
| nicotinamide | `NC(=O)c1cccnc1` | coformer; amide; heteroaromatic | coformer_candidate; amide_heteroaromatic | baseline | `software_stress_fixture_not_scientific_evidence` |
| nicotinic acid | `O=C(O)c1cccnc1` | coformer; acid; heteroaromatic | coformer_candidate; acid_heteroaromatic | baseline | `software_stress_fixture_not_scientific_evidence` |
| benzocaine | `CCOC(=O)c1ccc(N)cc1` | drug_like; ester; amine | ester_amine; para_substitution | baseline | `software_stress_fixture_not_scientific_evidence` |
| lidocaine | `CCN(CC)CC(=O)Nc1c(C)cccc1C` | drug_like; flexible; amide; amine | tertiary_amine; flexible_drug_like | baseline | `software_stress_fixture_not_scientific_evidence` |
| maleic acid | `O=C(O)C=CC(=O)O` | coformer; diacid | multiple_acids; alkene | duplicate-connectivity | `software_stress_fixture_not_scientific_evidence` |
| fumaric acid | `O=C(O)C=CC(=O)O` | coformer; diacid; stereoisomer_alias | stereoisomer_requires_more_than_connectivity | duplicate-connectivity | `software_stress_fixture_not_scientific_evidence` |
| menthol | `CC(C)C1CCC(C(C1)O)C` | terpene; chiral_like; alcohol | stereochemistry_missing; aliphatic_ring | baseline | `software_stress_fixture_not_scientific_evidence` |
| cholesterol | `CC(C)CCCC(C)C1CCC2C3CCC4=CC(O)CCC4(C)C3CCC12C` | large; fused_ring; steroid | large_fused_ring; stereochemistry_missing | baseline | `software_stress_fixture_not_scientific_evidence` |

## Policy

- Stress molecules are for parser, database, visualization, and energy-layer QA only.
- SMILES strings in this file are bug-hunt fixtures, not source-verified molecular records.
- No record in this file can support a scientific stability, formulation, or drug-discovery claim.
- Coordinate-bearing payloads remain governed by source-specific release-boundary rules.
