# CrystalProbe Backend-Ready Inputs

- Status: `backend_ready_inputs_recorded`
- Source report: `outputs\local_conformer_generation_with_xyz.json`
- Rows: `85`
- Ready rows: `83`
- Warning rows: `2`
- Blocked rows: `0`
- Claim-ready rows: `0`
- Claim boundary: `backend_ready_generated_conformer_input_not_scientific_evidence`

## Bug Signatures

| Signature | Severity | Count | Examples | Detail |
|---|---|---:|---|---|
| `rdkit_uff_not_converged` | `warning` | `2` | cholesterol, peg_long_fragment | Conformer generated, but UFFOptimizeMolecule returned code 1. |

## Input Rows

| Molecule | Status | Review | Atoms | XYZ | SHA-256 | Detail |
|---|---|---|---:|---|---|---|
| `water` | `ready` | `candidate_unverified` | `3` | `outputs/generated_conformers/water.xyz` | `e8195b5298a7` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `carbon_dioxide` | `ready` | `candidate_unverified` | `3` | `outputs/generated_conformers/carbon_dioxide.xyz` | `e40afee298d7` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `benzene` | `ready` | `candidate_unverified` | `12` | `outputs/generated_conformers/benzene.xyz` | `c659ac1d1cd5` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `pyridine` | `ready` | `candidate_unverified` | `11` | `outputs/generated_conformers/pyridine.xyz` | `22c9404d8692` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `phenol` | `ready` | `candidate_unverified` | `13` | `outputs/generated_conformers/phenol.xyz` | `8b552cf92cc6` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `ethanol` | `ready` | `candidate_unverified` | `9` | `outputs/generated_conformers/ethanol.xyz` | `384f0dc364a1` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `acetic_acid` | `ready` | `candidate_unverified` | `8` | `outputs/generated_conformers/acetic_acid.xyz` | `4b7963860a5e` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `dimethyl_sulfoxide` | `ready` | `candidate_unverified` | `10` | `outputs/generated_conformers/dimethyl_sulfoxide.xyz` | `1363fbd75c6d` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `urea` | `ready` | `candidate_unverified` | `8` | `outputs/generated_conformers/urea.xyz` | `bcc729c4ac54` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `glycine_neutral` | `ready` | `candidate_unverified` | `10` | `outputs/generated_conformers/glycine_neutral.xyz` | `37387198f7fe` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `glycine_zwitterion` | `ready` | `candidate_unverified` | `10` | `outputs/generated_conformers/glycine_zwitterion.xyz` | `7dd2898dd0e4` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `l_alanine` | `ready` | `candidate_unverified` | `13` | `outputs/generated_conformers/l_alanine.xyz` | `dee242b829da` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `lactic_acid` | `ready` | `candidate_unverified` | `12` | `outputs/generated_conformers/lactic_acid.xyz` | `5d3912ea7de9` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `betaine` | `ready` | `candidate_unverified` | `19` | `outputs/generated_conformers/betaine.xyz` | `8f87d19247eb` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `sodium_chloride` | `ready` | `candidate_unverified` | `2` | `outputs/generated_conformers/sodium_chloride.xyz` | `ef5bc37138b0` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `methylammonium_chloride` | `ready` | `candidate_unverified` | `9` | `outputs/generated_conformers/methylammonium_chloride.xyz` | `4d507ab6ecec` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `choline_chloride` | `ready` | `candidate_unverified` | `22` | `outputs/generated_conformers/choline_chloride.xyz` | `3059c61d4bcd` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `imidazole` | `ready` | `candidate_unverified` | `9` | `outputs/generated_conformers/imidazole.xyz` | `cb5c9519835b` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `acetylacetone` | `ready` | `candidate_unverified` | `15` | `outputs/generated_conformers/acetylacetone.xyz` | `49a5d5ce03fa` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `naphthalene` | `ready` | `candidate_unverified` | `18` | `outputs/generated_conformers/naphthalene.xyz` | `24837c53cf6c` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `anthracene` | `ready` | `candidate_unverified` | `24` | `outputs/generated_conformers/anthracene.xyz` | `49243f8821ab` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `polyethylene_glycol_fragment` | `ready` | `candidate_unverified` | `24` | `outputs/generated_conformers/polyethylene_glycol_fragment.xyz` | `d11e0c4e724d` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `caffeine` | `ready` | `candidate_unverified` | `24` | `outputs/generated_conformers/caffeine.xyz` | `73933474e1a5` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `caffeine_monohydrate_fixture` | `ready` | `candidate_unverified` | `27` | `outputs/generated_conformers/caffeine_monohydrate_fixture.xyz` | `07ac015b6d5c` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `aspirin` | `ready` | `candidate_unverified` | `21` | `outputs/generated_conformers/aspirin.xyz` | `e07471a19feb` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `paracetamol` | `ready` | `candidate_unverified` | `20` | `outputs/generated_conformers/paracetamol.xyz` | `b9782265d64a` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `ibuprofen` | `ready` | `candidate_unverified` | `33` | `outputs/generated_conformers/ibuprofen.xyz` | `6882114ccf53` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `naproxen` | `ready` | `candidate_unverified` | `31` | `outputs/generated_conformers/naproxen.xyz` | `2e366d5d6803` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `carbamazepine` | `ready` | `candidate_unverified` | `30` | `outputs/generated_conformers/carbamazepine.xyz` | `6fd0fed56c88` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `nicotinamide` | `ready` | `candidate_unverified` | `15` | `outputs/generated_conformers/nicotinamide.xyz` | `e76e8d65809b` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `nicotinic_acid` | `ready` | `candidate_unverified` | `14` | `outputs/generated_conformers/nicotinic_acid.xyz` | `585c53812404` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `benzocaine` | `ready` | `candidate_unverified` | `23` | `outputs/generated_conformers/benzocaine.xyz` | `52004c6d6d74` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `lidocaine` | `ready` | `candidate_unverified` | `39` | `outputs/generated_conformers/lidocaine.xyz` | `adeac3b2681b` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `maleic_acid` | `ready` | `candidate_unverified` | `12` | `outputs/generated_conformers/maleic_acid.xyz` | `2d34ffd0a90e` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `fumaric_acid` | `ready` | `candidate_unverified` | `12` | `outputs/generated_conformers/fumaric_acid.xyz` | `25e1ac1cc5ff` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `menthol` | `ready` | `candidate_unverified` | `31` | `outputs/generated_conformers/menthol.xyz` | `2d9159325093` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `cholesterol` | `warning` | `candidate_unverified` | `74` | `outputs/generated_conformers/cholesterol.xyz` | `556c81aee0a7` | Conformer generated, but UFFOptimizeMolecule returned code 1. |
| `methane` | `ready` | `candidate_unverified` | `5` | `outputs/generated_conformers/methane.xyz` | `e91ecce123d2` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `ethane` | `ready` | `candidate_unverified` | `8` | `outputs/generated_conformers/ethane.xyz` | `a9554b45f413` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `propane` | `ready` | `candidate_unverified` | `11` | `outputs/generated_conformers/propane.xyz` | `da701bdf3cfc` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `butane` | `ready` | `candidate_unverified` | `14` | `outputs/generated_conformers/butane.xyz` | `18cee1ababd4` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `hexane` | `ready` | `candidate_unverified` | `20` | `outputs/generated_conformers/hexane.xyz` | `d18b3df09ff9` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `decane` | `ready` | `candidate_unverified` | `32` | `outputs/generated_conformers/decane.xyz` | `0b1cdc33bcfb` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `methanol` | `ready` | `candidate_unverified` | `6` | `outputs/generated_conformers/methanol.xyz` | `ca09ce734bd7` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `propanol` | `ready` | `candidate_unverified` | `12` | `outputs/generated_conformers/propanol.xyz` | `4e0ac8669798` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `isopropanol` | `ready` | `candidate_unverified` | `12` | `outputs/generated_conformers/isopropanol.xyz` | `b72195d675b7` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `ethylene_glycol` | `ready` | `candidate_unverified` | `10` | `outputs/generated_conformers/ethylene_glycol.xyz` | `6bbfde420911` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `glycerol` | `ready` | `candidate_unverified` | `14` | `outputs/generated_conformers/glycerol.xyz` | `5c4657fbc649` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `formic_acid` | `ready` | `candidate_unverified` | `5` | `outputs/generated_conformers/formic_acid.xyz` | `a94c24e255b9` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `propionic_acid` | `ready` | `candidate_unverified` | `11` | `outputs/generated_conformers/propionic_acid.xyz` | `b2c6b1931e96` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `oxalic_acid` | `ready` | `candidate_unverified` | `8` | `outputs/generated_conformers/oxalic_acid.xyz` | `7452d929dd21` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `malonic_acid` | `ready` | `candidate_unverified` | `11` | `outputs/generated_conformers/malonic_acid.xyz` | `d569b588971b` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `succinic_acid` | `ready` | `candidate_unverified` | `14` | `outputs/generated_conformers/succinic_acid.xyz` | `1cc1f5113537` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `ammonia` | `ready` | `candidate_unverified` | `4` | `outputs/generated_conformers/ammonia.xyz` | `0117f45621ae` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `methylamine` | `ready` | `candidate_unverified` | `7` | `outputs/generated_conformers/methylamine.xyz` | `af81524e7772` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `ethylamine` | `ready` | `candidate_unverified` | `10` | `outputs/generated_conformers/ethylamine.xyz` | `53ad36049fe1` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `triethylamine` | `ready` | `candidate_unverified` | `22` | `outputs/generated_conformers/triethylamine.xyz` | `b604f9a80892` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `aniline` | `ready` | `candidate_unverified` | `14` | `outputs/generated_conformers/aniline.xyz` | `8a3b3edb1c0e` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `dichloromethane` | `ready` | `candidate_unverified` | `5` | `outputs/generated_conformers/dichloromethane.xyz` | `528c3fd0ca40` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `chloroform` | `ready` | `candidate_unverified` | `5` | `outputs/generated_conformers/chloroform.xyz` | `1c55497cc597` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `fluorobenzene` | `ready` | `candidate_unverified` | `12` | `outputs/generated_conformers/fluorobenzene.xyz` | `48a9c20ba3fc` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `furan` | `ready` | `candidate_unverified` | `9` | `outputs/generated_conformers/furan.xyz` | `e6b1827255b7` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `thiophene` | `ready` | `candidate_unverified` | `9` | `outputs/generated_conformers/thiophene.xyz` | `38dfb372d0af` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `pyrrole` | `ready` | `candidate_unverified` | `10` | `outputs/generated_conformers/pyrrole.xyz` | `ce435741a0db` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `morpholine` | `ready` | `candidate_unverified` | `15` | `outputs/generated_conformers/morpholine.xyz` | `e663b4601da3` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `piperidine` | `ready` | `candidate_unverified` | `17` | `outputs/generated_conformers/piperidine.xyz` | `8f9ca25ee2d6` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `cyclohexane` | `ready` | `candidate_unverified` | `18` | `outputs/generated_conformers/cyclohexane.xyz` | `2a48bc095100` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `adamantane` | `ready` | `candidate_unverified` | `26` | `outputs/generated_conformers/adamantane.xyz` | `bd4902089cbd` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `acetate` | `ready` | `candidate_unverified` | `7` | `outputs/generated_conformers/acetate.xyz` | `973153e5767a` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `ammonium` | `ready` | `candidate_unverified` | `5` | `outputs/generated_conformers/ammonium.xyz` | `d43a99c50445` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `tetramethylammonium` | `ready` | `candidate_unverified` | `17` | `outputs/generated_conformers/tetramethylammonium.xyz` | `27682249144a` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `sodium_acetate` | `ready` | `candidate_unverified` | `8` | `outputs/generated_conformers/sodium_acetate.xyz` | `1ed8ac160bfc` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `ammonium_nitrate` | `ready` | `candidate_unverified` | `9` | `outputs/generated_conformers/ammonium_nitrate.xyz` | `d82624f360ac` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `l_serine` | `ready` | `candidate_unverified` | `14` | `outputs/generated_conformers/l_serine.xyz` | `0129ad05bebd` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `d_serine` | `ready` | `candidate_unverified` | `14` | `outputs/generated_conformers/d_serine.xyz` | `58f5c942839a` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `tartaric_acid` | `ready` | `candidate_unverified` | `16` | `outputs/generated_conformers/tartaric_acid.xyz` | `71757f795d94` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `glucose_open_chain` | `ready` | `candidate_unverified` | `24` | `outputs/generated_conformers/glucose_open_chain.xyz` | `3c4bd96b1f1a` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `glucose_pyranose` | `ready` | `candidate_unverified` | `24` | `outputs/generated_conformers/glucose_pyranose.xyz` | `cc1a20e9836a` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `dipeptide_gly_gly` | `ready` | `candidate_unverified` | `17` | `outputs/generated_conformers/dipeptide_gly_gly.xyz` | `e85b8cc151da` | Generated conformer XYZ is present and hashable for backend smoke execution. |
| `tripeptide_gly_gly_gly` | `ready` | `candidate_unverified` | `24` | `outputs/generated_conformers/tripeptide_gly_gly_gly.xyz` | `018d17c63f0d` | Generated conformer XYZ is present and hashable for backend smoke execution. |

## Policy

- Generated conformer XYZ files are backend inputs for software smoke tests, not experimental structures.
- SHA-256 hashes identify exact local inputs without making them verified scientific evidence.
- Warning rows may still be useful for backend robustness checks, but they remain unverified inputs.
- No backend-ready input row can support a drug-discovery, stability, or benchmark claim by itself.
