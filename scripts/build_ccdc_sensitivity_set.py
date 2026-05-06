"""Generate deterministic perturbation CIFs from a selected CCDC block."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from ase.io import read, write

from crystalprobe.datahub.ccdc import write_ccdc_block
from crystalprobe.insight.sensitivity import (
    default_sensitivity_specs,
    perturb_atoms,
    sensitivity_manifest,
    summarize_perturbation,
    write_json,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--block-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    reference_cif = args.output_dir / f"reference_{args.block_id}.cif"
    write_ccdc_block(args.source, reference_cif, block_id=args.block_id)
    reference = read(str(reference_cif))

    variants = []
    for spec in default_sensitivity_specs():
        atoms = reference.copy() if spec.name == "reference" else perturb_atoms(reference, spec)
        output = args.output_dir / f"{spec.name}.cif"
        write(str(output), atoms)
        variants.append(summarize_perturbation(reference, atoms, spec, path=output))

    manifest = sensitivity_manifest(
        title=args.title,
        source=str(args.source),
        block_id=args.block_id,
        variants=variants,
    )
    write_json(args.manifest, manifest)
    print(json.dumps({"manifest": str(args.manifest), "variants": len(variants)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
