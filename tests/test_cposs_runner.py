from crystalprobe.datahub.cposs209 import CpossStructureRecord
from scripts.run_cposs_structure_inference import _filter_records


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
