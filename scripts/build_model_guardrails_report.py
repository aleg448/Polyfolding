"""Build FAIR Chemistry model-scope guardrail report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.model_guardrails import fairchem_guardrail_markdown, fairchem_guardrail_report


DEFAULT_REPOS = ["facebook/UMA", "facebook/OMC25", "facebook/OMAT24", "facebook/OMol25"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", action="append", default=[])
    parser.add_argument("--json-out", type=Path, default=Path("outputs/fairchem_model_guardrails.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/fairchem_model_guardrails.md"))
    args = parser.parse_args()

    report = fairchem_guardrail_report(args.repo_id or DEFAULT_REPOS)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, fairchem_guardrail_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
