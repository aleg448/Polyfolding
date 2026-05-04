"""Build AGI-assisted CPOSS candidate cards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.insight.cposs_pairs import cposs_candidate_cards, cposs_candidate_cards_markdown


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--triage", type=Path, default=Path("outputs/cposs_pair_triage_report.json"))
    parser.add_argument("--max-candidates", type=int, default=None)
    parser.add_argument("--json-out", type=Path, default=Path("outputs/cposs_candidate_cards.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/cposs_candidate_cards.md"))
    args = parser.parse_args()

    report = cposs_candidate_cards(
        json.loads(args.triage.read_text(encoding="utf-8")),
        max_candidates=args.max_candidates,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.write_text(cposs_candidate_cards_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
