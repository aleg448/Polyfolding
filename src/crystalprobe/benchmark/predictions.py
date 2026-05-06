"""Prediction file models for benchmark scoring."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from crystalprobe.benchmark.metrics import PairEnergyPrediction
from crystalprobe.core.io import atomic_write_text


class PairEnergyPredictionRecord(BaseModel):
    """JSON-serializable prediction for one polymorph pair."""

    model_config = ConfigDict(extra="forbid")

    pair_id: str = Field(..., min_length=1)
    energy_a: float
    energy_b: float
    energy_uncertainty_a: float | None = None
    energy_uncertainty_b: float | None = None
    ood_score_a: float | None = None
    ood_score_b: float | None = None
    ood_flag_a: bool = False
    ood_flag_b: bool = False
    energy_unit: str = "eV"
    model_name: str
    model_version: str | None = None
    notes: str = ""

    def as_metric_prediction(self) -> PairEnergyPrediction:
        return PairEnergyPrediction(energy_a=self.energy_a, energy_b=self.energy_b)


def load_pair_energy_predictions(path: str | Path) -> dict[str, PairEnergyPrediction]:
    """Load pair energy predictions from a JSON Lines file."""

    prediction_path = Path(path)
    predictions: dict[str, PairEnergyPrediction] = {}
    with prediction_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                record = PairEnergyPredictionRecord.model_validate_json(stripped)
            except Exception as exc:
                raise ValueError(f"{prediction_path}:{line_number}: invalid prediction: {exc}") from exc
            if record.pair_id in predictions:
                raise ValueError(f"{prediction_path}:{line_number}: duplicate pair_id {record.pair_id}")
            predictions[record.pair_id] = record.as_metric_prediction()
    return predictions


def load_pair_energy_prediction_records(path: str | Path) -> list[PairEnergyPredictionRecord]:
    """Load full prediction records from a JSON Lines file."""

    prediction_path = Path(path)
    records: list[PairEnergyPredictionRecord] = []
    seen: set[str] = set()
    with prediction_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                record = PairEnergyPredictionRecord.model_validate_json(stripped)
            except Exception as exc:
                raise ValueError(f"{prediction_path}:{line_number}: invalid prediction: {exc}") from exc
            if record.pair_id in seen:
                raise ValueError(f"{prediction_path}:{line_number}: duplicate pair_id {record.pair_id}")
            seen.add(record.pair_id)
            records.append(record)
    return records


def write_pair_energy_predictions(records: list[PairEnergyPredictionRecord], path: str | Path) -> None:
    rows = [
        json.dumps(record.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        for record in records
    ]
    atomic_write_text(path, "\n".join(rows) + ("\n" if rows else ""))
