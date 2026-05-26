"""Build the CrystalProbe tentative molecule benchmark report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.tentative_molecule_benchmark import (
    build_tentative_molecule_benchmark,
    load_molecule_panel,
    tentative_molecule_benchmark_markdown,
    write_tentative_molecule_benchmark_sqlite,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a tentative molecule-panel benchmark.")
    parser.add_argument(
        "--stress-catalog",
        type=Path,
        default=Path("data/curation/molecule_bug_hunt_stress_v0.1.json"),
    )
    parser.add_argument(
        "--panel",
        type=Path,
        default=Path("data/curation/molecule_benchmark_panel_v0.1.csv"),
    )
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_tentative_molecule_benchmark.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_tentative_molecule_benchmark.md"))
    parser.add_argument(
        "--sqlite-out",
        type=Path,
        default=Path("outputs/crystalprobe_tentative_molecule_benchmark.sqlite"),
    )
    parser.add_argument("--docs-out", type=Path, default=Path("docs/tentative_molecule_benchmark.md"))
    args = parser.parse_args()

    records = load_molecule_panel(args.stress_catalog, args.panel)
    report = build_tentative_molecule_benchmark(records)
    markdown = tentative_molecule_benchmark_markdown(report)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, markdown)
    atomic_write_text(args.docs_out, markdown)
    write_tentative_molecule_benchmark_sqlite(report, args.sqlite_out)
    print(
        json.dumps(
            {
                "json": str(args.json_out),
                "markdown": str(args.md_out),
                "sqlite": str(args.sqlite_out),
                "docs": str(args.docs_out),
                "molecules": report["counts"]["molecule_count"],
                "claim_ready": report["counts"]["claim_ready_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
