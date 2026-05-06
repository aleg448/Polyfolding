"""Build a prioritized measurement and curation queue from substance profiles."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.measurement_queue import measurement_queue_markdown, measurement_queue_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", type=Path, default=Path("outputs/crystalprobe_substance_profiles.json"))
    parser.add_argument("--environment-blockers", type=Path, default=Path("outputs/crystalprobe_environment_blockers.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_measurement_queue.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_measurement_queue.md"))
    args = parser.parse_args()

    environment_blockers = (
        json.loads(args.environment_blockers.read_text(encoding="utf-8")) if args.environment_blockers.exists() else None
    )
    report = measurement_queue_report(
        json.loads(args.profiles.read_text(encoding="utf-8")),
        environment_blockers=environment_blockers,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, measurement_queue_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
