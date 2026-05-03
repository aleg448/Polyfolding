"""Smoke-test installed optional MLIP backends."""

from __future__ import annotations

import argparse
import json

from ase.build import molecule

from crystalprobe.foundry.optional_adapters import AIMNet2Adapter, MACEOffAdapter


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["mace", "aimnet", "all"], default="all")
    parser.add_argument("--device", default=None)
    args = parser.parse_args()

    atoms = molecule("H2O")
    results: dict[str, object] = {}

    if args.backend in {"mace", "all"}:
        prediction = MACEOffAdapter(model="small", device=args.device).predict(atoms)
        results["mace"] = {"energy": prediction.energy, "forces_shape": [len(prediction.forces), 3], "metadata": prediction.metadata}

    if args.backend in {"aimnet", "all"}:
        prediction = AIMNet2Adapter(device=args.device, needs_dispersion=False).predict(atoms)
        results["aimnet"] = {"energy": prediction.energy, "forces_shape": [len(prediction.forces), 3], "metadata": prediction.metadata}

    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

