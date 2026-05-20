"""Build medication polymorph generation readiness reports."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.medication_generation import (
    medication_polymorph_generation_markdown,
    medication_polymorph_generation_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--autonomy", type=Path, default=Path("outputs/medication_polymorphism_autonomy.json"))
    parser.add_argument("--benchmark-evidence", type=Path, default=Path("outputs/medication_benchmark_evidence.json"))
    parser.add_argument("--extraction", type=Path, default=Path("outputs/medication_selected_block_extraction.json"))
    parser.add_argument("--evidence", type=Path, default=Path("data/curation/medication_polymorphism_evidence_v0.1.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/medication_polymorph_generation.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/medication_polymorph_generation.md"))
    args = parser.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8")) if args.evidence.exists() else {}
    report = medication_polymorph_generation_report(
        json.loads(args.autonomy.read_text(encoding="utf-8")),
        json.loads(args.benchmark_evidence.read_text(encoding="utf-8")),
        json.loads(args.extraction.read_text(encoding="utf-8")),
        evidence,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, medication_polymorph_generation_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
