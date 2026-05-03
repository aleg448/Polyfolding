"""Run single-structure MLIP inference over CPOSS209 CIF blocks."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from crystalprobe.datahub.cposs209 import CpossStructureRecord, index_cposs_cif
from crystalprobe.foundry.optional_adapters import AIMNet2Adapter, MACEOffAdapter
from crystalprobe.structures.cif import read_cif_structure


def _adapter(args: argparse.Namespace) -> Any:
    if args.backend == "mace":
        return MACEOffAdapter(model=args.mace_model, device=args.device)
    if args.backend == "aimnet2":
        return AIMNet2Adapter(
            model=args.aimnet_model,
            device=args.device,
            needs_dispersion=args.aimnet_dispersion,
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


def _prediction_row(
    record: CpossStructureRecord,
    *,
    source_path: Path,
    adapter: Any,
) -> dict[str, Any]:
    atoms = read_cif_structure(source_path, index=record.source_index)
    prediction = adapter.predict(atoms)
    return {
        "block_id": record.block_id,
        "family_code": record.family_code,
        "form_number": record.form_number,
        "source_file": record.source_file,
        "source_index": record.source_index,
        "formula": atoms.get_chemical_formula(),
        "natoms": len(atoms),
        "energy_ev": prediction.energy,
        "force_summary": _force_summary(prediction.forces),
        "model_metadata": prediction.metadata,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=Path("data/sources/cposs209/cg5c00255_si_004"))
    parser.add_argument("--source-file", default="All_Psi_Crys.cif")
    parser.add_argument("--output", type=Path, default=Path("outputs/cposs209_structure_predictions.jsonl"))
    parser.add_argument("--backend", choices=["mace", "aimnet2"], default="mace")
    parser.add_argument("--device", default=None)
    parser.add_argument("--mace-model", default="small")
    parser.add_argument("--aimnet-model", default="aimnet2")
    parser.add_argument("--aimnet-dispersion", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    source_path = args.source_dir / args.source_file
    records = index_cposs_cif(source_path, with_atoms=False)
    if args.limit is not None:
        records = records[: args.limit]

    model = _adapter(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    completed = 0
    errors = 0
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            try:
                row = _prediction_row(record, source_path=source_path, adapter=model)
            except Exception as exc:
                if not args.continue_on_error:
                    raise
                row = {
                    "block_id": record.block_id,
                    "family_code": record.family_code,
                    "source_file": record.source_file,
                    "source_index": record.source_index,
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
                "source_file": args.source_file,
                "attempted": len(records),
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
