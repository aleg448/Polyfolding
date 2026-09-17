from crystalprobe.datahub.cposs209 import CpossStructureRecord
from scripts.run_cposs_structure_inference import _filter_records
import pytest


def test_metadata_only_block_cannot_shift_inference_identity(tmp_path):
    pytest.importorskip("ase")
    from crystalprobe.datahub.cposs209 import index_cposs_cif
    from crystalprobe.uncertainty.base import EnergyForcePrediction
    from scripts.run_cposs_structure_inference import _prediction_row

    cell = ("_cell_length_a 8\n_cell_length_b 8\n_cell_length_c 8\n"
            "_cell_angle_alpha 90\n_cell_angle_beta 90\n_cell_angle_gamma 90\n"
            "loop_\n_atom_site_label\n_atom_site_type_symbol\n"
            "_atom_site_fract_x\n_atom_site_fract_y\n_atom_site_fract_z\n")
    path = tmp_path / "bundle.cif"
    path.write_text("data_META\n_note 'metadata only'\n"
                    + "data_IBP01\n" + cell + "O1 O 0 0 0\n"
                    + "data_IBP02\n" + cell + "H1 H 0 0 0\n", encoding="utf-8")
    records = index_cposs_cif(path, with_atoms=False)

    class Model:
        def predict(self, atoms):
            return EnergyForcePrediction(energy=0)

    row = _prediction_row(records[1], source_path=path, adapter=Model(), include_local_geometry=False)
    assert row["block_id"] == "IBP01"
    assert row["formula"] == "O"
    with pytest.raises(ValueError, match="coordinates"):
        _prediction_row(records[0], source_path=path, adapter=Model(), include_local_geometry=False)


def _record(block_id: str, family: str) -> CpossStructureRecord:
    return CpossStructureRecord(
        block_id=block_id,
        family_code=family,
        form_number=None,
        suffix=None,
        source_file="All_Psi_Crys.cif",
        source_index=0,
        formula=None,
        natoms=None,
        space_group=None,
        cell_setting=None,
        cell={},
    )


def test_filter_records_supports_family_block_id_and_limit():
    records = [
        _record("IBP01_PsiCrys", "IBP"),
        _record("IBP06_PsiCrys", "IBP"),
        _record("CBZ01_PsiCrys", "CBZ"),
    ]

    selected = _filter_records(
        records,
        families=["ibp"],
        block_ids=["ibp06_psicrys"],
        limit=1,
    )

    assert [record.block_id for record in selected] == ["IBP06_PsiCrys"]
