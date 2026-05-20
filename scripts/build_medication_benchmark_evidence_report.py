"""Build medication polymorphism evidence-dossier gate reports."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.medication_benchmark_evidence import (
    medication_benchmark_evidence_markdown,
    medication_benchmark_evidence_report,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--autonomy", type=Path, default=Path("outputs/medication_polymorphism_autonomy.json"))
    parser.add_argument("--evidence", type=Path, default=Path("data/curation/medication_polymorphism_evidence_v0.1.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/medication_benchmark_evidence.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/medication_benchmark_evidence.md"))
    args = parser.parse_args()

    evidence = json.loads(args.evidence.read_text(encoding="utf-8")) if args.evidence.exists() else {}
    report = medication_benchmark_evidence_report(
        json.loads(args.autonomy.read_text(encoding="utf-8")),
        evidence,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, medication_benchmark_evidence_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
