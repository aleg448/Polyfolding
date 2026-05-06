"""Build deterministic medication case-study figures."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.insight.figures import medication_case_study_svg, write_svg


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--measurement-summary", type=Path, default=Path("outputs/medication_measurement_summary.json"))
    parser.add_argument("--output", type=Path, default=Path("outputs/figures/medication_case_study_coverage.svg"))
    args = parser.parse_args()

    summary = json.loads(args.measurement_summary.read_text(encoding="utf-8"))
    write_svg(args.output, medication_case_study_svg(summary))
    print(json.dumps({"figure": str(args.output)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
