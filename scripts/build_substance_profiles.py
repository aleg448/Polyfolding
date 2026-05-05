"""Build substance-level CrystalProbe research profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

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
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_substance_profiles.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_substance_profiles.md"))
    args = parser.parse_args()

    report = substance_profile_report(
        therapeutic_priority=json.loads(args.therapeutic_priority.read_text(encoding="utf-8")),
        ccdc_sources=_load_optional(args.ccdc_sources),
        lisdexamfetamine_proof=_load_optional(args.lisdexamfetamine_proof),
        evidence_tiers=_load_optional(args.evidence_tiers),
        cposs_disagreement=_load_optional(args.cposs_disagreement),
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(substance_profile_markdown(report), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
