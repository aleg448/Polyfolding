"""Build candidate-safe molecule viewer artifacts."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
import re
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.molecule_viewers import (
    molecule_viewer_html,
    molecule_viewer_markdown,
    molecule_viewer_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build molecule viewer registry and HTML pages.")
    parser.add_argument(
        "--candidates",
        type=Path,
        default=Path("data/curation/evidence_resolution_candidates_v0.1.json"),
    )
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_molecule_viewers.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_molecule_viewers.md"))
    parser.add_argument("--docs-md-out", type=Path, default=Path("docs/molecule_viewers.md"))
    parser.add_argument("--viewer-dir", type=Path, default=Path("docs/viewers"))
    args = parser.parse_args()

    report = molecule_viewer_report(json.loads(args.candidates.read_text(encoding="utf-8")))
    viewer_pages = _write_viewer_pages(report, args.viewer_dir)
    report["viewer_pages"] = viewer_pages
    markdown = molecule_viewer_markdown(report, viewer_pages=viewer_pages)
    docs_markdown = molecule_viewer_markdown(
        report,
        viewer_pages=_relative_viewer_pages(viewer_pages, base=args.docs_md_out.parent),
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, markdown)
    atomic_write_text(args.docs_md_out, docs_markdown)
    print(
        json.dumps(
            {
                "json": str(args.json_out),
                "markdown": str(args.md_out),
                "docs_markdown": str(args.docs_md_out),
                "viewer_pages": viewer_pages,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _write_viewer_pages(report: dict[str, object], viewer_dir: Path) -> dict[str, str]:
    viewer_pages: dict[str, str] = {}
    viewer_dir.mkdir(parents=True, exist_ok=True)
    for target in report.get("targets", []):  # type: ignore[union-attr]
        pair_id = str(target["pair_id"])
        path = viewer_dir / f"{_safe_slug(pair_id)}.html"
        atomic_write_text(path, molecule_viewer_html(report, pair_id=pair_id))
        viewer_pages[pair_id] = str(path).replace("\\", "/")
    return viewer_pages


def _relative_viewer_pages(viewer_pages: dict[str, str], *, base: Path) -> dict[str, str]:
    relative_pages = {}
    for pair_id, path in viewer_pages.items():
        try:
            relative_pages[pair_id] = Path(path).relative_to(base).as_posix()
        except ValueError:
            relative_pages[pair_id] = path
    return relative_pages


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return slug or "viewer"


if __name__ == "__main__":
    raise SystemExit(main())
