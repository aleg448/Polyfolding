"""Build backend-disagreement metrics from a sensitivity summary."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.backend_disagreement import backend_disagreement_markdown, backend_disagreement_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, default=Path("outputs/ampetp_sensitivity_summary.json"))
    parser.add_argument("--title", default="AMPETP backend disagreement report")
    parser.add_argument("--json-out", type=Path, default=Path("outputs/ampetp_backend_disagreement.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/ampetp_backend_disagreement.md"))
    args = parser.parse_args()

    report = backend_disagreement_report(
        json.loads(args.summary.read_text(encoding="utf-8")),
        title=args.title,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, backend_disagreement_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
