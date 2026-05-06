"""Build AGI-assisted CPOSS candidate cards."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
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
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, cposs_candidate_cards_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
