"""Build deterministic medication case-study figures."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.insight.figures import medication_case_study_svg, medication_stereochemistry_svg, write_svg


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--measurement-summary", type=Path, default=Path("outputs/medication_measurement_summary.json"))
    parser.add_argument("--stereochemistry", type=Path, default=Path("outputs/medication_stereochemistry.json"))
    parser.add_argument("--case-study-output", type=Path, default=Path("outputs/figures/medication_case_study_coverage.svg"))
    parser.add_argument("--stereochemistry-output", type=Path, default=Path("outputs/figures/medication_stereochemistry_scope.svg"))
    args = parser.parse_args()

    summary = json.loads(args.measurement_summary.read_text(encoding="utf-8"))
    outputs = {"case_study_figure": str(args.case_study_output)}
    write_svg(args.case_study_output, medication_case_study_svg(summary))
    if args.stereochemistry.exists():
        stereochemistry = json.loads(args.stereochemistry.read_text(encoding="utf-8"))
        write_svg(args.stereochemistry_output, medication_stereochemistry_svg(stereochemistry))
        outputs["stereochemistry_figure"] = str(args.stereochemistry_output)
    print(json.dumps(outputs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
