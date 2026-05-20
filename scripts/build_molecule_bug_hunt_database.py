"""Build the molecule bug-hunt stress database."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.molecule_bug_hunt import (
    molecule_bug_hunt_markdown,
    molecule_bug_hunt_report,
    write_molecule_bug_hunt_sqlite,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a molecule stress database for software bug hunting.")
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path("data/curation/molecule_bug_hunt_stress_v0.1.json"),
    )
    parser.add_argument("--sqlite-out", type=Path, default=Path("outputs/crystalprobe_molecule_bug_hunt.sqlite"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_molecule_bug_hunt.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_molecule_bug_hunt.md"))
    parser.add_argument("--docs-md-out", type=Path, default=Path("docs/molecule_bug_hunt.md"))
    args = parser.parse_args()

    report = molecule_bug_hunt_report(json.loads(args.catalog.read_text(encoding="utf-8")))
    write_molecule_bug_hunt_sqlite(report, args.sqlite_out)
    markdown = molecule_bug_hunt_markdown(report)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, markdown)
    atomic_write_text(args.docs_md_out, markdown)
    print(
        json.dumps(
            {
                "sqlite": str(args.sqlite_out),
                "json": str(args.json_out),
                "markdown": str(args.md_out),
                "docs_markdown": str(args.docs_md_out),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
