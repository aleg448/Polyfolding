"""Build a CrystalProbe source-acquisition report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.source_acquisition import source_acquisition_markdown, source_acquisition_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempts", type=Path, default=Path("data/curation/source_acquisition_attempts_v0.1.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_source_acquisition.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_source_acquisition.md"))
    args = parser.parse_args()

    report = source_acquisition_report(json.loads(args.attempts.read_text(encoding="utf-8")))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(source_acquisition_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
