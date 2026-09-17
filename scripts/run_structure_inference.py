"""Run MLIP inference for one ASE-readable molecular or crystal structure."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from crystalprobe.core.io import atomic_write_json
from crystalprobe.core.paths import safe_filename
from crystalprobe.datahub.cif_repair import repair_cif_spacegroup_text
from crystalprobe.datahub.ccdc import cif_spacegroup_replacements, write_ccdc_block
from crystalprobe.foundry.optional_adapters import AIMNet2Adapter, MACEOffAdapter, UMAAdapter
from crystalprobe.insight.local_geometry import analyze_local_geometry


def _read_atoms(structure_path: Path, index: int | str, *, repair_cif_spacegroup: bool = False):
    from ase.io import read

    if not repair_cif_spacegroup:
        return read(str(structure_path), index=index)
    if structure_path.suffix.lower() != ".cif":
        return read(str(structure_path), index=index)
    repaired = repair_cif_spacegroup_text(structure_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / structure_path.name
        path.write_text(repaired, encoding="utf-8", newline="\n")
        return read(str(path), index=index)


def _adapter(args: argparse.Namespace) -> Any:
    if args.backend == "mace":
        return MACEOffAdapter(model=args.mace_model, device=args.device)
    if args.backend == "aimnet2":
        return AIMNet2Adapter(
            model=args.aimnet_model,
            device=args.device,
            needs_dispersion=args.aimnet_dispersion,
            charge=args.aimnet_charge,
            allow_periodic_cluster=args.allow_periodic_cluster,
        )
    if args.backend == "uma":
        return UMAAdapter(
            checkpoint=args.uma_checkpoint,
            task_name=args.uma_task_name,
            device=args.device,
        )
    raise ValueError(f"unsupported backend: {args.backend}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("structure", type=Path)
    parser.add_argument("--structure-id", required=True)
    parser.add_argument("--cif-block", help="Extract this data block from a multi-block CIF before reading")
    parser.add_argument("--cif-block-index", type=int, help="Extract this zero-based data block index before reading")
    parser.add_argument("--backend", choices=["mace", "aimnet2", "uma"], default="mace")
    parser.add_argument("--device", default=None)
    parser.add_argument("--mace-model", default="small")
    parser.add_argument("--aimnet-model", default="aimnet2")
    parser.add_argument("--aimnet-dispersion", action="store_true")
    parser.add_argument(
        "--aimnet-charge",
        type=float,
        default=0.0,
        help="Net total charge for AIMNet2 (used when the structure carries no charge annotation, e.g. a bare salt ion).",
    )
    parser.add_argument(
        "--allow-periodic-cluster",
        action="store_true",
        help="Let AIMNet2 evaluate a periodic input as an isolated cluster (documented approximation; off by default).",
    )
    parser.add_argument("--uma-checkpoint", default="uma-s-1p2")
    parser.add_argument("--uma-task-name", default="omc")
    parser.add_argument("--index", default="0")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repair-cif-spacegroup", action="store_true")
    parser.add_argument("--no-local-geometry", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    structure_path = args.structure
    spacegroup_sanitization: list[dict[str, str]] = []
    if args.cif_block is not None or args.cif_block_index is not None:
        extracted = Path("outputs") / "_structure_inference_blocks" / f"{safe_filename(args.structure_id)}.cif"
        block = write_ccdc_block(args.structure, extracted, block_id=args.cif_block, index=args.cif_block_index)
        spacegroup_sanitization = cif_spacegroup_replacements(block.text)
        structure_path = extracted

    if args.repair_cif_spacegroup and structure_path.suffix.lower() == ".cif":
        spacegroup_sanitization.extend(cif_spacegroup_replacements(
            structure_path.read_text(encoding="utf-8")
        ))

    index: int | str = int(args.index) if args.index.isdigit() else args.index
    atoms = _read_atoms(structure_path, index, repair_cif_spacegroup=args.repair_cif_spacegroup)
    model = _adapter(args)
    prediction = model.predict(atoms)
    row = {
        "structure_id": args.structure_id,
        "structure_path": str(args.structure),
        "read_structure_path": str(structure_path),
        "spacegroup_sanitization": spacegroup_sanitization,
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

    atomic_write_json(args.output, row)
    print(json.dumps({"output": str(args.output), "structure_id": args.structure_id, "backend": args.backend}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
