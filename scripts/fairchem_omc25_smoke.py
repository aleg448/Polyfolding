"""Smoke-test fairchem with a permitted OMC25 checkpoint.

The UMA checkpoint family is distributed from a separate gated Hugging Face
repository. This script keeps the OMC25 checkpoint test independent so token
plumbing, fairchem installation, and CUDA execution can be validated even while
UMA access is still pending.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from ase.build import molecule


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _device(preferred: str) -> str:
    if preferred != "auto":
        return preferred

    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


def _download_checkpoint(repo_id: str, filename: str, token: str | None) -> Path:
    from huggingface_hub import hf_hub_download

    return Path(
        hf_hub_download(
            repo_id=repo_id,
            repo_type="model",
            filename=filename,
            token=token,
        )
    )


def _water_smoke(checkpoint: Path, task_name: str, device: str) -> dict[str, Any]:
    from fairchem.core import FAIRChemCalculator

    atoms = molecule("H2O")
    atoms.set_cell([12.0, 12.0, 12.0])
    atoms.center()
    atoms.pbc = True
    atoms.calc = FAIRChemCalculator.from_model_checkpoint(
        str(checkpoint),
        task_name=task_name,
        device=device,
    )
    energy = float(atoms.get_potential_energy())
    forces = atoms.get_forces()
    return {
        "energy_ev": energy,
        "forces_shape": list(forces.shape),
        "device": device,
    }


def _try_uma(task_name: str, device: str) -> dict[str, Any]:
    try:
        from fairchem.core import FAIRChemCalculator

        FAIRChemCalculator.from_model_checkpoint(
            "uma-s-1p2",
            task_name=task_name,
            device=device,
        )
    except Exception as exc:  # pragma: no cover - depends on gated remote access.
        text = f"{type(exc).__name__}: {exc}"
        blocked = "facebook/UMA" in text or "GatedRepoError" in text or "403" in text
        return {
            "available": False,
            "blocked_by_access": blocked,
            "error_type": type(exc).__name__,
            "message": str(exc).splitlines()[0][:500],
        }
    return {
        "available": True,
        "blocked_by_access": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", default="facebook/OMC25")
    parser.add_argument("--checkpoint", default="checkpoints/esen_s.pt")
    parser.add_argument("--task-name", default="omc")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--try-uma", action="store_true")
    parser.add_argument(
        "--require-token",
        action="store_true",
        help="Fail instead of skipping when HF_TOKEN is not present.",
    )
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    device = _device(args.device)
    result: dict[str, Any] = {
        "hf_token_present": bool(token),
        "repo_id": args.repo_id,
        "checkpoint": args.checkpoint,
        "task_name": args.task_name,
        "device": device,
    }

    if not token:
        result["status"] = "skipped"
        result["reason"] = "HF_TOKEN is not present"
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2 if args.require_token else 0

    checkpoint_path = _download_checkpoint(args.repo_id, args.checkpoint, token)
    result["checkpoint_cache_path"] = str(checkpoint_path)
    result["checkpoint_sha256"] = _sha256(checkpoint_path)
    result["water_smoke"] = _water_smoke(checkpoint_path, args.task_name, device)

    if args.try_uma:
        result["uma_s_1p2"] = _try_uma(args.task_name, device)

    result["status"] = "ok"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
