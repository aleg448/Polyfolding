"""Build FAIR Chemistry model-scope guardrail report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.model_guardrails import fairchem_guardrail_markdown, fairchem_guardrail_report


DEFAULT_REPOS = ["facebook/UMA", "facebook/OMC25", "facebook/OMAT24", "facebook/OMol25"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", action="append", default=[])
    parser.add_argument("--json-out", type=Path, default=Path("outputs/fairchem_model_guardrails.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/fairchem_model_guardrails.md"))
    args = parser.parse_args()

    report = fairchem_guardrail_report(args.repo_id or DEFAULT_REPOS)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(fairchem_guardrail_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
