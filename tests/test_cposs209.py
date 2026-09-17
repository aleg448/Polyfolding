from pathlib import Path

from crystalprobe.datahub.cposs209 import (
    generate_cposs_pair_candidates,
    index_cposs_cif,
    iter_cif_block_ids,
    parse_cposs_block_id,
    summarize_cposs_pair_candidates,
    summarize_cposs_records,
)


def _write_tiny_cif(path: Path) -> None:
    path.write_text(
        """
data_CRN01_PsiCrys
_symmetry_cell_setting           monoclinic
_symmetry_space_group_name_H-M   'P 21/c'
_cell_length_a                   10.1
_cell_length_b                   3.7
_cell_length_c                   19.2
_cell_angle_alpha                90
_cell_angle_beta                 116.7
_cell_angle_gamma                90
_cell_volume                     659.7

data_ACR12_PsiMol
_symmetry_cell_setting           triclinic
_symmetry_space_group_name_H-M   'P -1'
_cell_length_a                   4.1
_cell_length_b                   5.2
_cell_length_c                   6.3
_cell_angle_alpha                88.1
_cell_angle_beta                 91.2
_cell_angle_gamma                92.3
_cell_volume                     120.5
""".lstrip(),
        encoding="utf-8",
        newline="\n",
    )


def test_parse_cposs_block_id():
    assert parse_cposs_block_id("CRN01_PsiCrys") == ("CRN", 1, "PsiCrys")
    assert parse_cposs_block_id("ACR12_PsiMol") == ("ACR", 12, "PsiMol")
    assert parse_cposs_block_id("unstructured") == ("unstructured", None, None)


def test_iter_cif_block_ids_without_ase(tmp_path):
    cif = tmp_path / "tiny.cif"
    _write_tiny_cif(cif)
    assert iter_cif_block_ids(cif) == ["CRN01_PsiCrys", "ACR12_PsiMol"]


def test_index_cposs_cif_without_atom_metadata(tmp_path):
    cif = tmp_path / "tiny.cif"
    _write_tiny_cif(cif)
    records = index_cposs_cif(cif, with_atoms=False)
    assert [record.block_id for record in records] == ["CRN01_PsiCrys", "ACR12_PsiMol"]
    assert records[0].family_code == "CRN"
    assert records[0].form_number == 1
    assert records[0].space_group == "P 21/c"
    assert records[0].cell["volume"] == 659.7
    assert records[0].formula is None


def test_index_cposs_cif_tolerates_cif_null_cell_values(tmp_path):
    cif = tmp_path / "nulls.cif"
    cif.write_text(
        """
data_NUL01_PsiCrys
_symmetry_space_group_name_H-M   'P 21/c'
_cell_length_a                   10.1
_cell_length_b                   ?
_cell_length_c                   .
_cell_angle_beta                 116.7(3)
_cell_angle_alpha                nan
_cell_angle_gamma                inf
_cell_volume                     659.7
""".lstrip(),
        encoding="utf-8",
        newline="\n",
    )
    records = index_cposs_cif(cif, with_atoms=False)
    assert len(records) == 1
    cell = records[0].cell
    assert cell["a"] == 10.1
    assert cell["volume"] == 659.7
    assert cell["beta"] == 116.7  # standard-uncertainty suffix stripped
    assert "b" not in cell  # '?' null marker skipped
    assert "c" not in cell  # '.' null marker skipped
    assert "alpha" not in cell
    assert "gamma" not in cell


def test_index_cposs_cif_skips_multiline_text_fields(tmp_path):
    # A ';'-delimited text field contains a 'data_' token and a fake cell-length
    # line. Neither must be parsed as a real block or tag.
    cif = tmp_path / "text_field.cif"
    cif.write_text(
        """
data_REAL01_PsiCrys
_symmetry_space_group_name_H-M   'P 21/c'
_journal_paper_doi
;
Discussion of data_FAKE99 with _cell_length_a 999.9 inside prose.
;
_cell_length_a                   10.1
_cell_volume                     659.7
""".lstrip(),
        encoding="utf-8",
        newline="\n",
    )
    assert iter_cif_block_ids(cif) == ["REAL01_PsiCrys"]
    records = index_cposs_cif(cif, with_atoms=False)
    assert len(records) == 1
    assert records[0].block_id == "REAL01_PsiCrys"
    assert records[0].cell["a"] == 10.1  # real tag after the text field is still read
    assert records[0].cell["volume"] == 659.7


def test_summarize_cposs_records(tmp_path):
    cif = tmp_path / "tiny.cif"
    _write_tiny_cif(cif)
    records = index_cposs_cif(cif, with_atoms=False)
    summary = summarize_cposs_records(records)
    assert summary["records"] == 2
    assert summary["families"] == 2
    assert summary["family_counts"] == {"ACR": 1, "CRN": 1}


def test_generate_adjacent_pair_candidates(tmp_path):
    cif = tmp_path / "tiny.cif"
    _write_tiny_cif(cif)
    records = index_cposs_cif(cif, with_atoms=False)
    extra = records[0].__class__(
        block_id="CRN02_PsiCrys",
        family_code="CRN",
        form_number=2,
        suffix="PsiCrys",
        source_file="tiny.cif",
        source_index=2,
        formula=None,
        natoms=None,
        space_group="P 21/c",
        cell_setting="monoclinic",
        cell={},
    )
    candidates = generate_cposs_pair_candidates([records[0], extra, records[1]], mode="adjacent")
    assert len(candidates) == 1
    assert candidates[0].pair_id == "cposs209_crn_crn01_psicrys_vs_crn02_psicrys"
    assert candidates[0].stability_status == "uncurated"


def test_generate_all_pair_candidates(tmp_path):
    cif = tmp_path / "tiny.cif"
    _write_tiny_cif(cif)
    records = index_cposs_cif(cif, with_atoms=False)
    candidates = generate_cposs_pair_candidates(records, mode="all")
    summary = summarize_cposs_pair_candidates(candidates)
    assert summary["candidate_pairs"] == 0
