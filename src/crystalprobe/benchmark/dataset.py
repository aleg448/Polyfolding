"""Dataset loading and validation helpers."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Iterator
from pathlib import Path

from crystalprobe.benchmark.schema import CurationStatus, PolymorphPair


class BenchmarkDataset:
    """In-memory view over a JSON Lines polymorph-pair manifest."""

    def __init__(self, pairs: Iterable[PolymorphPair], *, root: Path | None = None) -> None:
        self.pairs = list(pairs)
        self.root = root

    def __iter__(self) -> Iterator[PolymorphPair]:
        return iter(self.pairs)

    def __len__(self) -> int:
        return len(self.pairs)

    def __getitem__(self, index: int) -> PolymorphPair:
        return self.pairs[index]

    def by_status(self, status: CurationStatus | str) -> "BenchmarkDataset":
        status_value = CurationStatus(status)
        return BenchmarkDataset([pair for pair in self.pairs if pair.curation_status == status_value], root=self.root)

    def verified(self) -> "BenchmarkDataset":
        return self.by_status(CurationStatus.VERIFIED)

    def slice_by_tag(self, tag: str) -> "BenchmarkDataset":
        return BenchmarkDataset([pair for pair in self.pairs if tag in pair.chemistry_tags], root=self.root)

    def pair_ids(self) -> list[str]:
        return [pair.pair_id for pair in self.pairs]

    def summary(self) -> dict[str, object]:
        statuses = Counter(pair.curation_status.value for pair in self.pairs)
        tags = Counter(tag for pair in self.pairs for tag in pair.chemistry_tags)
        sources = Counter(
            source.value
            for pair in self.pairs
            for source in (pair.structure_a.source, pair.structure_b.source)
        )
        orderings = Counter(pair.evidence.stability_ordering for pair in self.pairs)
        molecules = {
            pair.molecule.common_name or pair.molecule.smiles
            for pair in self.pairs
        }
        return {
            "pairs": len(self.pairs),
            "molecules": len(molecules),
            "statuses": dict(sorted(statuses.items())),
            "stability_orderings": dict(sorted(orderings.items())),
            "top_chemistry_tags": dict(tags.most_common(10)),
            "structure_sources": dict(sorted(sources.items())),
        }

    def validate_unique_pair_ids(self) -> None:
        counts = Counter(self.pair_ids())
        duplicates = sorted(pair_id for pair_id, count in counts.items() if count > 1)
        if duplicates:
            raise ValueError(f"duplicate pair_id values: {', '.join(duplicates)}")

    def validate_structure_files(self) -> list[str]:
        """Return missing CIF paths relative to the dataset root."""

        if self.root is None:
            raise ValueError("dataset root is not set")

        missing: list[str] = []
        for pair in self.pairs:
            for structure in (pair.structure_a, pair.structure_b):
                path = self.root / structure.cif_path
                if not path.exists():
                    missing.append(structure.cif_path)
        return sorted(set(missing))


def load_manifest(path: str | Path) -> BenchmarkDataset:
    """Load a CrystalProbe JSON Lines manifest."""

    manifest_path = Path(path)
    pairs: list[PolymorphPair] = []
    with manifest_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                pairs.append(PolymorphPair.model_validate_json(stripped))
            except Exception as exc:
                raise ValueError(f"{manifest_path}:{line_number}: invalid polymorph pair: {exc}") from exc

    dataset = BenchmarkDataset(pairs, root=manifest_path.parent)
    dataset.validate_unique_pair_ids()
    return dataset


def write_manifest(dataset: BenchmarkDataset, path: str | Path) -> None:
    """Write a dataset as JSON Lines with stable key ordering."""

    manifest_path = Path(path)
    with manifest_path.open("w", encoding="utf-8", newline="\n") as handle:
        for pair in dataset:
            data = pair.model_dump(mode="json")
            handle.write(json.dumps(data, sort_keys=True, separators=(",", ":")))
            handle.write("\n")

