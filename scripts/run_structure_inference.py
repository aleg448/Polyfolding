"""Run MLIP inference for one ASE-readable molecular or crystal structure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ase.io import read

from crystalprobe.datahub.ccdc import write_ccdc_block
from crystalprobe.foundry.optional_adapters import AIMNet2Adapter, MACEOffAdapter
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
    raise ValueError(f"unsupported backend: {args.backend}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("structure", type=Path)
    parser.add_argument("--structure-id", required=True)
    parser.add_argument("--cif-block", help="Extract this data block from a multi-block CIF before reading")
    parser.add_argument("--cif-block-index", type=int, help="Extract this zero-based data block index before reading")
    parser.add_argument("--backend", choices=["mace", "aimnet2"], default="mace")
    parser.add_argument("--device", default=None)
    parser.add_argument("--mace-model", default="small")
    parser.add_argument("--aimnet-model", default="aimnet2")
    parser.add_argument("--aimnet-dispersion", action="store_true")
    parser.add_argument("--index", default="0")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--no-local-geometry", action="store_true")
    args = parser.parse_args()

    structure_path = args.structure
    if args.cif_block is not None or args.cif_block_index is not None:
        extracted = Path("outputs") / "_structure_inference_blocks" / f"{args.structure_id}.cif"
        write_ccdc_block(args.structure, extracted, block_id=args.cif_block, index=args.cif_block_index)
        structure_path = extracted

    index: int | str = int(args.index) if args.index.isdigit() else args.index
    atoms = read(str(structure_path), index=index)
    model = _adapter(args)
    prediction = model.predict(atoms)
    row = {
        "structure_id": args.structure_id,
        "structure_path": str(args.structure),
        "read_structure_path": str(structure_path),
        "backend": args.backend,
        "formula": atoms.get_chemical_formula(),
        "natoms": len(atoms),
        "pbc": list(bool(value) for value in atoms.pbc),
        "energy_ev": prediction.energy,
        "force_summary": {
            "max_force_ev_per_ang": max(
                (sum(float(component) ** 2 for component in force) ** 0.5 for force in prediction.forces),
                default=0.0,
            ),
            "mean_force_ev_per_ang": (
                sum(sum(float(component) ** 2 for component in force) ** 0.5 for force in prediction.forces)
                / len(prediction.forces)
                if prediction.forces
                else 0.0
            ),
        },
        "model_metadata": prediction.metadata,
    }
    if not args.no_local_geometry:
        row["local_geometry"] = analyze_local_geometry(atoms, forces=prediction.forces)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(row, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(args.output), "structure_id": args.structure_id, "backend": args.backend}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
