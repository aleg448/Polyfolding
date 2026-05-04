# Facebook FAIR Chemistry Model Access

Date verified: 2026-05-04

The Hugging Face account associated with the local `.env` token now has accepted access for:

- `facebook/OMC25`
- `facebook/UMA`
- `facebook/OMAT24`
- `facebook/OMol25`

The machine-readable access note is `data/curation/facebook_model_access_v0.1.json`.

## Verified Docker Result

The fairchem Docker environment can see `HF_TOKEN`, download `facebook/OMC25` checkpoint `checkpoints/esen_s.pt`, run CUDA inference on periodic H2O, and initialize UMA checkpoint alias `uma-s-1p2`.

Command:

```powershell
docker compose run --rm crystalprobe-fairchem python scripts\fairchem_omc25_smoke.py --try-uma
```

Result summary:

- `facebook/OMC25` checkpoint SHA-256: `38cd8d4b48da75f1385fc7044ac33d7a7922ced8d7a4d007c62de3a9ede7b1fb`.
- Device: `cuda`.
- H2O smoke energy: `-14.11356679011865` eV.
- Forces shape: `[3, 3]`.
- UMA `uma-s-1p2`: available.

## Repository File Inventories

### `facebook/UMA`

- `checkpoints/uma-m-1p1.pt`
- `checkpoints/uma-s-1.pt`
- `checkpoints/uma-s-1p1.pt`
- `checkpoints/uma-s-1p2.pt`
- `references/form_elem_refs.yaml`
- `references/iso_atom_elem_refs.yaml`

### `facebook/OMC25`

- `checkpoints/esen_s.pt`
- `assets/omc25-starting-crystals.csv`

### `facebook/OMAT24`

- `eqV2_153M_omat.pt`
- `eqV2_153M_omat_mp_salex.pt`
- `eqV2_31M_mp.pt`
- `eqV2_31M_omat.pt`
- `eqV2_31M_omat_mp_salex.pt`
- `eqV2_86M_omat.pt`
- `eqV2_86M_omat_mp_salex.pt`
- `esen_30m_omat.pt`

### `facebook/OMol25`

- `checkpoints/AllScAIP/AllScAIP-OMol102M-md-cons.pt`
- `checkpoints/AllScAIP/AllScAIP-OMol102M-md-d.pt`
- `checkpoints/esen_md_direct_all.pt`
- `checkpoints/esen_sm_conserving_all.pt`
- `checkpoints/esen_sm_direct_all.pt`
- `references/iso_atom_elem_refs.yaml`

## Current Interpretation

UMA is no longer blocked by Hugging Face access. OMC25 and UMA are locally verified through Docker/fairchem.

OMAT24 and OMol25 access are verified by model-repo inventory. CrystalProbe still needs dedicated calculation paths before these become scientific workflow evidence.

UMA can be selected in the structure and sensitivity inference scripts with `--backend uma`. The default checkpoint alias is `uma-s-1p2`, and the default task is `omc`.

The current guardrail report is generated with:

```powershell
python scripts\build_model_guardrails_report.py
```

It writes `outputs/fairchem_model_guardrails.json` and `outputs/fairchem_model_guardrails.md`. In that report, OMAT24 and OMol25 are intentionally `access_verified_validation_blocked`: access is accepted, but CrystalProbe must not use them for organic molecular-crystal ranking, CPOSS benchmark claims, formation-energy claims, energy-above-hull claims, or therapeutic contrast claims until a task-specific validation path is implemented.

## Energy Reference Caution

UMA models and legacy inorganic bulk models trained using OMat24 are trained with DFT and DFT+U total-energy labels. These are not directly compatible with Materials Project calculations.

Do not apply Materials Project MP2020 corrections or Materials Project reference compounds directly to OMat24-trained model outputs. Use OMat24-specific reference unary compounds and MP2020-style anion and GGA/GGA+U mixing corrections from the OMat24 Hugging Face repository when doing OMat24-specific thermodynamic work.
