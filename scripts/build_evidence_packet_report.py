"""Build a single-pair evidence packet for research-cycle review."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.benchmark.dataset import load_manifest
from crystalprobe.benchmark.predictions import load_pair_energy_prediction_records
from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.evidence_packet import evidence_packet_markdown, evidence_packet_report, select_pair_for_packet


DEFAULT_PAIR_ID = "paracetamol_form_i_vs_form_ii_seed"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("data/benchmark/v0.1/manifest.jsonl"))
    parser.add_argument("--predictions", type=Path, default=Path("examples/demo_predictions.jsonl"))
    parser.add_argument("--pair-id", default=DEFAULT_PAIR_ID)
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_evidence_packet.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_evidence_packet.md"))
    args = parser.parse_args()

    dataset = load_manifest(args.manifest)
    pair = select_pair_for_packet(dataset.pairs, args.pair_id)
    predictions = {
        record.pair_id: record
        for record in load_pair_energy_prediction_records(args.predictions)
    } if args.predictions.exists() else {}
    report = evidence_packet_report(pair, prediction=predictions.get(pair.pair_id))
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, evidence_packet_markdown(report))
    print(
        json.dumps(
            {"json": str(args.json_out), "markdown": str(args.md_out), "pair_id": pair.pair_id},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
