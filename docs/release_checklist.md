# Release Checklist

Use this before tagging any public release.

## Code Release

- [ ] `python -B -m pytest -q -p no:cacheprovider` passes.
- [ ] `crystalprobe doctor` output is included in release notes.
- [ ] Optional adapter failures are documented as expected or fixed.
- [ ] `CITATION.cff` points to the real repository URL.
- [ ] License file is present.

## Benchmark Release

- [ ] No `verified` record contains TODO placeholders.
- [ ] Every `verified` record has DOI or durable URL evidence.
- [ ] Every `verified` record has explicit structure license metadata.
- [ ] Ambiguous records are excluded from headline metrics.
- [ ] Dataset card states known limitations and redistribution terms.

## Paper/Report Release

- [ ] Manifest SHA-256 is reported.
- [ ] Prediction file SHA-256 is reported.
- [ ] Model versions and checkpoint IDs are reported.
- [ ] OOD and uncertainty metrics are reported when available.
- [ ] Limitations section includes missing chemistry slices and licensing boundaries.

