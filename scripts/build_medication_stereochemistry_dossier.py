"""Build medication stereochemistry curation dossiers."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.medication_stereochemistry_dossier import (
    medication_stereochemistry_dossier_markdown,
    medication_stereochemistry_dossier_report,
)


def _load_optional(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stereochemistry", type=Path, default=Path("outputs/medication_stereochemistry.json"))
    parser.add_argument("--seed-ranking", type=Path, default=Path("outputs/medication_seed_ranking.json"))
    parser.add_argument("--evidence", type=Path, default=Path("data/curation/medication_polymorphism_evidence_v0.1.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/medication_stereochemistry_dossier.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/medication_stereochemistry_dossier.md"))
    args = parser.parse_args()

    report = medication_stereochemistry_dossier_report(
        json.loads(args.stereochemistry.read_text(encoding="utf-8")),
        json.loads(args.seed_ranking.read_text(encoding="utf-8")),
        _load_optional(args.evidence),
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, medication_stereochemistry_dossier_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
