"""Build AMPETP versus ibuprofen perturbation-sensitivity contrast reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.contrast import build_sensitivity_contrast_report, sensitivity_contrast_markdown


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ampetp", type=Path, default=Path("outputs/ampetp_sensitivity_summary.json"))
    parser.add_argument("--ibuprofen", type=Path, default=Path("outputs/ibuprofen_sensitivity_summary_mace.json"))
    parser.add_argument("--backend", default="mace")
    parser.add_argument("--json-out", type=Path, default=Path("outputs/therapeutic_sensitivity_contrast_mace.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/therapeutic_sensitivity_contrast_mace.md"))
    args = parser.parse_args()

    report = build_sensitivity_contrast_report(
        title="Therapeutic crystal perturbation sensitivity contrast",
        backend=args.backend,
        targets=[
            {"name": "AMPETP CCDC 1102740", "summary": json.loads(args.ampetp.read_text(encoding="utf-8"))},
            {"name": "Ibuprofen CCDC 774097", "summary": json.loads(args.ibuprofen.read_text(encoding="utf-8"))},
        ],
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(sensitivity_contrast_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
