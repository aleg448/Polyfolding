"""Build the CrystalProbe AGI-assisted evidence-tier report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.evidence_tiers import evidence_tier_markdown, evidence_tier_report


DEFAULT_RECORDS = [
    {
        "target": "lisdexamfetamine dimesylate crystal",
        "has_atom_coordinates": False,
        "backend_count": 0,
        "has_sensitivity_grid": False,
        "has_therapeutic_contrast": False,
        "has_source_provenance": True,
        "license_clean_for_redistribution": False,
        "human_database_validation": False,
        "experimental_stability_evidence": False,
    },
    {
        "target": "AMPETP CCDC 1102740",
        "has_atom_coordinates": True,
        "backend_count": 3,
        "has_sensitivity_grid": True,
        "has_therapeutic_contrast": True,
        "has_source_provenance": True,
        "license_clean_for_redistribution": False,
        "human_database_validation": False,
        "experimental_stability_evidence": False,
    },
    {
        "target": "ibuprofen CCDC 774097",
        "has_atom_coordinates": True,
        "backend_count": 3,
        "has_sensitivity_grid": True,
        "has_therapeutic_contrast": True,
        "has_source_provenance": True,
        "license_clean_for_redistribution": False,
        "human_database_validation": False,
        "experimental_stability_evidence": False,
    },
    {
        "target": "CPOSS IBP/CBZ bridge",
        "has_atom_coordinates": True,
        "backend_count": 1,
        "has_sensitivity_grid": False,
        "has_therapeutic_contrast": False,
        "has_source_provenance": True,
        "license_clean_for_redistribution": True,
        "human_database_validation": False,
        "experimental_stability_evidence": False,
    },
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_evidence_tiers.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_evidence_tiers.md"))
    args = parser.parse_args()

    records = DEFAULT_RECORDS if args.records is None else json.loads(args.records.read_text(encoding="utf-8"))
    report = evidence_tier_report(records)
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, evidence_tier_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
