"""Inspect and optionally extract blocks from a local CCDC/CSD CIF export."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

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
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
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
