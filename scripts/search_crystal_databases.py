"""Search open crystallographic databases for target structures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.datahub.cod import lisdexamfetamine_cod_queries, query_cod


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["lisdexamfetamine"], default="lisdexamfetamine")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    if args.target != "lisdexamfetamine":
        raise ValueError(f"unsupported target: {args.target}")

    query_results = []
    for query in lisdexamfetamine_cod_queries():
        rows = query_cod(query, timeout=args.timeout)
        query_results.append(
            {
                "query": query.as_dict(),
                "hit_count": len(rows),
                "hits": rows[:25],
                "truncated": len(rows) > 25,
            }
        )

    report = {
        "target": args.target,
        "databases": {
            "cod": {
                "license": "CC0/public domain according to COD site",
                "results": query_results,
            },
            "ccdc_access_structures": {
                "status": "manual_or_api_access_required",
                "reason": "Public Access Structures page requires human validation/terms; systematic access should use the CSD System/Python API.",
            },
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(args.output), "cod_queries": len(query_results)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
