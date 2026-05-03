"""Behavioural fingerprint analysis over polymorph-pair predictions."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Mapping

from crystalprobe.benchmark.metrics import PairEnergyPrediction, RankingAccuracy, ranking_accuracy
from crystalprobe.benchmark.schema import PolymorphPair


@dataclass(frozen=True)
class SliceResult:
    name: str
    correct: int
    evaluated: int
    skipped: int
    accuracy: float | None


@dataclass(frozen=True)
class FingerprintReport:
    overall: SliceResult
    by_tag: list[SliceResult]
    by_flexibility: list[SliceResult]
    by_halogen: list[SliceResult]
    by_charge: list[SliceResult]

    def as_dict(self) -> dict[str, object]:
        return {
            "overall": self.overall.__dict__,
            "by_tag": [result.__dict__ for result in self.by_tag],
            "by_flexibility": [result.__dict__ for result in self.by_flexibility],
            "by_halogen": [result.__dict__ for result in self.by_halogen],
            "by_charge": [result.__dict__ for result in self.by_charge],
        }


def build_fingerprint_report(
    pairs: list[PolymorphPair],
    predictions: Mapping[str, PairEnergyPrediction],
    *,
    min_slice_size: int = 1,
) -> FingerprintReport:
    """Build a behavioural fingerprint from pairwise energy predictions."""

    return FingerprintReport(
        overall=_slice_result("overall", ranking_accuracy(pairs, predictions)),
        by_tag=_slice_many(_group_by_tag(pairs), predictions, min_slice_size=min_slice_size),
        by_flexibility=_slice_many(_group_by_field(pairs, lambda pair: pair.molecule.flexibility_class), predictions, min_slice_size=min_slice_size),
        by_halogen=_slice_many(_group_by_field(pairs, lambda pair: f"has_halogen={pair.molecule.has_halogen}"), predictions, min_slice_size=min_slice_size),
        by_charge=_slice_many(_group_by_field(pairs, lambda pair: f"has_charge={pair.molecule.has_charge}"), predictions, min_slice_size=min_slice_size),
    )


def _slice_result(name: str, result: RankingAccuracy) -> SliceResult:
    return SliceResult(
        name=name,
        correct=result.correct,
        evaluated=result.evaluated,
        skipped=result.skipped,
        accuracy=result.accuracy,
    )


def _slice_many(
    groups: dict[str, list[PolymorphPair]],
    predictions: Mapping[str, PairEnergyPrediction],
    *,
    min_slice_size: int,
) -> list[SliceResult]:
    rows: list[SliceResult] = []
    for name, pairs in sorted(groups.items()):
        if len(pairs) < min_slice_size:
            continue
        rows.append(_slice_result(name, ranking_accuracy(pairs, predictions)))
    return rows


def _group_by_tag(pairs: list[PolymorphPair]) -> dict[str, list[PolymorphPair]]:
    groups: dict[str, list[PolymorphPair]] = defaultdict(list)
    for pair in pairs:
        for tag in pair.chemistry_tags:
            groups[tag].append(pair)
    return dict(groups)


def _group_by_field(pairs: list[PolymorphPair], key_fn) -> dict[str, list[PolymorphPair]]:
    groups: dict[str, list[PolymorphPair]] = defaultdict(list)
    for pair in pairs:
        groups[str(key_fn(pair))].append(pair)
    return dict(groups)

