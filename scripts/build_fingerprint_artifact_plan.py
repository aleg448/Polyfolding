"""Build a readiness plan for fingerprint-paper figures and calibration."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.fingerprint_artifacts import fingerprint_artifact_plan, fingerprint_artifact_plan_markdown


def _load_optional(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--promotion-gate", type=Path, default=Path("outputs/cposs_promotion_gate.json"))
    parser.add_argument("--medication-measurements", type=Path, default=Path("outputs/medication_measurement_summary.json"))
    parser.add_argument("--medication-figure", type=Path, default=Path("outputs/figures/medication_case_study_coverage.svg"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_fingerprint_artifact_plan.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_fingerprint_artifact_plan.md"))
    args = parser.parse_args()

    report = fingerprint_artifact_plan(
        promotion_gate=_load_optional(args.promotion_gate),
        medication_measurements=_load_optional(args.medication_measurements),
        generated_figures={
            "medication_case_studies": str(args.medication_figure)
        }
        if args.medication_figure.exists()
        else {},
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, fingerprint_artifact_plan_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
