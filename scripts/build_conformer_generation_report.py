"""Build the CrystalProbe conformer-generation report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.conformer_generation import (
    conformer_generation_markdown,
    conformer_generation_report,
    write_conformer_generation_sqlite,
)
from crystalprobe.insight.tentative_molecule_benchmark import load_molecule_panel


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an optional RDKit conformer-generation report.")
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
    parser.add_argument("--max-molecules", type=int, default=None)
    parser.add_argument("--random-seed", type=int, default=61453)
    parser.add_argument("--no-optimize", action="store_true")
    parser.add_argument("--write-xyz-dir", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_conformer_generation.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_conformer_generation.md"))
    parser.add_argument("--sqlite-out", type=Path, default=Path("outputs/crystalprobe_conformer_generation.sqlite"))
    parser.add_argument("--docs-out", type=Path, default=Path("docs/conformer_generation.md"))
    args = parser.parse_args()

    records = load_molecule_panel(args.stress_catalog, args.panel)
    report = conformer_generation_report(
        records,
        random_seed=args.random_seed,
        max_molecules=args.max_molecules,
        optimize=not args.no_optimize,
        write_xyz_dir=args.write_xyz_dir,
    )
    markdown = conformer_generation_markdown(report)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, markdown)
    atomic_write_text(args.docs_out, markdown)
    write_conformer_generation_sqlite(report, args.sqlite_out)
    print(
        json.dumps(
            {
                "json": str(args.json_out),
                "markdown": str(args.md_out),
                "sqlite": str(args.sqlite_out),
                "docs": str(args.docs_out),
                "generated": report["counts"]["generated_count"],
                "blocked": report["counts"]["blocked_count"],
                "coordinate_payload_enabled": report["coordinate_payload_enabled"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
