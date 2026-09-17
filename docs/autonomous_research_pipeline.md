# Autonomous Research Pipeline

Implementation and technology review: September 10, 2026.

For test results, actual campaign outcomes, and local receipt locations, see
[Campaign Validation](campaign_validation_2026-09-10.md).
For the subsequent audit of all pending changes, reproduced defects, and
updated tests, see [Pending Changes Review](pending_changes_review_2026-09-10.md).
The September 10 no-push bugfix pass and API compatibility changes are recorded in
[Bugfix Validation](bugfix_validation_2026-09-10.md).
For the subsequently authorized pre-push checks and calibration-report fix, see
[September 16 Review Validation](review_validation_2026-09-16.md).

CrystalProbe now has a bounded, resumable molecule campaign in addition to its
existing report-building research cycle. The campaign generates conformers,
optionally executes scientific backends, preserves experiment attempts, and
emits evidence packets. All campaign results remain `candidate_unverified`.

## Run the campaign

From the repository root, using the RDKit-enabled environment:

```powershell
.\.venv\Scripts\python.exe scripts/run_molecule_campaign.py --campaign-id molecule_qa --max-jobs 100 --max-seconds 300
```

This processes the existing stress catalog and CSV panel (85 unique molecule
IDs at implementation time). The default runs conformer generation only. Repeat
the same command to resume; completed tasks are reused only after their inputs,
source code, Python environment, and output hashes are checked.

For a small real-backend campaign:

```powershell
.\.venv\Scripts\python.exe scripts/run_molecule_campaign.py --campaign-id mace_pilot --limit 2 --backends mace --max-jobs 4 --max-seconds 180
```

Pass `--mace-checkpoint PATH_TO_LOCAL_MODEL` to hash and use a specific checkpoint.
Backend results using symbolic model names are deliberately not cached: the
runner cannot establish that the weights behind a name are unchanged.
Use `--fairchem-python PATH_TO_PYTHON` to route UMA tasks to their isolated runtime.
The current UMA adapter's default is `omc`; generated-molecule runs are software
QA and must not be interpreted as a validated molecular prediction protocol.

`--plan-only` writes a declarative plan without scientific execution. The current
CLI compiles plans from the repository's panel; it does not execute arbitrary
shell commands or plans supplied by a language model.

## Persistent evidence

Each campaign lives in `outputs/campaigns/CAMPAIGN_ID/`:

- `registry.sqlite`: run plans, environment provenance, and task attempts. It is
  persistent and separate from the rebuildable Evidence Atlas.
- `runs/RUN_ID/attempts/ATTEMPT_ID/`: request, result, generated coordinates,
  stdout, and stderr for each attempt. Re-execution creates a new directory.
- `runs/RUN_ID/source.zip`: source code and package configuration used to
  describe the run, including current uncommitted source changes.
- `runs/RUN_ID/evidence_packet.json` and `.md`: outcomes and a follow-up queue
  derived from actual failures, blockers, and warnings.
- `latest.json`: a convenience pointer represented as the latest report copy.

The registry uses an exclusive, process-lifetime SQLite lock in a separate
database to prevent competing workers. A subsequent invocation marks abandoned
running attempts as interrupted. It never deletes historical attempts.

A source change during execution invalidates that invocation's successful
attempts for cache reuse. Avoid editing calculation code during a campaign.

Execution statuses and evidence status are independent. `completed_with_issues`
is an honest research outcome, not permission to promote a record. The CLI
returns exit code 2 for that outcome. `paused` means the invocation exhausted
its budget and can be resumed; it returns 0.

The execution order is a validated directed acyclic graph. Failed prerequisites
block their descendants while independent tasks continue. Direct worker crashes
and timeouts have bounded retries (at most two by default per task per invocation).
Permanent reported failures and missing dependencies are not retried inside the
same invocation. A new invocation may attempt them again.

## Optional Prefect integration

Install the `orchestration` extra (pinned to the tested Prefect 3.8.5) in a separate
environment. The scientific
Python is still selected independently:

```powershell
python -m venv .venv-orchestration
.\.venv-orchestration\Scripts\python.exe -m pip install -e ".[orchestration,dev]"
.\.venv-orchestration\Scripts\python.exe scripts/run_molecule_campaign.py --orchestrator prefect --python .venv/Scripts/python.exe --campaign-id prefect_pilot --limit 2
```

Prefect observes the campaign as a flow. The local registry owns individual task
attempts and cache validation. Flow-result persistence/caching and automatic
flow retries are disabled so a completed flow cannot conceal a changed artifact
or silently multiply the compute budget. Unless explicitly configured otherwise,
Prefect state is stored under `.cache/prefect`; analytics are disabled by default.
This integration does not create a schedule or publish data to Prefect Cloud.

## Scientific corrections

- ASE's unannotated zero charge array no longer overrides an explicitly supplied
  default charge. Non-finite charge values are rejected.
- Generated XYZ headers retain RDKit's formal total charge; the corresponding
  metadata records it too. A real ammonium RDKit-to-ASE test exercises the boundary.
- Verified CPOSS promotion requires a supplied, locked block-to-form mapping,
  explicit boolean disorder annotations, distinct curator/reviewer labels, and
  `human_expert_review: true`.
- A recorded human-review flag is an attestation, not automated proof that a
  review occurred. Source inspection and independent scientific judgment remain
  necessary. The campaign worker itself cannot promote records.

## Technology decisions

These are primary-source technologies assessed on the review date, not a claim
that one model is universally state of the art. Upstream pages are mutable;
capture a tested package version and weight digest for every experiment.

| Technology | Relevant capability | Decision |
|---|---|---|
| Prefect 3 | Task states, retry policies, persistence and workflow observation | Optional flow integration implemented; local scientific artifact checks remain authoritative |
| TorchSim | GPU-batched atomistic simulation and variable-cell/position optimization | Next throughput experiment after a validated single-structure reference; not installed or benchmarked here |
| AIMNetCentral | Periodic electrostatics and charge-aware inference in current upstream APIs | Candidate adapter upgrade; our existing cluster-only path remains explicitly restricted |
| MACE-OMOL | Broader molecular chemistry with charge/spin inputs | Candidate ion/open-shell comparison backend; does not automatically validate MACE-OFF outputs on these systems |
| UMA / FAIRChem | Task-conditioned atomistic predictions | Existing isolated adapter retained; record task and energy reference before comparisons |
| FastCSP | End-to-end crystal candidate generation and ranking | Future producer of candidates for CrystalProbe's audit; not implemented by generating molecular conformers |

Prefect documents that caching needs persisted results and that result storage
does not manage arbitrary files created by application code. This is why we
verify coordinate and result hashes ourselves. [Prefect results](https://docs.prefect.io/v3/advanced/results),
[Prefect tasks](https://docs.prefect.io/v3/concepts/tasks).

TorchSim provides batchable simulation and optimization, including automated
batch sizing. Throughput and numerical agreement must be measured on our own
inputs before replacing the reference path. [TorchSim](https://github.com/torchsim/torch-sim),
[autobatching guide](https://torchsim.github.io/torch-sim/tutorials/autobatching_tutorial.html).

Current AIMNetCentral advertises periodic systems with DSF/Ewald/PME and ASE
integration. This describes upstream capabilities, not the behavior of our
installed `.eval` adapter. [AIMNetCentral](https://github.com/isayevlab/aimnetcentral).

The MACE model table distinguishes neutral-organic MACE-OFF23 from MACE-OMOL's
broader chemistry and charge/spin conditioning. Check model-specific training
scope and licenses before selecting a checkpoint. [MACE model inventory](https://github.com/ACEsuit/mace).

FAIRChem's releases include UMA-S 1.2 and evolving task-specific model support.
FastCSP is an upstream crystal prediction workflow, not an experimental stability
label source. [FAIRChem releases](https://github.com/facebookresearch/fairchem/releases),
[FastCSP paper](https://arxiv.org/abs/2508.02641).

## Limits and next experiments

This is a local, single-worker computational research campaign. It is not yet an
autonomous literature retrieval agent, a distributed scheduler, a crystal
landscape generator, a training pipeline, or an experimental laboratory loop.
The budgets bound direct worker execution; hashing, startup, and report-writing
overhead can add wall time. Worker timeouts do not guarantee termination of
arbitrary descendants; current scientific workers do not intentionally spawn
independent long-lived subprocesses.

The generated follow-up queue is an inspection proposal, not an automatically
executed experiment or a calibrated expected-information-gain estimate.
The next experimental extension should preregister small coordinate/cell
perturbations, compare within-backend ranking stability, and record failure
rates and runtime by molecule class. Keep generated molecules and periodic
crystal comparisons in separate campaigns. Calibration/accuracy claims need
independent reference labels and separate calibration/evaluation sets.

Historical reports under `outputs/` are not refreshed by the new campaign. Use
the run-specific evidence packet to assess these new computations. Public
export still requires source and artifact release review; nothing in this
runner changes coordinate redistribution policy.
