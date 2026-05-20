"""Build evidence-resolution report for a single evidence packet."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.evidence_resolution import evidence_resolution_markdown, evidence_resolution_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=Path("outputs/crystalprobe_evidence_packet.json"))
    parser.add_argument(
        "--candidates",
        type=Path,
        default=Path("data/curation/evidence_resolution_candidates_v0.1.json"),
    )
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_evidence_resolution.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_evidence_resolution.md"))
    args = parser.parse_args()

    report = evidence_resolution_report(
        json.loads(args.packet.read_text(encoding="utf-8")),
        json.loads(args.candidates.read_text(encoding="utf-8")),
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, evidence_resolution_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
