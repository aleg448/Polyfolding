"""Build the first real backend result table from backend smoke rows."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.backend_result_table import (
    backend_result_table_markdown,
    backend_result_table_report,
    write_backend_result_table_sqlite,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the first actual generated-conformer backend result table.")
    parser.add_argument("--backend-smoke", type=Path, default=Path("outputs/crystalprobe_backend_smoke.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_backend_result_table.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_backend_result_table.md"))
    parser.add_argument("--sqlite-out", type=Path, default=Path("outputs/crystalprobe_backend_result_table.sqlite"))
    parser.add_argument("--docs-out", type=Path, default=Path("docs/backend_result_table.md"))
    args = parser.parse_args()

    report = backend_result_table_report(json.loads(args.backend_smoke.read_text(encoding="utf-8")))
    markdown = backend_result_table_markdown(report)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, markdown)
    atomic_write_text(args.docs_out, markdown)
    write_backend_result_table_sqlite(report, args.sqlite_out)
    print(
        json.dumps(
            {
                "json": str(args.json_out),
                "markdown": str(args.md_out),
                "sqlite": str(args.sqlite_out),
                "docs": str(args.docs_out),
                "rows": report["counts"]["row_count"],
                "passed": report["counts"]["passed_count"],
                "blocked": report["counts"]["blocked_count"],
                "claim_ready": report["counts"]["claim_ready_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
