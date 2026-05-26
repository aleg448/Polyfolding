"""Build a small backend smoke benchmark over generated conformer inputs."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.backend_smoke import (
    backend_smoke_markdown,
    backend_smoke_report,
    write_backend_smoke_sqlite,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a tiny backend smoke benchmark over generated conformers.")
    parser.add_argument(
        "--input-manifest",
        type=Path,
        default=Path("outputs/crystalprobe_backend_ready_inputs.json"),
        help="Backend-ready input manifest built from generated conformers.",
    )
    parser.add_argument("--backend", dest="backend", action="append", choices=["mace", "aimnet2", "uma"])
    parser.add_argument("--backends", nargs="+", choices=["mace", "aimnet2", "uma"])
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--dry-run", action="store_true", help="Record selected input/backend rows without execution.")
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_backend_smoke.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_backend_smoke.md"))
    parser.add_argument("--sqlite-out", type=Path, default=Path("outputs/crystalprobe_backend_smoke.sqlite"))
    parser.add_argument("--docs-out", type=Path, default=Path("docs/backend_smoke.md"))
    args = parser.parse_args()

    selected = args.backends or args.backend or ["mace", "aimnet2"]

    manifest = json.loads(args.input_manifest.read_text(encoding="utf-8"))
    report = backend_smoke_report(
        manifest,
        backends=selected,
        limit=args.limit,
        execute=not args.dry_run,
        device=args.device,
    )
    markdown = backend_smoke_markdown(report)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, markdown)
    atomic_write_text(args.docs_out, markdown)
    write_backend_smoke_sqlite(report, args.sqlite_out)
    print(
        json.dumps(
            {
                "json": str(args.json_out),
                "markdown": str(args.md_out),
                "sqlite": str(args.sqlite_out),
                "docs": str(args.docs_out),
                "passed": report["counts"]["passed_count"],
                "blocked": report["counts"]["blocked_count"],
                "failed": report["counts"]["failed_count"],
                "claim_ready": report["counts"]["claim_ready_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
