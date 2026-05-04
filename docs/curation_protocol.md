# Benchmark Curation Protocol

Use this protocol before promoting any polymorph-pair record beyond `draft`.

## Required Evidence

- Two CIF references, one per polymorph form.
- Structure source ID and redistribution license for each CIF.
- Experimental stability ordering with temperature and condition notes when available.
- DOI or durable URL for the stability evidence.
- Explicit disorder annotation, even when the value is `false`.
- Chemistry tags that support the planned behavioural slices.

## CPOSS209 Intake

Use the CPOSS209 indexer to create a source inventory before promoting records:

```powershell
python -m crystalprobe.benchmark.cli cposs-index data\sources\cposs209\cg5c00255_si_004 --no-atoms
python -m crystalprobe.benchmark.cli cposs-pairs data\sources\cposs209\cg5c00255_si_004\All_Psi_Crys.cif
```

The indexer supplies block IDs, molecule-family codes, form numbers, space groups, and cell metadata. It does not supply experimental stability ordering; that still has to be curated from primary evidence.

The adjacent-form pair queue from `All_Psi_Crys.cif` currently contains 189 candidate pairs across 20 families. Those candidates are a curation queue, not benchmark records, until experimental evidence is attached.

The local CPOSS mini-benchmark bridge can also be converted into an adjacent relative-energy pair queue:

```powershell
python scripts\build_cposs_pair_candidate_report.py
python scripts\build_cposs_pair_triage_report.py
python scripts\build_cposs_evidence_workpack.py
```

This writes `outputs/cposs_pair_candidate_report.json`, `outputs/cposs_pair_candidate_report.md`, `outputs/cposs_pair_triage_report.json`, `outputs/cposs_pair_triage_report.md`, `outputs/cposs_evidence_workpack.json`, and `outputs/cposs_evidence_workpack.md`. These candidates are ranked by local model-relative energy only and remain `needs_experimental_evidence` until stability evidence, source-license review, and disorder annotations are attached.

## Promotion Rules

- `draft`: placeholders allowed; never used for scientific claims.
- `reviewed`: no TODO placeholders; evidence extracted by one curator.
- `verified`: no TODO placeholders; evidence checked by a second reviewer; ambiguous stability excluded.
- `excluded`: retained for audit trail but excluded from primary metrics.

## Ambiguity Handling

If studies disagree, keep the record but set `stability_ordering` to `ambiguous`. Ambiguous records can support qualitative discussion and failure-mode discovery, but not ranking accuracy or calibration claims.
