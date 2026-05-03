# FastCSP Integration Plan

FastCSP integration should be incremental and upstream-friendly.

## PR 1: Documentation and Provenance

Add output metadata fields for model version, input hash, runtime, and hardware tier. This is low-risk and useful even without uncertainty integration.

## PR 2: Regression Benchmark Hook

Add a small polymorph-pair benchmark hook that can run in CI or nightly mode. The first upstream target should be a smoke benchmark, not the full CrystalProbe dataset.

## PR 3: Uncertainty Wrapper Integration

Expose a ranking path that can call CrystalProbe-compatible wrappers and emit energy uncertainty plus OOD status.

## Fork Criteria

Fork only if upstream review blocks the research release for more than one month or if APIs are incompatible with honest uncertainty reporting.

