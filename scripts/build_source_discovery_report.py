"""Build a CrystalProbe source-discovery report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.source_discovery import source_discovery_markdown, source_discovery_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", type=Path, default=Path("data/curation/source_discovery_targets_v0.1.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_source_discovery.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_source_discovery.md"))
    args = parser.parse_args()

    report = source_discovery_report(json.loads(args.targets.read_text(encoding="utf-8")))
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, source_discovery_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
