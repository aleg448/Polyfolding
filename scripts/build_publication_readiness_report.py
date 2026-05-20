"""Build a conservative publication-readiness gate report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.publication import publication_readiness_markdown, publication_readiness_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cposs-promotion", type=Path, default=Path("outputs/cposs_promotion_gate.json"))
    parser.add_argument("--cposs-block-mapping", type=Path, default=Path("outputs/cposs_block_form_mapping.json"))
    parser.add_argument("--fingerprint-plan", type=Path, default=Path("outputs/crystalprobe_fingerprint_artifact_plan.json"))
    parser.add_argument("--release-boundary", type=Path, default=Path("outputs/crystalprobe_release_boundary.json"))
    parser.add_argument("--execution-unblock", type=Path, default=Path("outputs/crystalprobe_execution_unblock_report.json"))
    parser.add_argument("--handoff", type=Path, default=Path("outputs/crystalprobe_handoff_summary.json"))
    parser.add_argument("--medication-stereochemistry-dossier", type=Path, default=Path("outputs/medication_stereochemistry_dossier.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_publication_readiness.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_publication_readiness.md"))
    args = parser.parse_args()

    report = publication_readiness_report(
        cposs_promotion=json.loads(args.cposs_promotion.read_text(encoding="utf-8")),
        cposs_block_mapping=json.loads(args.cposs_block_mapping.read_text(encoding="utf-8"))
        if args.cposs_block_mapping.exists()
        else None,
        fingerprint_plan=json.loads(args.fingerprint_plan.read_text(encoding="utf-8")),
        release_boundary=json.loads(args.release_boundary.read_text(encoding="utf-8")),
        execution_unblock=json.loads(args.execution_unblock.read_text(encoding="utf-8")),
        handoff=json.loads(args.handoff.read_text(encoding="utf-8")),
        medication_stereochemistry_dossier=(
            json.loads(args.medication_stereochemistry_dossier.read_text(encoding="utf-8"))
            if args.medication_stereochemistry_dossier.exists()
            else None
        ),
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, publication_readiness_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
