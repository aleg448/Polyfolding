"""Build substance-level CrystalProbe research profiles."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.substance_profiles import substance_profile_markdown, substance_profile_report


def _load_optional(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--therapeutic-priority", type=Path, default=Path("data/curation/therapeutic_priority_v0.1.json"))
    parser.add_argument("--ccdc-sources", type=Path, default=Path("data/curation/ccdc_therapeutic_sources_v0.1.json"))
    parser.add_argument("--lisdexamfetamine-proof", type=Path, default=Path("data/curation/lisdexamfetamine_dimesylate_proof_v0.1.json"))
    parser.add_argument("--evidence-tiers", type=Path, default=Path("outputs/crystalprobe_evidence_tiers.json"))
    parser.add_argument("--cposs-disagreement", type=Path, default=Path("outputs/cposs_high_priority_backend_disagreement.json"))
    parser.add_argument("--source-discovery", type=Path, default=Path("outputs/crystalprobe_source_discovery.json"))
    parser.add_argument("--source-acquisition", type=Path, default=Path("outputs/crystalprobe_source_acquisition.json"))
    parser.add_argument("--medication-stereochemistry", type=Path, default=Path("outputs/medication_stereochemistry.json"))
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_substance_profiles.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_substance_profiles.md"))
    args = parser.parse_args()

    report = substance_profile_report(
        therapeutic_priority=json.loads(args.therapeutic_priority.read_text(encoding="utf-8")),
        ccdc_sources=_load_optional(args.ccdc_sources),
        lisdexamfetamine_proof=_load_optional(args.lisdexamfetamine_proof),
        evidence_tiers=_load_optional(args.evidence_tiers),
        cposs_disagreement=_load_optional(args.cposs_disagreement),
        source_discovery=_load_optional(args.source_discovery),
        source_acquisition=_load_optional(args.source_acquisition),
        medication_stereochemistry=_load_optional(args.medication_stereochemistry),
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, substance_profile_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
