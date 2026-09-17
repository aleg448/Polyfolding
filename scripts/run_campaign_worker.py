"""Isolated scientific worker for a single research campaign task."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
from pathlib import Path

from crystalprobe.core.io import atomic_write_json
from crystalprobe.core.ledger import file_sha256
from crystalprobe.insight.backend_ready_inputs import backend_ready_inputs_report
from crystalprobe.insight.backend_smoke import backend_smoke_report
from crystalprobe.insight.conformer_generation import conformer_generation_report
from crystalprobe.insight.tentative_molecule_benchmark import MoleculeRecord


def execute(request: dict, directory: Path) -> dict:
    for path, expected in request["input_hashes"].items():
        if file_sha256(path) != expected:
            raise ValueError(f"input hash mismatch: {path}")
    parameters = request["parameters"]
    artifacts = []
    if request["kind"] == "conformer":
        molecule = MoleculeRecord(**parameters["molecule"])
        report = conformer_generation_report(
            [molecule], random_seed=parameters["seed"], write_xyz_dir=directory / "coordinates",
        )
        row = report["rows"][0]
        state = {"generated": "succeeded", "warning": "succeeded", "blocked": "blocked"}.get(row["status"], "failed")
        if row["xyz_path"]:
            xyz = Path(row["xyz_path"])
            artifacts.append(str(xyz.relative_to(directory)))
            row["xyz_sha256"] = file_sha256(xyz)
        payload = {"conformer": row}
    elif request["kind"] == "backend":
        parents = list(request["parents"].values())
        if len(parents) != 1:
            raise ValueError("a backend task requires exactly one conformer parent")
        conformer = parents[0]["payload"]["conformer"]
        if file_sha256(conformer["xyz_path"]) != conformer["xyz_sha256"]:
            raise ValueError("conformer changed since generation")
        manifest = backend_ready_inputs_report({"rows": [conformer]}, base_dir=Path.cwd())
        report = backend_smoke_report(
            manifest, backends=[parameters["backend"]], device=parameters["options"].get("device", "cpu"),
            backend_options=parameters["options"],
        )
        row = report["benchmark_rows"][0]
        state = {"passed": "succeeded", "warning": "succeeded", "blocked": "blocked"}.get(row["status"], "failed")
        payload = {"backend_row": row}
    else:
        raise ValueError("unknown worker kind")
    return {"execution_status": state, "review_status": "candidate_unverified", "artifacts": artifacts,
            "detail": row["detail"], **payload}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding="utf-8"))
    result = execute(request, args.output.parent)
    atomic_write_json(args.output, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
