# Pending Changes Review: September 10, 2026

Historical review snapshot. The subsequent
[Bugfix Validation](bugfix_validation_2026-09-10.md) addresses the remaining
calibration/reference gaps and additional defects after publication was paused.
Its test counts and behavior supersede this snapshot for the working tree.

Scope: the entire uncommitted change set, including the inherited AI changes
and the new research campaign. Existing work was preserved; no commit or push
was performed. This is a code and execution review, not scientific verification.

## Findings Fixed

| Priority | Finding | Correction and regression evidence |
|---|---|---|
| P1 | A verified row with NaN uncertainty, negative uncertainty, infinite energy, or an unsupported unit could be labeled eligible for scoring. NaN thresholds also passed the margin comparison. | Energy gates now reject invalid measurements; report thresholds must be finite and non-negative even with no verified records. The shared abstention helper rejects non-finite inputs. Threshold units and values are recorded. Tests: `test_energy_verification.py`, `test_calibrated_abstention.py`. |
| P2 | The neighbor-list path used the first periodic image of an atom pair rather than the closest, missing a 0.3-Angstrom short contact. Its cutoff also excluded custom short-contact thresholds above the bond threshold. | Retain the minimum distance across images, order pairs deterministically, and cover both cutoffs. Dense and neighbor paths now agree on the reproduced examples. Tests: `test_local_geometry.py`. |
| P2 | CCDC splitting still interpreted a line beginning `data_` inside multiline prose as a new structure. Space-group normalization could rewrite prose too. | Respect semicolon-delimited text while splitting and normalizing. Normalization and its provenance share one implementation. Tests: `test_ccdc.py`. |
| P2 | Block extraction normalized CIF spellings before provenance collection, leaving an empty normalization list in the inference result. | Preserve normalization history from the original selected block, with and without the explicit repair flag. Tests: `test_run_structure_inference.py`. |
| P2 | A worker could return a list instead of a conformer object, be saved as successful, and then crash final evidence-packet generation. | Validate nested measurement object types before recording success. Malformed results become failed attempts. Tests: `test_research_campaign.py`. |
| P2 | Whitespace-only citations satisfied the promotion presence check. | Require an actual nonblank citation string and normalize citation whitespace on record construction. Tests: `test_cposs_promotion.py`. |
| P3 | Windows path separators were interpreted differently by the filename helper on POSIX. | Normalize both separator conventions before selecting the filename component. Tests: `test_paths.py`. |

The first regression run reproduced 12 failing cases across the energy,
geometry, CIF, and worker-result boundaries. Two additional CLI tests reproduced
the lost extraction provenance before its correction.

The rest of the pending changes were inspected for integration and claim
boundaries: prediction loaders and coverage metrics, adapter scope and charge
handling, CPOSS promotion, molecule QA and viewer URL guards, campaign planning,
hash-validated reuse, locking/recovery, optional Prefect flow, packaging, CI,
and public documentation. This does not assert the absence of undiscovered bugs.

## Verification

| Check | Result |
|---|---|
| Scientific environment full suite | 357 passed, 1 skipped |
| Base environment full suite | 339 passed, 7 skipped |
| Modern conformer dependencies, isolated environment full suite | 357 passed, 1 skipped |
| Isolated environment `pip check` | No broken requirements |
| Expanded scientific CI contract set, executed locally | 57 passed |
| Ruff | Passed |
| Existing mypy typed-core gate | Passed, 27 source files |
| Git whitespace check | Passed |

CI now includes ASE geometry and optional-adapter/molecule-QA tests in its
scientific dependency job. Minimal installations skip some scientific tests;
they are not a substitute for that job. Linux and Python 3.12 CI have not been
executed remotely during this review. The mypy gate remains scoped and does not
cover every new campaign module.

The existing scientific environment uses `rdkit-pypi 2022.9.5` and NumPy 1.26.4.
To test the pending dependency modernization rather than assume compatibility,
`.[dev,conformer]` and `ase>=3.23` were installed in the separate orchestration
environment. It resolved RDKit 2026.3.6, NumPy 2.4.6, and ASE 3.29.0. The modern
suite above runs there; the established MACE environment was not upgraded.

## Post-review Execution Receipts

| Campaign | Outcome | Run ID |
|---|---|---|
| `review_panel_20260910` | 85 conformer jobs succeeded, about 70 seconds | `03717e55155244d5b1078b9406cbf693` |
| Same panel, repeated | 85 cached, zero worker jobs | `e4f1314fb3024621b95d8b5eddef9275` |
| `review_mace_20260910` | Two conformers and two pinned MACE-OFF23 small jobs succeeded, about 20 seconds | `0f41b9ad08c549159268da4f25871cda` |
| Same MACE pilot, repeated | Four cached, zero worker jobs | `d928500075ce407ea6c48c8bd55cc903` |
| `review_modern_rdkit_20260910` | 85 modern-RDKit conformer jobs succeeded, about 65 seconds | `cf486a52ec544143a94e5b9ffebedbab` |
| Same modern panel, repeated | 85 cached, zero worker jobs | `f40f6b94e22d4d14969a67ac08e19823` |

Receipts are in `outputs/campaigns/CAMPAIGN_ID/runs/RUN_ID/evidence_packet.json`
and `.md`. All six have source fingerprint
`ace801f34f857c7e86b5a8c85695d50100d75406970b83e148e5ab89fb1ded5c`,
with no detected source changes during execution. The legacy-RDKit panel retains
UFF non-convergence warnings for cholesterol, glycylglycylglycine, and the long
polyethylene glycol fragment. Successful execution does not erase those warnings.

The modern-RDKit panel retains warnings for cholesterol and the long polyethylene
glycol fragment, but not glycylglycylglycine. This is a version-dependent
convergence observation from one seeded run, not a scientific accuracy or
performance comparison. Both environments preserve total charge and retain
candidate-only status. Use the orchestration environment's Python with the
`review_modern_rdkit_20260910` campaign ID to reproduce that run.

## Remaining Boundaries

- All campaign outputs remain `candidate_unverified`, with zero claim-ready
  records. Human-review fields are attestations, not proof that review occurred.
- A nonzero margin is not evidence of calibration. The default zero conformal
  margin is a heuristic eligibility check. The existing small-sample
  `finite_sample_max_threshold` fallback must not be presented as achieving the
  requested conformal coverage; independent calibration and evaluation data
  remain necessary before a scientific claim.
- Adapter reference/scope metadata does not establish cross-model energy
  comparability. The explicit mixed-reference override and undeclared legacy
  models still require caller judgment and cannot establish calibration.
- The campaign is single-worker; direct-process timeouts do not guarantee
  termination of arbitrary descendants. Symbolic checkpoint results are not
  cached, and execution success is not a validation of model training scope.
- Previously generated public reports and campaign packets are historical.
  Changed source fingerprints intentionally prevent their automatic reuse.

## Reproduce

```powershell
python -B -m pytest --capture=sys -p no:cacheprovider -q
.\.venv\Scripts\python.exe -B -m pytest --capture=sys -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m ruff check src scripts tests
.\.venv\Scripts\python.exe -m mypy
.\.venv\Scripts\python.exe -B scripts/run_molecule_campaign.py --campaign-id review_panel_20260910 --max-jobs 100 --max-seconds 300
```

Repeat the campaign command to check hash-validated reuse. Local outputs remain
under ignored `outputs/`; publication still needs artifact and license review.
