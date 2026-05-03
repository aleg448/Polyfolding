"""Command-line interface for benchmark curation checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.benchmark.curation import readiness_report
from crystalprobe.benchmark.dataset import load_manifest
from crystalprobe.benchmark.metrics import ranking_accuracy
from crystalprobe.benchmark.predictions import load_pair_energy_prediction_records, load_pair_energy_predictions
from crystalprobe.config import load_config
from crystalprobe.datahub.cposs209 import index_cposs_directory, summarize_cposs_records
from crystalprobe.datahub.sources import source_registry
from crystalprobe.foundry.adapters import all_adapter_availability
from crystalprobe.insight.fingerprint import build_fingerprint_report
from crystalprobe.insight.calibration import build_calibration_report
from crystalprobe.insight.reporting import fingerprint_markdown
from crystalprobe.openbench.quick import run_quick_benchmark


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="crystalprobe", description="CrystalProbe benchmark utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a JSON Lines benchmark manifest")
    validate.add_argument("manifest", type=Path)
    validate.add_argument("--require-files", action="store_true", help="Fail if referenced CIF files are missing")

    summarize = subparsers.add_parser("summarize", help="Print a manifest summary as JSON")
    summarize.add_argument("manifest", type=Path)

    score = subparsers.add_parser("score-ranking", help="Score pairwise energy predictions against a manifest")
    score.add_argument("manifest", type=Path)
    score.add_argument("predictions", type=Path)
    score.add_argument("--verified-only", action="store_true", help="Evaluate only verified benchmark records")

    curation = subparsers.add_parser("curation-report", help="Report blockers before promoting draft records")
    curation.add_argument("manifest", type=Path)

    fingerprint = subparsers.add_parser("fingerprint", help="Generate a behavioural fingerprint report")
    fingerprint.add_argument("manifest", type=Path)
    fingerprint.add_argument("predictions", type=Path)
    fingerprint.add_argument("--markdown", type=Path, help="Optional markdown output path")

    calibration = subparsers.add_parser("calibration", help="Generate pairwise ranking calibration diagnostics")
    calibration.add_argument("manifest", type=Path)
    calibration.add_argument("predictions", type=Path)
    calibration.add_argument("--bins", type=int, default=10)

    quick = subparsers.add_parser("quick-benchmark", help="Run quick benchmark analysis into an output directory")
    quick.add_argument("manifest", type=Path)
    quick.add_argument("predictions", type=Path)
    quick.add_argument("output_dir", type=Path)
    quick.add_argument("--ledger", type=Path)
    quick.add_argument("--verified-only", action="store_true")

    run_config = subparsers.add_parser("run-config", help="Run a workflow from a CrystalProbe JSON config")
    run_config.add_argument("config", type=Path)

    subparsers.add_parser("doctor", help="Check optional scientific backend availability")
    subparsers.add_parser("sources", help="List curated external data/model sources")

    cposs = subparsers.add_parser("cposs-index", help="Index extracted CPOSS209 CIF source files")
    cposs.add_argument("source_dir", type=Path, nargs="?", default=Path("data/sources/cposs209/cg5c00255_si_004"))
    cposs.add_argument("--json-out", type=Path, help="Optional path for the full indexed record JSON")
    cposs.add_argument("--no-atoms", action="store_true", help="Skip ASE atom/formula metadata")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        dataset = load_manifest(args.manifest)
        if args.require_files:
            missing = dataset.validate_structure_files()
            if missing:
                for path in missing:
                    print(f"missing CIF: {path}")
                return 2
        print(f"OK: {len(dataset)} polymorph-pair records")
        return 0

    if args.command == "summarize":
        dataset = load_manifest(args.manifest)
        print(json.dumps(dataset.summary(), indent=2, sort_keys=True))
        return 0

    if args.command == "score-ranking":
        dataset = load_manifest(args.manifest)
        if args.verified_only:
            dataset = dataset.verified()
        predictions = load_pair_energy_predictions(args.predictions)
        result = ranking_accuracy(list(dataset), predictions)
        print(
            json.dumps(
                {
                    "accuracy": result.accuracy,
                    "correct": result.correct,
                    "evaluated": result.evaluated,
                    "skipped": result.skipped,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "curation-report":
        dataset = load_manifest(args.manifest)
        print(json.dumps(readiness_report(dataset), indent=2, sort_keys=True))
        return 0

    if args.command == "fingerprint":
        dataset = load_manifest(args.manifest)
        predictions = load_pair_energy_predictions(args.predictions)
        report = build_fingerprint_report(list(dataset), predictions)
        if args.markdown:
            args.markdown.parent.mkdir(parents=True, exist_ok=True)
            args.markdown.write_text(fingerprint_markdown(report), encoding="utf-8", newline="\n")
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
        return 0

    if args.command == "calibration":
        dataset = load_manifest(args.manifest)
        records = load_pair_energy_prediction_records(args.predictions)
        report = build_calibration_report(list(dataset), records, bins=args.bins)
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
        return 0

    if args.command == "quick-benchmark":
        result = run_quick_benchmark(
            manifest=args.manifest,
            predictions=args.predictions,
            output_dir=args.output_dir,
            ledger=args.ledger,
            verified_only=args.verified_only,
        )
        print(json.dumps({"report_json": str(result.report_json), "report_markdown": str(result.report_markdown), "calibration_json": str(result.calibration_json), "ledger": str(result.ledger_path) if result.ledger_path else None}, indent=2, sort_keys=True))
        return 0

    if args.command == "run-config":
        config = load_config(args.config)
        if config.workflow == "quick_benchmark":
            quick_config = config.quick_benchmark
            result = run_quick_benchmark(
                manifest=quick_config.manifest,
                predictions=quick_config.predictions,
                output_dir=quick_config.output_dir,
                ledger=quick_config.ledger,
                verified_only=quick_config.verified_only,
            )
            print(json.dumps({"report_json": str(result.report_json), "report_markdown": str(result.report_markdown), "calibration_json": str(result.calibration_json), "ledger": str(result.ledger_path) if result.ledger_path else None}, indent=2, sort_keys=True))
            return 0

    if args.command == "doctor":
        rows = [availability.__dict__ | {"blocker": availability.blocker} for availability in all_adapter_availability()]
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0

    if args.command == "sources":
        print(json.dumps([source.__dict__ for source in source_registry()], indent=2, sort_keys=True))
        return 0

    if args.command == "cposs-index":
        records = index_cposs_directory(args.source_dir, with_atoms=not args.no_atoms)
        payload = {
            "summary": summarize_cposs_records(records),
            "records": [record.as_dict() for record in records],
        }
        if args.json_out:
            args.json_out.parent.mkdir(parents=True, exist_ok=True)
            args.json_out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
