"""Build a backend-ready generated-conformer input manifest."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.backend_ready_inputs import (
    backend_ready_inputs_markdown,
    backend_ready_inputs_report,
    write_backend_ready_inputs_sqlite,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a hashed manifest of generated conformers ready for backends.")
    parser.add_argument(
        "--conformer-report",
        type=Path,
        default=Path("outputs/local_conformer_generation_with_xyz.json"),
        help="Conformer-generation JSON report with local XYZ payload paths.",
    )
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_backend_ready_inputs.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_backend_ready_inputs.md"))
    parser.add_argument("--sqlite-out", type=Path, default=Path("outputs/crystalprobe_backend_ready_inputs.sqlite"))
    parser.add_argument("--docs-out", type=Path, default=Path("docs/backend_ready_inputs.md"))
    args = parser.parse_args()

    conformer_report = json.loads(args.conformer_report.read_text(encoding="utf-8"))
    report = backend_ready_inputs_report(
        conformer_report,
        source_report_path=args.conformer_report,
        base_dir=Path.cwd(),
    )
    markdown = backend_ready_inputs_markdown(report)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, markdown)
    atomic_write_text(args.docs_out, markdown)
    write_backend_ready_inputs_sqlite(report, args.sqlite_out)
    print(
        json.dumps(
            {
                "json": str(args.json_out),
                "markdown": str(args.md_out),
                "sqlite": str(args.sqlite_out),
                "docs": str(args.docs_out),
                "ready": report["counts"]["ready_count"],
                "warnings": report["counts"]["warning_count"],
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
