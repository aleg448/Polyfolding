"""Known data/model sources used by CrystalProbe."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataSource:
    name: str
    kind: str
    url: str
    license: str
    access_notes: str


def source_registry() -> list[DataSource]:
    """Return the curated source registry for data acquisition planning."""

    return [
        DataSource(
            name="CPOSS209",
            kind="benchmark_dataset",
            url="https://acs.figshare.com/articles/dataset/28883051",
            license="See ACS/Figshare item; verify before redistribution",
            access_notes="Primary CrystalProbe curation target; download requires network access.",
        ),
        DataSource(
            name="OMC25 dataset",
            kind="training_dataset",
            url="https://huggingface.co/datasets/facebook/OMC25",
            license="CC-BY-4.0",
            access_notes="Large ASE-LMDB dataset; Hugging Face access approval may be required.",
        ),
        DataSource(
            name="OMC25/UMA models",
            kind="model_checkpoint",
            url="https://huggingface.co/facebook/OMC25",
            license="Model licenses vary; verify per checkpoint",
            access_notes="Use through fairchem after accepting repository terms.",
        ),
        DataSource(
            name="fairchem",
            kind="code",
            url="https://github.com/facebookresearch/fairchem",
            license="MIT for code; model/data licenses vary",
            access_notes="Needed for UMA and FastCSP-family integration.",
        ),
        DataSource(
            name="MACE-OFF23",
            kind="model_checkpoint",
            url="https://mace-docs.readthedocs.io/en/latest/guide/foundation_models.html",
            license="Academic Software License for checkpoints",
            access_notes="Use through MACE ASE calculator; verify license compatibility for public workflows.",
        ),
    ]

