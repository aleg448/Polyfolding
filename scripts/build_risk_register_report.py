"""Build the CrystalProbe consolidated risk register."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.risk import risk_register_markdown, risk_register_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publication-readiness", type=Path, default=Path("outputs/crystalprobe_publication_readiness.json"))
    parser.add_argument("--release-boundary", type=Path, default=Path("outputs/crystalprobe_release_boundary.json"))
    parser.add_argument("--cposs-promotion", type=Path, default=Path("outputs/cposs_promotion_gate.json"))
    parser.add_argument("--cposs-block-mapping", type=Path, default=Path("outputs/cposs_block_form_mapping.json"))
    parser.add_argument("--cposs-promotion-burndown", type=Path, default=Path("outputs/cposs_promotion_burndown.json"))
    parser.add_argument("--fingerprint-plan", type=Path, default=Path("outputs/crystalprobe_fingerprint_artifact_plan.json"))
    parser.add_argument("--medication-stereochemistry", type=Path, default=Path("outputs/medication_stereochemistry.json"))
    parser.add_argument("--medication-stereochemistry-dossier", type=Path, default=Path("outputs/medication_stereochemistry_dossier.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_risk_register.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_risk_register.md"))
    args = parser.parse_args()

    report = risk_register_report(
        publication_readiness=json.loads(args.publication_readiness.read_text(encoding="utf-8")),
        release_boundary=json.loads(args.release_boundary.read_text(encoding="utf-8")),
        cposs_promotion=json.loads(args.cposs_promotion.read_text(encoding="utf-8")),
        cposs_block_mapping=json.loads(args.cposs_block_mapping.read_text(encoding="utf-8")),
        cposs_promotion_burndown=json.loads(args.cposs_promotion_burndown.read_text(encoding="utf-8")) if args.cposs_promotion_burndown.exists() else {},
        fingerprint_plan=json.loads(args.fingerprint_plan.read_text(encoding="utf-8")),
        medication_stereochemistry=json.loads(args.medication_stereochemistry.read_text(encoding="utf-8")) if args.medication_stereochemistry.exists() else {},
        medication_stereochemistry_dossier=json.loads(args.medication_stereochemistry_dossier.read_text(encoding="utf-8")) if args.medication_stereochemistry_dossier.exists() else {},
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, risk_register_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
