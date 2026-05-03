# Benchmark Curation Protocol

Use this protocol before promoting any polymorph-pair record beyond `draft`.

## Required Evidence

- Two CIF references, one per polymorph form.
- Structure source ID and redistribution license for each CIF.
- Experimental stability ordering with temperature and condition notes when available.
- DOI or durable URL for the stability evidence.
- Explicit disorder annotation, even when the value is `false`.
- Chemistry tags that support the planned behavioural slices.

## Promotion Rules

- `draft`: placeholders allowed; never used for scientific claims.
- `reviewed`: no TODO placeholders; evidence extracted by one curator.
- `verified`: no TODO placeholders; evidence checked by a second reviewer; ambiguous stability excluded.
- `excluded`: retained for audit trail but excluded from primary metrics.

## Ambiguity Handling

If studies disagree, keep the record but set `stability_ordering` to `ambiguous`. Ambiguous records can support qualitative discussion and failure-mode discovery, but not ranking accuracy or calibration claims.

