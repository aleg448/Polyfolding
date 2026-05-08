"""Build curator-fillable evidence workpacks from CPOSS pair triage."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.cposs_pairs import cposs_evidence_workpack, cposs_evidence_workpack_markdown


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage", type=Path, default=Path("outputs/cposs_pair_triage_report.json"))
    parser.add_argument("--evidence-overrides", type=Path, default=Path("data/curation/cposs_evidence_overrides_v0.1.json"))
    parser.add_argument("--max-candidates", type=int, default=None)
    parser.add_argument("--json-out", type=Path, default=Path("outputs/cposs_evidence_workpack.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/cposs_evidence_workpack.md"))
    args = parser.parse_args()

    evidence_overrides = {}
    if args.evidence_overrides.exists():
        evidence_overrides = json.loads(args.evidence_overrides.read_text(encoding="utf-8"))

    report = cposs_evidence_workpack(
        json.loads(args.triage.read_text(encoding="utf-8")),
        max_candidates=args.max_candidates,
        evidence_overrides=evidence_overrides,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, cposs_evidence_workpack_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
