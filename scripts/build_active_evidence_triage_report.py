"""Build active evidence triage from the benchmark manifest."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.benchmark.dataset import load_manifest
from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.active_evidence_triage import (
    active_evidence_triage_markdown,
    active_evidence_triage_report,
    triage_items_from_pairs,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data/benchmark/v0.1/manifest.jsonl"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_active_evidence_triage.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_active_evidence_triage.md"))
    args = parser.parse_args()

    dataset = load_manifest(args.manifest)
    report = active_evidence_triage_report(triage_items_from_pairs(dataset.pairs))
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, active_evidence_triage_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
