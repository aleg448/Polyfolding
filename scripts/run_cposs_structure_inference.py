"""Run single-structure MLIP inference over CPOSS209 CIF blocks."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
import math
from pathlib import Path
from typing import Any

from crystalprobe.core.io import atomic_write_text
from crystalprobe.datahub.cposs209 import CpossStructureRecord, index_cposs_cif
from crystalprobe.foundry.optional_adapters import AIMNet2Adapter, MACEOffAdapter, UMAAdapter
from crystalprobe.insight.local_geometry import analyze_local_geometry
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


def _prediction_row(
    record: CpossStructureRecord,
    *,
    source_path: Path,
    adapter: Any,
    include_local_geometry: bool,
) -> dict[str, Any]:
    atoms = read_cif_structure(source_path, index=record.source_index)
    prediction = adapter.predict(atoms)
    row = {
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
    if include_local_geometry:
        row["local_geometry"] = analyze_local_geometry(atoms, forces=prediction.forces)
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=Path("data/sources/cposs209/cg5c00255_si_004"))
    parser.add_argument("--source-file", default="All_Psi_Crys.cif")
    parser.add_argument("--output", type=Path, default=Path("outputs/cposs209_structure_predictions.jsonl"))
    parser.add_argument("--backend", choices=["mace", "aimnet2", "uma"], default="mace")
    parser.add_argument("--device", default=None)
    parser.add_argument("--mace-model", default="small")
    parser.add_argument("--aimnet-model", default="aimnet2")
    parser.add_argument("--aimnet-dispersion", action="store_true")
    parser.add_argument("--uma-checkpoint", default="uma-s-1p2")
    parser.add_argument("--uma-task-name", default="omc")
    parser.add_argument(
        "--family",
        action="append",
        default=[],
        help="Restrict to one CPOSS family code; repeat for multiple families, e.g. --family IBP --family CBZ.",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--block-id", action="append", default=[], help="Restrict to one CPOSS block id; repeat for multiple blocks.")
    parser.add_argument("--no-local-geometry", action="store_true", help="Skip local bond/contact/force diagnostics")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    source_path = args.source_dir / args.source_file
    records = index_cposs_cif(source_path, with_atoms=False)
    records = _filter_records(records, families=args.family, block_ids=args.block_id, limit=args.limit)

    model = _adapter(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    completed = 0
    errors = 0
    rows = []
    for record in records:
        try:
            row = _prediction_row(
                record,
                source_path=source_path,
                adapter=model,
                include_local_geometry=not args.no_local_geometry,
            )
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
        rows.append(json.dumps(row, sort_keys=True, separators=(",", ":")))
    atomic_write_text(args.output, "\n".join(rows) + ("\n" if rows else ""))

    print(
        json.dumps(
            {
                "backend": args.backend,
                "source_file": args.source_file,
                "attempted": len(records),
                "completed": completed,
                "errors": errors,
                "families": sorted({record.family_code for record in records}),
                "output": str(args.output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if errors == 0 else 2


def _filter_records(
    records: list[CpossStructureRecord],
    *,
    families: list[str],
    block_ids: list[str],
    limit: int | None,
) -> list[CpossStructureRecord]:
    selected = records
    if families:
        family_set = {family.upper() for family in families}
        selected = [record for record in selected if record.family_code.upper() in family_set]
    if block_ids:
        block_set = {block_id.upper() for block_id in block_ids}
        selected = [record for record in selected if record.block_id.upper() in block_set]
    if limit is not None:
        selected = selected[:limit]
    return selected


if __name__ == "__main__":
    raise SystemExit(main())
