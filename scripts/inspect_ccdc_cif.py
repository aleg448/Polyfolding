"""Inspect and optionally extract blocks from a local CCDC/CSD CIF export."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json
from crystalprobe.datahub.ccdc import split_ccdc_cif, summarize_ccdc_blocks, write_ccdc_block


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cif", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--extract-block")
    parser.add_argument("--extract-index", type=int)
    parser.add_argument("--extract-out", type=Path)
    args = parser.parse_args()

    blocks = split_ccdc_cif(args.cif)
    report = {
        "source": str(args.cif),
        "summary": summarize_ccdc_blocks(blocks),
        "blocks": [block.as_dict() for block in blocks],
    }
    if args.json_out:
        atomic_write_json(args.json_out, report)
    if args.extract_out:
        selected = write_ccdc_block(
            args.cif,
            args.extract_out,
            block_id=args.extract_block,
            index=args.extract_index,
        )
        report["extracted"] = {"block_id": selected.block_id, "output": str(args.extract_out)}
    print(json.dumps(report["summary"] | ({"extracted": report.get("extracted")} if "extracted" in report else {}), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
