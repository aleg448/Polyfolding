"""Build a ChemRxiv-style draft from local CrystalProbe reports."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_text
from crystalprobe.insight.preprint import chemrxiv_preprint_draft


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--memo", type=Path, default=Path("outputs/crystalprobe_preliminary_findings_memo.md"))
    parser.add_argument("--readiness", type=Path, default=Path("outputs/ampetp_readiness_report.json"))
    parser.add_argument("--sensitivity", type=Path, default=Path("outputs/ampetp_sensitivity_summary.json"))
    parser.add_argument("--cposs", type=Path, default=Path("outputs/cposs_mini_benchmark_report.json"))
    parser.add_argument("--bundle", type=Path, default=Path("outputs/ampetp_research_bundle_manifest.json"))
    parser.add_argument("--contrast", type=Path, default=Path("outputs/therapeutic_sensitivity_contrast_mace.json"))
    parser.add_argument("--output", type=Path, default=Path("outputs/crystalprobe_chemrxiv_preprint_draft.md"))
    args = parser.parse_args()

    draft = chemrxiv_preprint_draft(
        memo_text=args.memo.read_text(encoding="utf-8"),
        readiness=json.loads(args.readiness.read_text(encoding="utf-8")),
        sensitivity=json.loads(args.sensitivity.read_text(encoding="utf-8")),
        cposs_bridge=json.loads(args.cposs.read_text(encoding="utf-8")),
        bundle_manifest=json.loads(args.bundle.read_text(encoding="utf-8")),
        therapeutic_contrast=json.loads(args.contrast.read_text(encoding="utf-8")) if args.contrast.exists() else None,
    )
    atomic_write_text(args.output, draft)
    print(json.dumps({"draft": str(args.output)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
