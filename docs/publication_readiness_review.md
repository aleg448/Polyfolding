# CrystalProbe Publication Readiness Review

Date: 2026-06-10

This review covers the current all-molecule QA, backend-result, release-boundary, and publication-readiness state after the backend result table and molecule bug dashboard work.

## Current Decision

CrystalProbe is ready for a draft code-and-methods review. It is not ready for public release of CCDC/CSD-derived scientific artifacts, raw coordinate-bearing local files, or headline polymorph benchmark claims.

The strongest review story is now reliability infrastructure: deterministic report generators, explicit claim gates, candidate-safe viewer links, all-molecule parser/conformer/backend QA, and consistency checks that keep generated summaries aligned.

## Evidence Reviewed

- `outputs/crystalprobe_release_boundary.md`
- `outputs/crystalprobe_publication_readiness.md`
- `outputs/crystalprobe_report_consistency.md`
- `outputs/crystalprobe_backend_result_table.md`
- `outputs/crystalprobe_molecule_bug_dashboard.md`
- `outputs/crystalprobe_backend_smoke.md`
- `outputs/crystalprobe_backend_ready_inputs.md`
- `outputs/crystalprobe_conformer_generation.md`
- `outputs/crystalprobe_tentative_molecule_benchmark.md`
- `docs/backend_result_table.md`
- `docs/molecule_bug_dashboard.md`
- `CASE_STUDY.md`
- `README.md`

## Release Boundary Findings

- Candidate-public artifacts: `242`.
- License-review-required artifacts: `57`.
- Local-only artifacts: `1`.
- The local-only artifact is `outputs/ccdc_ampetp_extracted.cif`; it must stay out of Git and public archives unless the CCDC/CSD license explicitly permits redistribution.
- Generated CCDC/CSD-derived reports, figures, manifests, and local measurement summaries remain `license_review_required`.
- Backend-ready input manifests, backend smoke/result tables, molecule bug dashboards, molecule bug-hunt databases, and tentative molecule benchmark databases are classified as `candidate_public` because they contain normalized metadata, QA fixtures, hashes, claim gates, links, and release categories without raw gated-coordinate payloads.
- The release-boundary report is conservative enough for internal publication planning, but it is not a legal review.

## Publication Gates

| Gate | Decision | Reason |
|---|---|---|
| Code-and-methods review | Go | The source tree is clean, the latest commit is coherent, and tests passed in both tracked Python runtimes. |
| Public artifact/demo review | Go with guardrails | Public docs and copied assets are candidate-safe, but generated outputs still need release-boundary review before sharing as a package. |
| Backend QA review | Go | The 85-molecule dashboard exposes parser, conformer, backend, energy/force sanity, and issue-signature state without promoting scientific claims. |
| First backend result table | Go as execution evidence | 170 backend rows are reported, with 83 passed, 85 blocked, 2 failed, and 0 claim-ready rows. |
| AIMNet2 Windows execution | Blocked | Rows consistently record `backend_missing_windows_cpp_compiler`; this is an environment blocker, not a chemistry result. |
| MACE salt/ion edge cases | Investigate | `sodium_chloride` and `sodium_acetate` show `backend_execution_exception`; these are useful QA targets. |
| Public release of CCDC/CSD-derived artifacts | Hold | `57` artifacts require human source-license review. |
| Public release of raw or extracted CCDC/CSD CIFs | No-go | Coordinate-bearing local-only artifacts must remain excluded unless redistribution is explicitly allowed. |
| CPOSS benchmark claims | No-go | Verified-pair milestone is still `0` of `20`; candidate rows lack complete experimental stability and review evidence. |
| Cross-backend thermodynamic claims | No-go | MACE, AIMNet2, and UMA absolute energies are not a shared thermodynamic scale without calibration. |

## Interesting Current Findings

- The all-molecule panel is useful because it catches software and environment failure modes before they can become scientific claims.
- RDKit parsing is currently robust across the 85-molecule QA panel, while conformer generation surfaces two UFF non-convergence warnings.
- MACE produced usable smoke rows for most generated conformers, but salts/ions exposed two execution exceptions that deserve targeted debugging.
- AIMNet2 is blocked uniformly on this Windows run by missing C++ compiler support, which is a clean environment finding rather than an ambiguous model failure.
- The report consistency gate currently reports `reports_consistent` with `0` blocked checks, aligning test summaries, release-boundary counts, publication gate counts, and status-chain ordering.

## Required Before Public Publication

1. Complete human license review for every `license_review_required` artifact planned for sharing.
2. Keep raw CCDC files, extracted coordinate CIFs, and other `local_only` coordinate-bearing artifacts out of Git and public archives.
3. Promote no CPOSS candidate into benchmark status until experimental stability ordering, DOI or durable URL, license decisions, disorder annotations, curator, reviewer, and block-form mapping are complete.
4. Re-run release-boundary, publication-readiness, status-chain, handoff, and report-consistency reports after any artifact or status change.
5. Re-run tests in both Python runtimes before tagging, pushing a review bundle, or opening a PR.
6. Treat backend smoke/result rows as execution evidence only; do not infer scientific validity from passed backend execution.

## Immediate Recommended Order

1. Send the current branch for draft code-and-methods review.
2. Ask reviewers to start with `CASE_STUDY.md`, `README.md`, `docs/backend_result_table.md`, `docs/molecule_bug_dashboard.md`, and this readiness review.
3. For the next technical milestone, debug the two MACE salt/ion exceptions and then rerun `scripts\build_backend_smoke_report.py --all --backends mace aimnet2`.
4. For the next scientific milestone, curate one CPOSS candidate through block-form mapping and source review without promoting it until the full claim gate passes.
