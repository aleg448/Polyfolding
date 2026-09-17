"""Plan or resume a bounded molecule research campaign."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
import sys
from pathlib import Path

from crystalprobe.core.io import atomic_write_json
from crystalprobe.insight.tentative_molecule_benchmark import load_molecule_panel
from crystalprobe.research.campaign import run_campaign
from crystalprobe.research.molecules import molecule_campaign


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-id", default="molecule_qa")
    parser.add_argument("--backends", nargs="*", choices=["mace", "aimnet2", "uma"], default=[])
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--fairchem-python")
    parser.add_argument("--mace-checkpoint")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-jobs", type=int, default=100)
    parser.add_argument("--max-seconds", type=float, default=300)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--orchestrator", choices=["local", "prefect"], default="local")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    records = load_molecule_panel(
        root / "data/curation/molecule_bug_hunt_stress_v0.1.json",
        root / "data/curation/molecule_benchmark_panel_v0.1.csv",
    )
    if args.limit is not None:
        if args.limit < 1:
            parser.error("--limit must be positive")
        records = records[:args.limit]
    campaign = molecule_campaign(
        records, campaign_id=args.campaign_id, backends=tuple(args.backends), python=args.python,
        backend_pythons={"uma": args.fairchem_python} if args.fairchem_python else {},
        mace_checkpoint=args.mace_checkpoint, device=args.device,
    )
    directory = root / "outputs/campaigns" / campaign.campaign_id
    if args.plan_only:
        atomic_write_json(directory / "plan.json", campaign.model_dump())
        print(json.dumps({"plan": str(directory / "plan.json"), "tasks": len(campaign.tasks)}))
        return 0
    runner = run_campaign
    if args.orchestrator == "prefect":
        from crystalprobe.research.prefect_flow import run_prefect_campaign
        runner = run_prefect_campaign
    report = runner(campaign, root=root, output_dir=directory,
                    max_jobs=args.max_jobs, max_seconds=args.max_seconds)
    print(json.dumps({"status": report["status"], "counts": report["counts"],
                      "jobs_executed": report["jobs_executed"], "latest": str(directory / "latest.json")}))
    return 2 if report["status"] == "completed_with_issues" else 0


if __name__ == "__main__":
    raise SystemExit(main())
