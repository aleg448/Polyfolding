# Crystallographic Database Search

This document records the database-search path for target crystal structures.

## Open Databases

The Crystallography Open Database (COD) is the preferred first pass because it is open and its CIF files are programmatically retrievable. CrystalProbe wraps COD searches with:

```powershell
python scripts\search_crystal_databases.py --target lisdexamfetamine --output outputs\lisdexamfetamine_crystal_database_search.json
```

For lisdexamfetamine dimesylate, the current COD result is negative for:

- `lisdexamfetamine`
- `lisdexamphetamine`
- `amphetamine` + `dimesylate`
- exact salt formula `C17 H33 N3 O7 S2`

A loose CHNOS cell-volume query around the patent lattice volume returns unrelated candidates and no target-name match.

Scripted result:

- `text_lisdexamfetamine`: 0 hits.
- `text_lisdexamphetamine`: 0 hits.
- `text_amphetamine_dimesylate`: 0 hits.
- `formula_salt_exact`: 0 hits.
- `cell_window_chons`: 1401 broad hits, first hits unrelated by formula/title.

## CCDC/CSD

The public CCDC Access Structures service currently requires human validation and terms acceptance in a browser. The page also states that systematic retrieval and analysis should use the CSD System and its Python API.

For this project, the CCDC/CSD path is:

1. Search manually or through an installed/licensed CSD Python API for:
   - `lisdexamfetamine`
   - `lisdexamphetamine`
   - `L-lysine-d-amphetamine dimesylate`
   - formula `C17 H33 N3 O7 S2`
   - patent lattice window: monoclinic, `P 21`, `a=10.2509`, `b=11.2804`, `c=19.3534`, `beta=94.124`, `V=2232.1`.
2. If a CCDC deposition exists, export the CIF only if license terms permit local research use.
3. Store the raw CIF under `data/sources/ccdc/`, which is ignored by git.
4. Record the identifier, license/access terms, and derived measurement results in the curation dossier.

## Current Lisdexamfetamine Status

Patent evidence proves a crystal form was characterized, but an open coordinate file has not been found. COD appears negative. CCDC/CSD remains the next likely source, requiring manual/API access.
