"""Build a focused CPOSS block-to-form mapping dossier."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.cposs_block_mapping import (
    cposs_block_mapping_dossier,
    cposs_block_mapping_dossier_markdown,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--block-mapping", type=Path, default=Path("outputs/cposs_block_form_mapping.json"))
    parser.add_argument("--block-id", default=None)
    parser.add_argument("--json-out", type=Path, default=Path("outputs/cposs_block_mapping_dossier.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/cposs_block_mapping_dossier.md"))
    args = parser.parse_args()

    dossier = cposs_block_mapping_dossier(
        json.loads(args.block_mapping.read_text(encoding="utf-8")),
        block_id=args.block_id,
    )
    atomic_write_json(args.json_out, dossier)
    atomic_write_text(args.md_out, cposs_block_mapping_dossier_markdown(dossier))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
