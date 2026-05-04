from pathlib import Path

from crystalprobe.datahub.ccdc import sanitize_cif_text, split_ccdc_cif, summarize_ccdc_blocks, write_ccdc_block


def test_split_ccdc_cif_ignores_preamble(tmp_path):
    cif = tmp_path / "bundle.cif"
    cif.write_text(
        """
# CCDC preamble
data_ONE
_chemical_name_common ibuprofen
_chemical_formula_sum 'C13 H18 O2'
_symmetry_space_group_name_H-M P21/c

data_TWO
_chemical_name_systematic '(+)-Amphetamine dihydrogen phosphate'
_chemical_formula_sum 'C9 H16 N O4 P'
_symmetry_space_group_name_H-M P2(1)
""".lstrip(),
        encoding="utf-8",
    )
    blocks = split_ccdc_cif(cif)
    assert [block.block_id for block in blocks] == ["ONE", "TWO"]
    summary = summarize_ccdc_blocks(blocks)
    assert summary["blocks"] == 2
    assert summary["formulas"]["C13 H18 O2"] == 1


def test_sanitize_cif_text_normalizes_space_groups():
    text = "_symmetry_space_group_name_H-M P2(1)\n_space_group_name_H-M_alt P21/c\n"
    sanitized = sanitize_cif_text(text)
    assert "'P 21'" in sanitized
    assert "'P 21/c'" in sanitized


def test_write_ccdc_block(tmp_path):
    cif = tmp_path / "bundle.cif"
    out = tmp_path / "out.cif"
    cif.write_text("data_ONE\n_chemical_formula_sum 'C'\n\ndata_TWO\n_chemical_formula_sum 'H2'\n", encoding="utf-8")
    block = write_ccdc_block(cif, out, block_id="TWO")
    assert block.block_id == "TWO"
    assert out.read_text(encoding="utf-8").startswith("data_TWO")
