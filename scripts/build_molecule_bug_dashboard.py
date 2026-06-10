"""Build the joined molecule bug dashboard."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.molecule_bug_dashboard import (
    molecule_bug_dashboard_markdown,
    molecule_bug_dashboard_report,
    write_molecule_bug_dashboard_sqlite,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a joined molecule-level parser/conformer/backend QA dashboard.")
    parser.add_argument(
        "--tentative-benchmark",
        type=Path,
        default=Path("outputs/crystalprobe_tentative_molecule_benchmark.json"),
    )
    parser.add_argument(
        "--backend-ready-inputs",
        type=Path,
        default=Path("outputs/crystalprobe_backend_ready_inputs.json"),
    )
    parser.add_argument("--backend-smoke", type=Path, default=Path("outputs/crystalprobe_backend_smoke.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_molecule_bug_dashboard.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_molecule_bug_dashboard.md"))
    parser.add_argument("--sqlite-out", type=Path, default=Path("outputs/crystalprobe_molecule_bug_dashboard.sqlite"))
    parser.add_argument("--docs-out", type=Path, default=Path("docs/molecule_bug_dashboard.md"))
    args = parser.parse_args()

    report = molecule_bug_dashboard_report(
        tentative_benchmark=json.loads(args.tentative_benchmark.read_text(encoding="utf-8")),
        backend_ready_inputs=json.loads(args.backend_ready_inputs.read_text(encoding="utf-8")),
        backend_smoke=json.loads(args.backend_smoke.read_text(encoding="utf-8")),
    )
    markdown = molecule_bug_dashboard_markdown(report)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, markdown)
    atomic_write_text(args.docs_out, markdown)
    write_molecule_bug_dashboard_sqlite(report, args.sqlite_out)
    print(
        json.dumps(
            {
                "json": str(args.json_out),
                "markdown": str(args.md_out),
                "sqlite": str(args.sqlite_out),
                "docs": str(args.docs_out),
                "molecules": report["counts"]["molecule_count"],
                "claim_ready": report["counts"]["claim_ready_count"],
                "issues": report["counts"]["issue_signature_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
