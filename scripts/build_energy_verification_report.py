"""Build the CrystalProbe energy-layer verification report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.energy_verification import energy_verification_markdown, energy_verification_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an energy-layer verification report.")
    parser.add_argument("--manifest", type=Path, default=Path("data/benchmark/v0.1/manifest.jsonl"))
    parser.add_argument("--predictions", type=Path, default=Path("examples/demo_predictions.jsonl"))
    parser.add_argument("--molecule-bug-hunt", type=Path, default=Path("outputs/crystalprobe_molecule_bug_hunt.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_energy_verification.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_energy_verification.md"))
    args = parser.parse_args()

    report = energy_verification_report(
        manifest_path=args.manifest,
        predictions_path=args.predictions,
        molecule_bug_hunt=_read_json_if_exists(args.molecule_bug_hunt),
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, energy_verification_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


def _read_json_if_exists(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
