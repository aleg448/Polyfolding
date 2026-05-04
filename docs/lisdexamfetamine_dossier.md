# Lisdexamfetamine Dimesylate Dossier

This dossier scopes what CrystalProbe can prove today for lisdexamfetamine dimesylate and what remains blocked. It is a solid-form research note, not medical advice.

## Target

- Salt/API: lisdexamfetamine dimesylate.
- Parent: lisdexamfetamine.
- PubChem salt CID: `11597697`.
- PubChem parent CID: `11597698`.
- Salt formula: `C17H33N3O7S2`.
- Parent formula: `C15H25N3O`.

## Evidence Found

PubChem identifies lisdexamfetamine dimesylate as the dimesylate salt, gives the parent compound relationship, component methanesulfonic acid relationship, formula, SMILES, InChI, and other identifiers.

US patent `US7659253` reports a crystalline lisdexamfetamine dimesylate form. The accessible patent text gives XRPD peaks, DSC behavior, and single-crystal lattice parameters. It also describes the single-crystal data collection/refinement workflow and reports a comparison between calculated and experimental XRPD.

## Current Proof Status

| Layer | Status | Meaning |
| --- | --- | --- |
| Identity | Verified from public source | PubChem identity and parent/salt relationship are clear. |
| Crystalline solid form | Evidence present | Patent reports crystalline dimesylate and lattice parameters. |
| Computable crystal coordinates | Blocked | We do not yet have a license-clean CIF or atom-coordinate table. |
| MLIP crystal ranking | Not ready | Needs coordinates and a comparison form or verified endpoint. |
| Molecule-level diagnostics | Ready | PubChem parent 3D conformer can be measured now. |

## Measurement Plan

1. Measure the PubChem parent 3D conformer with MACE and AIMNet.
2. Record local bond/contact/force diagnostics.
3. Treat those results as parent-molecule diagnostics only.
4. Continue source discovery for a license-compatible crystalline dimesylate CIF.

## Commands

```powershell
python scripts\run_structure_inference.py data\sources\pubchem\lisdexamfetamine_11597698_3d.sdf --structure-id lisdexamfetamine_parent_pubchem_11597698 --backend mace --output outputs\lisdexamfetamine_parent_mace.json
python scripts\run_structure_inference.py data\sources\pubchem\lisdexamfetamine_11597698_3d.sdf --structure-id lisdexamfetamine_parent_pubchem_11597698 --backend aimnet2 --output outputs\lisdexamfetamine_parent_aimnet2.json
```

## Current Blocker

The core blocker is not model execution. It is source coordinates. The patent proves a crystalline dimesylate form exists, but the accessible text does not provide a redistributable coordinate file. Without coordinates, CrystalProbe cannot honestly claim a crystal-packing or polymorph measurement.

## Crystallographic Database Search

Open COD queries are negative for direct target-name and exact-formula searches. A loose CHNOS cell-volume query around the patent lattice returns 1401 broad candidates, but the first inspected hits are unrelated by formula/title and no direct target-name hit is present.

CCDC/CSD remains the likely source for coordinates, but the public Access Structures page requires human validation and terms acceptance, and systematic retrieval should use the CSD System/Python API. Search terms and lattice windows are recorded in `docs/crystallographic_database_search.md`.

## Completed Parent-Conformer Measurements

MACE-OFF23 small and AIMNet2 both successfully measured the PubChem parent conformer from CID `11597698`.

Shared result:

- Formula: `C15H25N3O`.
- Atoms: 44.
- Diagnostic flag: `high_force_atom`.
- Top local issue: amide/carbonyl O-C environment.
- Severe short contacts: none reported.

Backend-specific result:

- MACE-OFF23 small: energy `-22496.379770707095 eV`, max force `1.3198525597858526 eV/Ang`.
- AIMNet2: energy `-22494.29040775406 eV`, max force `1.247026870117706 eV/Ang`.

These measurements prove that CrystalProbe can analyze the lisdexamfetamine parent conformer and identify local stress consistently across two MLIPs. They do not prove the dimesylate crystal packing because the salt/crystal coordinates remain unavailable.
