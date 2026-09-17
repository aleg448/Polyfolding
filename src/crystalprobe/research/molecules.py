"""Compile the existing molecule panel into reproducible research tasks."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

from crystalprobe.core.ledger import object_sha256
from crystalprobe.insight.tentative_molecule_benchmark import MoleculeRecord
from crystalprobe.research.campaign import Campaign, ResearchTask


def molecule_campaign(
    records: Iterable[MoleculeRecord], *, campaign_id: str = "molecule_qa",
    backends: tuple[str, ...] = (), python: str = sys.executable,
    backend_pythons: dict[str, str] | None = None,
    mace_checkpoint: str | None = None, device: str = "cpu", seed: int = 61453,
) -> Campaign:
    tasks = []
    backend_pythons = backend_pythons or {}
    if len(backends) != len(set(backends)) or set(backends) - {"mace", "aimnet2", "uma"}:
        raise ValueError("backends must be unique supported adapter names")
    for record in records:
        identity = object_sha256(record.molecule_id)[:16]
        task_id = f"conformer.{identity}"
        stable_seed = (seed + int(identity[:8], 16)) % (2**31 - 1)
        tasks.append(ResearchTask(
            task_id=task_id, kind="conformer", python=python,
            parameters={"molecule": record.as_dict(), "seed": stable_seed},
        ))
        for backend in backends:
            options: dict[str, object] = {"device": device}
            files = []
            if backend == "mace" and mace_checkpoint:
                checkpoint = str(Path(mace_checkpoint).resolve())
                options["mace_model"] = checkpoint
                files.append(checkpoint)
            tasks.append(ResearchTask(
                task_id=f"{backend}.{identity}", kind="backend", dependencies=[task_id],
                parameters={"backend": backend, "options": options, "molecule_id": record.molecule_id},
                python=backend_pythons.get(backend, python), input_files=files,
                cacheable=bool(files),
            ))
    return Campaign(campaign_id=campaign_id, tasks=tasks, question=(
        "Which molecules expose conformer-generation, backend execution, or energy/force sanity failures?"
    ))
