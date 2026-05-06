"""Search open crystallographic databases for target structures."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json
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
    atomic_write_json(args.output, report)
    print(json.dumps({"output": str(args.output), "cod_queries": len(query_results)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
