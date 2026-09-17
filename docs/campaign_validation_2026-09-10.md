# Campaign Validation: September 10, 2026

Historical pre-review execution snapshot. The later
[Pending Changes Review](pending_changes_review_2026-09-10.md) records additional
fixes and updated tests. The source fingerprint and counts below describe the
earlier implementation, not the post-review working tree.

This is software and execution evidence. It establishes neither experimental
stability ordering nor scientific prediction accuracy. No record was promoted.

## Verification

| Check | Result |
|---|---|
| Base Python full test suite | 316 passed, 7 skipped |
| Scientific `.venv` full test suite | 332 passed, 1 skipped |
| Isolated orchestration environment focused tests | 26 passed |
| Scientific contract tests matching the added CI job | 38 passed |
| Ruff | Passed |
| Existing mypy typed-core gate | Passed, 27 source files |
| Git whitespace check | Passed |
| CI configuration | Parsed locally; new GitHub job has not been run remotely |

The new regression tests cover incomplete CPOSS mapping/disorder/review,
ASE's unannotated charge arrays, real ammonium XYZ charge preservation,
dependency ordering, bounded retries, interruption recovery, writer exclusion,
input/source/environment changes, artifact tampering, malformed worker results,
and prohibited evidence promotion by a worker.

## Actual campaigns

| Campaign | Observed outcome |
|---|---|
| Full panel, initial generation | 85 conformer jobs completed in approximately 81 seconds |
| Full panel, current-code budget exercise | Paused after 10 completed jobs with 75 pending |
| Full panel, resumed | Reused 10 tasks and executed the remaining 75 |
| Full panel, repeated after completion | Reused all 85 tasks; zero worker jobs; about 1 second inside the runner |
| Pinned MACE-OFF23 small pilot | Two conformers and two real backend jobs succeeded; repeat reused all four |
| Prefect 3.8.5 pilot | Two real conformer tasks completed through the optional flow; temporary server stopped on exit |

The generated follow-up queue retains UFF non-convergence warnings for
cholesterol, glycylglycylglycine, and the long polyethylene glycol fragment.
Coordinates were generated, but convergence was not asserted. These are useful
QA cases, not verified optimized geometries.

## Local receipts

The following run directories contain immutable-per-attempt records and local
evidence packets. They are intentionally under ignored `outputs/` and are not
automatically included in a public artifact or Git commit.

- Panel reuse: `outputs/campaigns/september_panel/runs/c8cb1edde1204a51a3e9ddf774850f7c/`
- MACE reuse: `outputs/campaigns/september_smoke/runs/1d4d4c0df9164f28b9176fa2b71227d9/`
- Prefect execution: `outputs/campaigns/prefect_pilot/runs/64e449e5d48349b8ae226d7e0e7f34de/`

All three receipts identify source fingerprint
`1bb73b91a6120c2508c6cfa30f2164e56ada3c5131ef18424400eb46fbb816a8`.
The source fingerprint covers Python source and package configuration; this
validation document and CI YAML are not calculation inputs.

## Reproduction

```powershell
python -B -m pytest --capture=sys -p no:cacheprovider -q
.\.venv\Scripts\python.exe -B -m pytest --capture=sys -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m ruff check src scripts tests
.\.venv\Scripts\python.exe -m mypy
.\.venv\Scripts\python.exe scripts/run_molecule_campaign.py --campaign-id september_panel --max-jobs 100 --max-seconds 300
```

See [Autonomous Research Pipeline](autonomous_research_pipeline.md) for model
checkpoint selection, optional Prefect setup, primary-source technology research,
execution limits, and planned scientific extensions. The tests validate the
local execution contract; they do not establish production-scale distributed
reliability or validate new upstream model families.
