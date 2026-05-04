# CCDC Source Ingestion

This note records how CrystalProbe handles local CCDC/CSD CIF exports. Raw CCDC files stay under `data/sources/ccdc/`, which is ignored by git. Checked-in files may record identifiers, commands, summaries, and derived measurements, but not redistributed raw coordinates.

## Local Exports

The current local source set contains two CCDC multi-block CIF exports:

- `data/sources/ccdc/ccdc_amphetamine_phosphate_1036952-978407.cif`
- `data/sources/ccdc/ccdc_ibuprofen_bundle_1041369-776185.cif`

The amphetamine-family export contains 30 blocks. The selected proof block is `AMPETP`, CCDC `1102740`, systematic name `(+)-Amphetamine dihydrogen phosphate`, formula moiety `C9 H14 N1 1+,H2 O4 P1 1-`, space group `P 21`.

The ibuprofen export contains 31 blocks. The selected proof block is `ibuprofen`, CCDC `774097`, formula `C13 H18 O2`, space group `P 21/c`, audit DOI `10.5517/cctzhw4`.

## Inspection and Extraction

```powershell
python scripts\inspect_ccdc_cif.py data\sources\ccdc\ccdc_amphetamine_phosphate_1036952-978407.cif --json-out outputs\ccdc_amphetamine_bundle_index.json --extract-block AMPETP --extract-out outputs\ccdc_ampetp_extracted.cif
python scripts\inspect_ccdc_cif.py data\sources\ccdc\ccdc_ibuprofen_bundle_1041369-776185.cif --json-out outputs\ccdc_ibuprofen_bundle_index.json --extract-block ibuprofen --extract-out outputs\ccdc_ibuprofen_774097_extracted.cif
```

`inspect_ccdc_cif.py` splits multi-block exports, records per-block metadata tags, and can extract one block into a standalone CIF. The extractor sanitizes common CSD space-group spellings such as `P2(1)` and `P2(1)/c` into forms ASE can parse.

## Measurement Commands

These commands run directly from the raw local CCDC bundles and extract the requested block into `outputs/_structure_inference_blocks/` before ASE reads it.

```powershell
python scripts\run_structure_inference.py data\sources\ccdc\ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend mace --output outputs\ccdc_ampetp_mace.json
python scripts\run_structure_inference.py data\sources\ccdc\ccdc_amphetamine_phosphate_1036952-978407.cif --cif-block AMPETP --structure-id ccdc_1102740_amphetamine_dihydrogen_phosphate --backend aimnet2 --output outputs\ccdc_ampetp_aimnet2.json
python scripts\run_structure_inference.py data\sources\ccdc\ccdc_ibuprofen_bundle_1041369-776185.cif --cif-block ibuprofen --structure-id ccdc_774097_ibuprofen --backend mace --output outputs\ccdc_ibuprofen_774097_mace.json
docker compose run --rm crystalprobe-core python scripts/run_structure_inference.py data/sources/ccdc/ccdc_ibuprofen_bundle_1041369-776185.cif --cif-block ibuprofen --structure-id ccdc_774097_ibuprofen --backend aimnet2 --output outputs/ccdc_ibuprofen_774097_aimnet2_linux.json
```

## Interpretation

These files prove the ingestion and measurement path on two real CCDC crystal structures relevant to therapeutic-priority work. The amphetamine-phosphate structure is useful adjacent evidence for the amphetamine medication family, but it is not lisdexamfetamine dimesylate. Lisdexamfetamine dimesylate remains blocked until a license-compatible crystal CIF or atom-coordinate table is found.
