"""Check the public CrystalProbe artifact for drift and safety."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.public_artifact_integrity import (
    public_artifact_integrity_markdown,
    public_artifact_integrity_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public CrystalProbe artifact integrity.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/public_artifact_integrity.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/public_artifact_integrity.md"))
    args = parser.parse_args()

    report = public_artifact_integrity_report(root=args.root)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, public_artifact_integrity_markdown(report))
    print(json.dumps({"status": report["status"], "json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0 if report["status"] == "public_artifact_integrity_passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
