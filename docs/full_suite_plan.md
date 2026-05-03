# CrystalProbe Full-Suite Build Plan

This repository implements the CrystalProbe vertical slice as a dependency-light research suite. The full POLARIS architecture remains the long horizon; CrystalProbe focuses on the trust infrastructure needed first.

## Implemented Locally

- Benchmark schema and curation readiness checks.
- Pairwise prediction file format.
- Ranking and behavioural fingerprint metrics.
- Markdown/JSON report generation.
- Quick benchmark runner with provenance ledger output.
- Optional adapter discovery for ASE, MACE-OFF, AIMNet2, UMA, and FastCSP.
- Paper outlines for the fingerprint, data descriptor, and JOSS outputs.

## Adapter Strategy

Heavy scientific dependencies are isolated behind `crystalprobe.foundry`. The core package stays installable on a plain Python environment; real MLIP execution is enabled by installing optional backends and configuring model assets.

The next adapter implementations should land in this order:

1. ASE CIF reader, because every MLIP backend needs a structure object.
2. MACE-OFF single-point energy adapter.
3. MACE-OFF pairwise ranking runner.
4. AIMNet2 adapter.
5. Ensemble wrapper over MACE-OFF/AIMNet2.
6. FastCSP quick-mode integration.

## Scientific Release Criteria

- No headline metric can include `draft` records.
- Every `verified` record must have license, source ID, stability citation, and disorder annotation.
- Every model result must include model name, version/checkpoint, input manifest hash, prediction file hash, and CrystalProbe version.
- Ambiguous stability records are allowed only in exploratory reports.

