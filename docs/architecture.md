# CrystalProbe Architecture

CrystalProbe uses one shared contract across four research tracks:

1. Benchmark curation produces JSON Lines records that validate against `PolymorphPair`.
2. Model adapters convert structures into `EnergyForcePrediction` objects.
3. Evaluation code joins pair records with predicted energies and computes ranking, gap, and calibration metrics.
4. Papers and public releases consume generated summaries and figures from the same package.

The schema is intentionally strict for `reviewed` and `verified` records but permissive for `draft` records. That lets curation begin immediately without laundering placeholders into scientific claims.

## Near-Term Adapter Plan

- Add an ASE-backed CIF loader behind an optional dependency.
- Implement a `MACEAdapter` once local MACE-OFF installation is confirmed.
- Implement an `AIMNet2Adapter` separately so import failures are isolated.
- Keep UMA and FastCSP integrations behind optional extras because their dependency footprint will be larger.

## Scientific Guardrails

- Pairwise ranking claims should use only `verified` records.
- Ambiguous stability records belong in exploratory analyses, not headline metrics.
- Every public result must pin model checkpoint, package version, structure source, and benchmark manifest hash.

