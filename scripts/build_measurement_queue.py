"""Build a prioritized measurement and curation queue from substance profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.measurement_queue import measurement_queue_markdown, measurement_queue_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", type=Path, default=Path("outputs/crystalprobe_substance_profiles.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_measurement_queue.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_measurement_queue.md"))
    args = parser.parse_args()

    report = measurement_queue_report(json.loads(args.profiles.read_text(encoding="utf-8")))
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(measurement_queue_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
