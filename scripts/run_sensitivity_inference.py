"""Run MLIP inference over a generated perturbation sensitivity manifest."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from ase.io import read

from crystalprobe.core.paths import portable_path
from crystalprobe.foundry.optional_adapters import AIMNet2Adapter, MACEOffAdapter, UMAAdapter
from crystalprobe.insight.local_geometry import analyze_local_geometry


def _adapter(args: argparse.Namespace) -> Any:
    if args.backend == "mace":
        return MACEOffAdapter(model=args.mace_model, device=args.device)
    if args.backend == "aimnet2":
        return AIMNet2Adapter(
            model=args.aimnet_model,
            device=args.device,
            needs_dispersion=args.aimnet_dispersion,
        )
    if args.backend == "uma":
        return UMAAdapter(
            checkpoint=args.uma_checkpoint,
            task_name=args.uma_task_name,
            device=args.device,
        )
    raise ValueError(f"unsupported backend: {args.backend}")


def _force_summary(forces: tuple[tuple[float, ...], ...]) -> dict[str, float]:
    norms = [math.sqrt(sum(component * component for component in row)) for row in forces]
    if not norms:
        return {"max_force_ev_per_ang": 0.0, "mean_force_ev_per_ang": 0.0}
    return {
        "max_force_ev_per_ang": max(norms),
        "mean_force_ev_per_ang": sum(norms) / len(norms),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--backend", choices=["mace", "aimnet2", "uma"], default="mace")
    parser.add_argument("--device", default=None)
    parser.add_argument("--mace-model", default="small")
    parser.add_argument("--aimnet-model", default="aimnet2")
    parser.add_argument("--aimnet-dispersion", action="store_true")
    parser.add_argument("--uma-checkpoint", default="uma-s-1p2")
    parser.add_argument("--uma-task-name", default="omc")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--no-local-geometry", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    model = _adapter(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    completed = 0
    errors = 0
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for variant in manifest["variants"]:
            try:
                variant_path = portable_path(variant["path"])
                atoms = read(str(variant_path))
                prediction = model.predict(atoms)
                row = {
                    "backend": args.backend,
                    "manifest": str(args.manifest),
                    "variant": variant["name"],
                    "variant_path": str(variant_path),
                    "formula": atoms.get_chemical_formula(),
                    "natoms": len(atoms),
                    "pbc": [bool(value) for value in atoms.pbc],
                    "energy_ev": prediction.energy,
                    "force_summary": _force_summary(prediction.forces),
                    "model_metadata": prediction.metadata,
                    "perturbation": variant,
                }
                if not args.no_local_geometry:
                    row["local_geometry"] = analyze_local_geometry(atoms, forces=prediction.forces)
            except Exception as exc:
                if not args.continue_on_error:
                    raise
                row = {
                    "backend": args.backend,
                    "manifest": str(args.manifest),
                    "variant": variant["name"],
                    "variant_path": variant.get("path"),
                    "error": f"{type(exc).__name__}: {exc}",
                }
                errors += 1
            else:
                completed += 1
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")))
            handle.write("\n")

    print(
        json.dumps(
            {
                "backend": args.backend,
                "attempted": len(manifest["variants"]),
                "completed": completed,
                "errors": errors,
                "output": str(args.output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if errors == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
