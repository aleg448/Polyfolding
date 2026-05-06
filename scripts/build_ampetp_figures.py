"""Build deterministic SVG figures for the AMPETP pilot paper."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from ase.io import read

from crystalprobe.insight.figures import (
    backend_measurement_svg,
    guardrail_svg,
    provenance_flow_svg,
    sensitivity_delta_svg,
    structure_projection_svg,
    write_svg,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-study", type=Path, default=Path("outputs/ampetp_case_study_report.json"))
    parser.add_argument("--sensitivity", type=Path, default=Path("outputs/ampetp_sensitivity_summary.json"))
    parser.add_argument("--structure-cif", type=Path, default=Path("outputs/ccdc_ampetp_extracted.cif"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/figures"))
    args = parser.parse_args()

    case_study = json.loads(args.case_study.read_text(encoding="utf-8"))
    sensitivity = json.loads(args.sensitivity.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "provenance": args.output_dir / "ampetp_provenance_flow.svg",
        "structure": args.output_dir / "ampetp_structure_projection.svg",
        "backend": args.output_dir / "ampetp_backend_force_diagnostics.svg",
        "sensitivity": args.output_dir / "ampetp_sensitivity_energy_deltas.svg",
        "guardrails": args.output_dir / "ampetp_claim_guardrails.svg",
    }
    write_svg(
        outputs["provenance"],
        provenance_flow_svg(
            "AMPETP CrystalProbe provenance",
            [
                "Local CCDC multi-CIF export",
                "AMPETP block extraction",
                "ASE periodic crystal",
                "MACE and AIMNet2 inference",
                "Diagnostics and paper figures",
            ],
        ),
    )
    write_svg(outputs["structure"], structure_projection_svg(read(str(args.structure_cif))))
    write_svg(outputs["backend"], backend_measurement_svg(case_study))
    write_svg(outputs["sensitivity"], sensitivity_delta_svg(sensitivity))
    write_svg(
        outputs["guardrails"],
        guardrail_svg(
            "AMPETP claim boundaries",
            supported=[
                "Real CCDC crystal ingestion",
                "Two-backend periodic inference",
                "Bond and force diagnostics",
                "Perturbation sensitivity probes",
            ],
            blocked=[
                "Not lisdexamfetamine dimesylate",
                "Not a polymorph ranking",
                "No experimental stability claim",
                "No calibrated uncertainty yet",
            ],
        ),
    )
    print(json.dumps({key: str(path) for key, path in outputs.items()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
