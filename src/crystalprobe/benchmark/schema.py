"""Canonical schema for CrystalProbe polymorph-pair records."""

from __future__ import annotations

from enum import Enum
from pathlib import PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CurationStatus(str, Enum):
    """Lifecycle state for a benchmark record."""

    DRAFT = "draft"
    REVIEWED = "reviewed"
    VERIFIED = "verified"
    EXCLUDED = "excluded"


class SourceName(str, Enum):
    """Known source families for structures."""

    CPOSS209 = "CPOSS209"
    BLIND_TEST_7 = "blind_test_7"
    OMC25 = "OMC25"
    LITERATURE = "literature"
    POLARIS_CURATED = "POLARIS_curated"
    INTERNAL_FIXTURE = "internal_fixture"


LicenseName = Literal["CC-BY-4.0", "CC0-1.0", "Apache-2.0", "inherited_restricted", "unknown"]
StabilityOrdering = Literal["A>B", "B>A", "A=B (within error)", "ambiguous"]
FlexibilityClass = Literal["rigid", "semi_rigid", "flexible", "unknown"]


class StructureRef(BaseModel):
    """Reference to one crystal structure in a pair."""

    model_config = ConfigDict(extra="forbid")

    structure_id: str = Field(..., min_length=1)
    cif_path: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1, description="Human-readable form label, e.g. Form I")
    space_group: str | None = None
    z_prime: float | None = Field(default=None, ge=0)
    density_g_per_cm3: float | None = Field(default=None, gt=0)
    source: SourceName
    source_id: str = Field(..., min_length=1)
    license: LicenseName

    @field_validator("cif_path")
    @classmethod
    def cif_path_must_be_relative_posix(cls, value: str) -> str:
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("cif_path must be a relative POSIX path inside the dataset root")
        return value


class ExperimentalEvidence(BaseModel):
    """Experimental evidence for the relative stability assignment."""

    model_config = ConfigDict(extra="forbid")

    stability_ordering: StabilityOrdering
    temperature_K: float | None = Field(default=None, gt=0)
    relative_humidity: float | None = Field(default=None, ge=0, le=100)
    free_energy_diff_kJ_per_mol: float | None = None
    free_energy_diff_uncertainty_kJ_per_mol: float | None = Field(default=None, ge=0)
    citation_doi: str | None = None
    citation_url: str | None = None
    notes: str = ""

    @model_validator(mode="after")
    def require_citation_pointer(self) -> "ExperimentalEvidence":
        if not self.citation_doi and not self.citation_url and "TODO" not in self.notes.upper():
            raise ValueError("experimental evidence needs citation_doi, citation_url, or an explicit TODO note")
        return self


class ChemistryAnnotation(BaseModel):
    """Molecular and chemistry-slice metadata."""

    model_config = ConfigDict(extra="forbid")

    smiles: str = Field(..., min_length=1)
    inchi: str | None = None
    common_name: str | None = None
    cas_number: str | None = None
    flexibility_class: FlexibilityClass
    h_bond_motifs: list[str] = Field(default_factory=list)
    functional_groups: list[str] = Field(default_factory=list)
    has_halogen: bool
    has_charge: bool
    is_chiral: bool


class PolymorphPair(BaseModel):
    """One curated pair of polymorph structures for the same molecule."""

    model_config = ConfigDict(extra="forbid")

    pair_id: str = Field(..., min_length=1, pattern=r"^[a-z0-9][a-z0-9_\-]*$")
    molecule: ChemistryAnnotation
    structure_a: StructureRef
    structure_b: StructureRef
    evidence: ExperimentalEvidence
    curation_status: CurationStatus = CurationStatus.DRAFT
    chemistry_tags: list[str] = Field(default_factory=list)
    has_disorder: bool | None = None
    disorder_notes: str = ""
    notes: str = ""
    schema_version: str = "0.1.0"

    @model_validator(mode="after")
    def validate_pair_contract(self) -> "PolymorphPair":
        if self.structure_a.structure_id == self.structure_b.structure_id:
            raise ValueError("structure_a and structure_b must refer to different structures")

        if self.curation_status in {CurationStatus.REVIEWED, CurationStatus.VERIFIED}:
            serialized = self.model_dump_json().upper()
            if "TODO" in serialized:
                raise ValueError("reviewed or verified records cannot contain TODO placeholders")
            if self.evidence.stability_ordering == "ambiguous" and self.curation_status == CurationStatus.VERIFIED:
                raise ValueError("verified records cannot use ambiguous stability ordering")
            if self.has_disorder is None:
                raise ValueError("reviewed or verified records must explicitly set has_disorder")
        return self

    @property
    def experimental_winner(self) -> Literal["A", "B"] | None:
        """Return the experimentally more stable side when defined."""

        if self.evidence.stability_ordering == "A>B":
            return "A"
        if self.evidence.stability_ordering == "B>A":
            return "B"
        return None

