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
```

The indexer supplies block IDs, molecule-family codes, form numbers, space groups, and cell metadata. It does not supply experimental stability ordering; that still has to be curated from primary evidence.

## Promotion Rules

- `draft`: placeholders allowed; never used for scientific claims.
- `reviewed`: no TODO placeholders; evidence extracted by one curator.
- `verified`: no TODO placeholders; evidence checked by a second reviewer; ambiguous stability excluded.
- `excluded`: retained for audit trail but excluded from primary metrics.

## Ambiguity Handling

If studies disagree, keep the record but set `stability_ordering` to `ambiguous`. Ambiguous records can support qualitative discussion and failure-mode discovery, but not ranking accuracy or calibration claims.
