"""Build the CPOSS promotion burn-down report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.cposs_burndown import cposs_promotion_burndown_markdown, cposs_promotion_burndown_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--promotion", type=Path, default=Path("outputs/cposs_promotion_gate.json"))
    parser.add_argument("--block-mapping", type=Path, default=Path("outputs/cposs_block_form_mapping.json"))
    parser.add_argument("--target-pair-count", type=int, default=20)
    parser.add_argument("--json-out", type=Path, default=Path("outputs/cposs_promotion_burndown.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/cposs_promotion_burndown.md"))
    args = parser.parse_args()

    report = cposs_promotion_burndown_report(
        json.loads(args.promotion.read_text(encoding="utf-8")),
        json.loads(args.block_mapping.read_text(encoding="utf-8")),
        target_pair_count=args.target_pair_count,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, cposs_promotion_burndown_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
