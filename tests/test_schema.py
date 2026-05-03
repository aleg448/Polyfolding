import pytest

from crystalprobe.benchmark.schema import PolymorphPair


def _record(status="draft", ordering="ambiguous"):
    return {
        "pair_id": "fixture_pair",
        "molecule": {
            "smiles": "O",
            "inchi": "TODO",
            "common_name": "water fixture",
            "cas_number": None,
            "flexibility_class": "rigid",
            "h_bond_motifs": ["donor_acceptor"],
            "functional_groups": ["fixture"],
            "has_halogen": False,
            "has_charge": False,
            "is_chiral": False,
        },
        "structure_a": {
            "structure_id": "fixture_a",
            "cif_path": "cifs/a.cif",
            "label": "A",
            "space_group": None,
            "z_prime": None,
            "density_g_per_cm3": None,
            "source": "internal_fixture",
            "source_id": "fixture_a",
            "license": "CC0-1.0",
        },
        "structure_b": {
            "structure_id": "fixture_b",
            "cif_path": "cifs/b.cif",
            "label": "B",
            "space_group": None,
            "z_prime": None,
            "density_g_per_cm3": None,
            "source": "internal_fixture",
            "source_id": "fixture_b",
            "license": "CC0-1.0",
        },
        "evidence": {
            "stability_ordering": ordering,
            "temperature_K": None,
            "relative_humidity": None,
            "free_energy_diff_kJ_per_mol": None,
            "free_energy_diff_uncertainty_kJ_per_mol": None,
            "citation_doi": None,
            "citation_url": None,
            "notes": "TODO: fixture evidence",
        },
        "curation_status": status,
        "chemistry_tags": ["fixture"],
        "has_disorder": None,
        "disorder_notes": "TODO",
        "notes": "TODO fixture",
        "schema_version": "0.1.0",
    }


def test_draft_record_allows_todo_placeholders():
    pair = PolymorphPair.model_validate(_record())
    assert pair.experimental_winner is None


def test_verified_record_rejects_todo_placeholders():
    with pytest.raises(ValueError, match="TODO"):
        PolymorphPair.model_validate(_record(status="verified", ordering="A>B"))


def test_cif_path_must_stay_inside_dataset_root():
    record = _record()
    record["structure_a"]["cif_path"] = "../outside.cif"
    with pytest.raises(ValueError, match="relative POSIX path"):
        PolymorphPair.model_validate(record)

