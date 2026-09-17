# Pre-Push Validation: September 16, 2026

This is a code-and-methods review checkpoint, not a scientific benchmark release.
The user reauthorized edits, reports, and a push request conditional on successful
testing. The no-push instruction in the September 10 reports describes that
historical pass; it is not the current instruction.

## Review Scope

The pending branch includes the bounded, resumable campaign runner and the
scientific-contract fixes described in
[Bugfix Validation](bugfix_validation_2026-09-10.md) and
[Pending Changes Review](pending_changes_review_2026-09-10.md). Existing changes
were preserved. This pass additionally corrected the legacy calibration-report
path used by the calibration CLI and quick benchmark.

- Missing uncertainty no longer synthesizes 100% confidence.
- Reports include only verified, non-OOD records with defined experimental
  ordering, finite eV energies, and valid positive combined uncertainty.
  Excluded predictions carry explicit reasons. Low-margin predictions remain
  included to avoid selecting only easy cases.
- Empty Brier/ECE scores are `null`, not perfect-looking zeroes. Probability
  metrics reject non-finite or out-of-range inputs and non-boolean outcomes.
- The exponential confidence mapping remains a heuristic, not a fitted
  probability model. Reports and ledger entries explicitly declare
  `calibration_validated: false`; figures display unavailable scores honestly.
- Regression tests cover invalid energies/uncertainties, OOD, unsupported units,
  overflow, empty evidence, unverified records, and report/ledger integration.

## Validation

The new calibration tests reproduced 23 failures before the fix; all 25 tests
in that module passed afterward.

| Check | Result |
|---|---|
| Base environment, full suite | 396 passed, 10 skipped |
| Existing scientific environment, full suite | 425 passed, 1 skipped |
| Modern RDKit/NumPy/ASE environment, full suite | 425 passed, 1 skipped |
| Modern environment, affected report/figure tests after final spacing change | 33 passed |
| Calibration, quick benchmark, and reviewer-facing publication checks | 57 passed |
| Ruff | Passed |
| Mypy typed-core gate | Passed, 27 source files |
| Python compileall | Passed |
| Git whitespace check | Passed |

The base and existing scientific suites were rerun after the final figure
spacing change. The modern full suite preceded that layout-only change, with
the affected tests rerun afterward. Remote CI has not yet been observed for
this checkpoint. A simple local secret-pattern scan found no matches; this is
not a substitute for the CI secret scanner or a comprehensive security audit.

Reproduction commands (from the repository root):

```powershell
python -B -m pytest --capture=sys -p no:cacheprovider -q
.\.venv\Scripts\python.exe -B -m pytest --capture=sys -p no:cacheprovider -q
.\.venv-orchestration\Scripts\python.exe -B -m pytest --capture=sys -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m ruff check src scripts tests
.\.venv\Scripts\python.exe -m mypy
python -m compileall -q src scripts tests
git -c core.autocrlf=false diff --check
```

## Fresh Execution Receipts

| Campaign | Outcome | Run ID |
|---|---|---|
| `review_panel_20260916` | 85 conformer tasks succeeded, about 104 seconds | `36101fbe949c46a7a40c62fec1fc57c1` |
| Same panel, repeated | 85 cached, zero worker jobs | `e0a3507ed03d4c8e82e29e86049d5399` |
| `review_mace_20260916` | Two conformers and two MACE tasks succeeded, about 78 seconds | `d7c14222172e46ce824f318a108debae` |
| Same pinned MACE pilot, repeated | Four cached, zero worker jobs | `6d42c6f2d0de410da60db9d0dfe46f52` |

Receipts and exact source archives remain local under
`outputs/campaigns/CAMPAIGN_ID/runs/RUN_ID/`. The panel used modern RDKit; the
MACE pilot used the existing scientific environment and the local
`MACE-OFF23_small.model` checkpoint. Both repetitions verified artifact hashes
and reused successful tasks without scientific worker execution.

The panel's source fingerprint is
`9f0e43856c0cafa798d70a5b124436025c8dc861602eba1fe91c95136b920dca`.
The final reliability-figure spacing adjustment happened after those panel
runs. The subsequent MACE pilot used the final calculation-source fingerprint
`923c83c3b9bae49a8ca04334828c1b880fb662620e99b401face0b1b74f3a429`.
No source changed during either campaign. Source-sensitive cache invalidation
will recompute the older panel after this layout change; the receipts are not
silently relabeled as byte-identical to the final source.

All results remain `candidate_unverified`, with zero claim-ready records. UFF
non-convergence warnings for cholesterol and the long polyethylene glycol
fragment remain visible in both the fresh and cached panel reports. A successful
task does not establish an optimized geometry. AIMNet2 and UMA were not rerun
as real backends during this pass.

## Compatibility

Consumers of `brier_score`, `expected_calibration_error`, and calibration report
JSON must accept `None`/`null` for empty evidence. Calibration reports no longer
include draft or reviewed pairs. Nonempty output is labeled
`heuristic_diagnostics_not_validated`; empty output is `no_eligible_evidence`.
Neither status validates the confidence mapping or promotes a record.

## Review Boundary

Only source, tests, CI configuration, and documentation are intended for this
branch push. Generated reports, source archives, model checkpoints, local
environments, campaign databases, and restricted CCDC/CSD coordinates remain
outside the commit. Historical reports are not rewritten as current runs.

Tests establish software behavior, not experimental truth. Verified labels,
held-out calibration provenance, model-domain validity, and independent human
review remain scientific requirements. Optional backend execution and remote CI
results must be distinguished from local contract tests. This checkpoint does
not authorize a public scientific dataset or paper release.
