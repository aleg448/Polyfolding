# Bugfix Validation: September 10, 2026

This pass follows the user's instruction to stop publication/push work and fix
the remaining defects. No commit or push was performed. The earlier pending-change
review and its campaign receipts remain historical snapshots.

## Corrected Behavior

- CPOSS inference now selects by data-block identity, not an ASE coordinate
  index. A regression reproduced an oxygen block being reported with the next
  hydrogen block's coordinates after a metadata-only header. Metadata-only,
  missing, or ambiguous selected blocks now fail explicitly.
- Split-conformal calibration no longer clips an out-of-range order statistic
  to the largest observed error. It returns `insufficient_calibration_samples`
  with `threshold: null`, and both abstention APIs preserve the missing-threshold
  decision. Calibration and bootstrap inputs reject non-finite samples.
- A clear numerical margin is now `margin_clear_not_calibrated`, never
  `claim_direction_allowed`. Reports explicitly record
  `calibration_validated: false`. Successful energy sanity checks do not assert
  scientific calibration.
- Ensembles require every member to declare the same energy reference. The
  mixed-reference override now raises; it cannot establish alignment merely by
  being enabled. Conflicting prediction references/scopes and non-finite
  energies/OOD scores are rejected. A single member reports missing uncertainty,
  not zero uncertainty. Ensemble disagreement is not calibrated error.
- Campaign plans reject malformed molecule/options objects. Corrupted cached
  JSON or malformed artifact/payload metadata cannot abort the whole run or be
  reused as a successful measurement; tasks are recomputed.
- Coincident atoms remain visible as zero-distance short contacts. Invalid
  force shapes, non-finite positions/forces, and invalid cutoffs fail explicitly.
  A failed periodic distance calculation is no longer retried as a cluster.
- Unreadable declared charge annotations fail instead of silently becoming the
  default neutral charge. Explicit absence of ASE annotations still uses the
  caller's documented default.
- Malformed evidence forms block their candidate without aborting later
  candidates. Compound values cannot masquerade as required scalar fields.
- Non-finite energies are unrankable, rather than counted as a winner or tie.
  Non-finite CIF cell values are omitted as unavailable. Molecule QA helpers use
  scoped RDKit log suppression and restore the caller's log configuration.
- Filename fallbacks are sanitized too, and Windows reserved device names are
  prefixed to remain ordinary filenames.

The conformal rule uses the `ceil((n + 1) * coverage)` order statistic, without
interpolation. The implementation does not prove that supplied residuals are
held out or exchangeable. Method reference:
[Finite-sample correction](https://www.taija.org/ConformalPrediction.jl/dev/explanation/finite_sample_correction/),
following [Angelopoulos and Bates](https://arxiv.org/abs/2107.07511).

## Compatibility Changes

Consumers must handle a null calibration threshold by abstaining, not replacing
it with zero. `allow_mixed_reference=True` now raises a `ValueError`; perform
validated alignment upstream and supply a shared reference. Undeclared legacy
ensemble models must add an explicit reference. Code matching the old
`claim_direction_allowed` or `energy_verification_passed` statuses must migrate
to the non-calibration-claim statuses. Original snapshot reports are not silently
rewritten or represented as current computations.

## Tests

| Check | Result |
|---|---|
| Existing scientific environment, full suite | 402 passed, 1 skipped |
| Modern RDKit/NumPy/ASE environment, full suite | 402 passed, 1 skipped |
| Base environment, full suite | 373 passed, 10 skipped |
| Ruff | Passed |
| Existing mypy typed-core gate | Passed, 27 files |
| Git whitespace check | Passed after normalizing mixed line endings in the CPOSS script |
| Historical-module report CLI | Passed; outputs in `outputs/bugfix_validation/` |

The new regression runs reproduced 25 initial failures, 14 additional geometry/
input failures, and the CIF identity mismatch before their respective fixes.
There are 45 additional test cases in the scientific suite relative to the
previous 357-test snapshot. The scientific CI job now also runs the CPOSS block
identity test. Remote CI has not been run during this pass.

## Execution Receipts

| Campaign | Outcome | Run ID |
|---|---|---|
| `bugfix_panel_20260910` | 85 modern-RDKit conformer tasks succeeded in about 68 seconds | `12d8d41f0e164336aa9db421ff9fa476` |
| Same panel, repeated | 85 cached, zero worker jobs | `7a9f72ceaf4746e38845c9a45caebf2c` |
| `bugfix_mace_20260910` | Two conformers and two pinned MACE-OFF23 small backend tasks succeeded | `f77f4e08a39140bd8207c4e548287698` |
| Same MACE pilot, repeated | Four cached, zero worker jobs | `a6e93fdff62e4326acdf450e674cf720` |

Each receipt is under
`outputs/campaigns/CAMPAIGN_ID/runs/RUN_ID/evidence_packet.json` and `.md`.
Their source fingerprint is
`69570688ab9967d501a5fbf952f88d237f0feeb1980047543681a8278c5d84e0`.
No calculation-source changes were detected during these runs. Local generated
outputs remain ignored by Git and were not published.

After these campaigns, mixed CRLF/LF endings in the CPOSS script's import block
were normalized to LF. No executable statement changed, and the scientific suite
was rerun. The receipts retain their exact pre-normalization byte fingerprints;
a subsequent campaign will invalidate the old cache because source hashes include
line endings. This is intentional rather than rewriting historical receipts.

The panel retains UFF non-convergence warnings for cholesterol and the long
polyethylene glycol fragment. Those are scientific-computation outcomes to
investigate, not suppressed test failures or verified optimized geometries.

## Reproduce

```powershell
python -B -m pytest --capture=sys -p no:cacheprovider -q
.\.venv\Scripts\python.exe -B -m pytest --capture=sys -p no:cacheprovider -q
.\.venv-orchestration\Scripts\python.exe -B -m pytest --capture=sys -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m ruff check src scripts tests
.\.venv\Scripts\python.exe -m mypy
.\.venv-orchestration\Scripts\python.exe -B scripts/run_molecule_campaign.py --campaign-id bugfix_panel_20260910 --max-jobs 100 --max-seconds 300
```

This validation establishes tested software behavior, not the absence of every
possible defect. Experimental labels, independent review, calibration dataset
provenance, and model-domain validation still require evidence. Campaigns remain
`candidate_unverified`; this pass does not authorize publication or pushing.
