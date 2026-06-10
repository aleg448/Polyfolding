# Release Checklist

Use this before tagging any public release.

## Code Release

- [ ] `python -m pytest -q` passes in the base Python runtime.
- [ ] `.\.venv\Scripts\python.exe -m pytest -q` passes in the RDKit-enabled project runtime.
- [ ] `python -m compileall -q src scripts tests` passes.
- [ ] `crystalprobe doctor` or `python -m crystalprobe.benchmark.cli doctor` output is included in release notes.
- [ ] Optional adapter failures are documented as expected or fixed.
- [ ] `CITATION.cff` points to the real repository URL.
- [ ] License file is present.
- [ ] `git status --short --branch` is clean except for an intentional review branch ahead of origin.

## Benchmark Release

- [ ] No `verified` record contains TODO placeholders.
- [ ] Every `verified` record has DOI or durable URL evidence.
- [ ] Every `verified` record has explicit structure license metadata.
- [ ] Ambiguous records are excluded from headline metrics.
- [ ] Dataset card states known limitations and redistribution terms.

## Paper/Report Release

- [ ] `python scripts\build_release_boundary_report.py` has been re-run after artifact changes.
- [ ] `python scripts\build_publication_readiness_report.py` has been re-run after release-boundary changes.
- [ ] `python scripts\build_report_consistency_report.py` reports `reports_consistent`.
- [ ] `python scripts\check_public_artifact.py` passes before publishing public-facing docs or assets.
- [ ] Manifest SHA-256 is reported.
- [ ] Prediction file SHA-256 is reported.
- [ ] Model versions and checkpoint IDs are reported.
- [ ] OOD and uncertainty metrics are reported when available.
- [ ] Limitations section includes missing chemistry slices and licensing boundaries.
- [ ] CCDC/CSD-derived reports, figures, manifests, and measurements marked `license_review_required` have human license review before public sharing.
- [ ] Raw, extracted, or generated coordinate-bearing CCDC/CSD files marked `local_only` are excluded from public archives.
