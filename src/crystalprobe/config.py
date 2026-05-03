"""Typed run configuration for reproducible CrystalProbe workflows."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class QuickBenchmarkConfig(BaseModel):
    """Configuration for the dependency-light quick benchmark."""

    model_config = ConfigDict(extra="forbid")

    manifest: str = Field(..., min_length=1)
    predictions: str = Field(..., min_length=1)
    output_dir: str = Field(..., min_length=1)
    ledger: str | None = None
    verified_only: bool = False


class CrystalProbeConfig(BaseModel):
    """Top-level workflow config."""

    model_config = ConfigDict(extra="forbid")

    workflow: str = Field(..., pattern=r"^quick_benchmark$")
    quick_benchmark: QuickBenchmarkConfig


def load_config(path: str | Path) -> CrystalProbeConfig:
    config_path = Path(path)
    return CrystalProbeConfig.model_validate_json(config_path.read_text(encoding="utf-8"))


def write_config(config: CrystalProbeConfig, path: str | Path) -> None:
    config_path = Path(path)
    config_path.write_text(
        json.dumps(config.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

