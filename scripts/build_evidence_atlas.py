"""Build the CrystalProbe Evidence Atlas database and static explorer."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.evidence_atlas import (
    build_evidence_atlas,
    evidence_atlas_explorer_html,
    evidence_atlas_markdown,
    write_evidence_atlas_sqlite,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a queryable CrystalProbe evidence atlas.")
    parser.add_argument("--manifest", type=Path, default=Path("data/benchmark/v0.1/manifest.jsonl"))
    parser.add_argument("--predictions", type=Path, default=Path("examples/demo_predictions.jsonl"))
    parser.add_argument("--evidence-packet", type=Path, default=Path("outputs/crystalprobe_evidence_packet.json"))
    parser.add_argument(
        "--evidence-resolution",
        type=Path,
        default=Path("outputs/crystalprobe_evidence_resolution.json"),
    )
    parser.add_argument("--molecule-viewers", type=Path, default=Path("outputs/crystalprobe_molecule_viewers.json"))
    parser.add_argument("--release-boundary", type=Path, default=Path("outputs/crystalprobe_release_boundary.json"))
    parser.add_argument("--sqlite-out", type=Path, default=Path("outputs/crystalprobe_evidence_atlas.sqlite"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_evidence_atlas.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_evidence_atlas.md"))
    parser.add_argument("--docs-md-out", type=Path, default=Path("docs/evidence_atlas.md"))
    parser.add_argument("--explorer-out", type=Path, default=Path("docs/evidence_atlas.html"))
    args = parser.parse_args()

    report = build_evidence_atlas(
        manifest_path=args.manifest,
        predictions_path=args.predictions,
        evidence_packet=_read_json_if_exists(args.evidence_packet),
        evidence_resolution=_read_json_if_exists(args.evidence_resolution),
        molecule_viewers=_read_json_if_exists(args.molecule_viewers),
        release_boundary=_read_json_if_exists(args.release_boundary),
    )
    write_evidence_atlas_sqlite(report, args.sqlite_out)
    markdown = evidence_atlas_markdown(
        report,
        sqlite_path=str(args.sqlite_out).replace("\\", "/"),
        explorer_path=str(args.explorer_out).replace("\\", "/"),
    )
    docs_markdown = evidence_atlas_markdown(
        report,
        sqlite_path=str(args.sqlite_out).replace("\\", "/"),
        explorer_path=args.explorer_out.name,
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, markdown)
    atomic_write_text(args.docs_md_out, docs_markdown)
    atomic_write_text(args.explorer_out, evidence_atlas_explorer_html(report))
    print(
        json.dumps(
            {
                "sqlite": str(args.sqlite_out),
                "json": str(args.json_out),
                "markdown": str(args.md_out),
                "docs_markdown": str(args.docs_md_out),
                "explorer": str(args.explorer_out),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _read_json_if_exists(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
