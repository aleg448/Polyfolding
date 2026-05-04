"""Build backend-disagreement metrics from a sensitivity summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

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
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.write_text(backend_disagreement_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
