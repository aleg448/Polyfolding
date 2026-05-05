"""Build a CrystalProbe source-discovery report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.source_discovery import source_discovery_markdown, source_discovery_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", type=Path, default=Path("data/curation/source_discovery_targets_v0.1.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_source_discovery.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_source_discovery.md"))
    args = parser.parse_args()

    report = source_discovery_report(json.loads(args.targets.read_text(encoding="utf-8")))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(source_discovery_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
