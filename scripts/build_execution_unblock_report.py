"""Build a combined execution unblock report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.unblock import execution_unblock_markdown, execution_unblock_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment-blockers", type=Path, default=Path("outputs/crystalprobe_environment_blockers.json"))
    parser.add_argument("--backend-blockers", type=Path, default=Path("data/curation/medication_backend_blockers_v0.1.json"))
    parser.add_argument("--measurement-queue", type=Path, default=Path("outputs/crystalprobe_measurement_queue.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_execution_unblock_report.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_execution_unblock_report.md"))
    args = parser.parse_args()

    report = execution_unblock_report(
        environment_blockers=json.loads(args.environment_blockers.read_text(encoding="utf-8")),
        medication_backend_blockers=json.loads(args.backend_blockers.read_text(encoding="utf-8")),
        measurement_queue=json.loads(args.measurement_queue.read_text(encoding="utf-8")) if args.measurement_queue.exists() else None,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, execution_unblock_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
