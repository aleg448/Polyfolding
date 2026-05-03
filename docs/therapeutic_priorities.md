# Therapeutic Priority Queue

CrystalProbe should start visible measurements with medicines that people understand and that have real solid-form stakes. This document defines the first therapeutic-priority queue; it is not medical advice and it is not a verified benchmark.

## Priority Order

1. ADHD medications with public solid-form evidence.
2. High-use everyday medicines already present in CPOSS209 or the draft manifest.
3. Neurology and quality-control reference systems with strong polymorph literature.

## ADHD Targets

- Atomoxetine hydrochloride: highest initial ADHD curation target. Public literature reports stable and metastable polymorphic forms, and a later commercial powder-diffraction structure. The blocker is license-compatible CIF access and primary-evidence extraction.
- Methylphenidate hydrochloride: important target, but currently in source-discovery state for open polymorph CIFs.
- Lisdexamfetamine dimesylate: important salt-form target, but currently in source-discovery state for solid-form structures.
- Modafinil: not a first-line ADHD benchmark target, but useful adjacent neuropharmaceutical polymorph evidence exists and may be a good early external-CIF curation exercise.

## Immediate CPOSS Measurements

CPOSS209 does not appear to contain the core ADHD medicines above, so immediate measurements should use overlapping foundation medicines:

- `IBP`: ibuprofen, 7 CPOSS crystal blocks.
- `CBZ`: carbamazepine, 9 CPOSS crystal blocks.

Run source-level measurements with:

```powershell
python scripts\run_cposs_structure_inference.py --backend mace --family IBP --output outputs\cposs_ibp_mace.jsonl
python scripts\summarize_structure_predictions.py outputs\cposs_ibp_mace.jsonl --json-out outputs\cposs_ibp_mace_summary.json
python scripts\run_cposs_structure_inference.py --backend mace --family CBZ --output outputs\cposs_cbz_mace.jsonl
```

These are source-level energy and force diagnostics. They become benchmark ranking measurements only after the corresponding experimental stability labels are verified.

## Data File

The machine-readable queue is `data/curation/therapeutic_priority_v0.1.json`.
