from crystalprobe.datahub.ccdc import (
    cif_spacegroup_replacements,
    sanitize_cif_text,
    split_ccdc_cif,
    summarize_ccdc_blocks,
    write_ccdc_block,
)


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


def test_parse_tags_skips_multiline_text_field_contents(tmp_path):
    cif = tmp_path / "bundle.cif"
    cif.write_text(
        """
data_ONE
_chemical_name_common ibuprofen
_chemical_formula_sum 'C13 H18 O2'
_journal_note
;
Prose mentioning _chemical_formula_sum 'C99 H99' that must not be parsed.
;
_symmetry_space_group_name_H-M P21/c
""".lstrip(),
        encoding="utf-8",
    )
    blocks = split_ccdc_cif(cif)
    assert len(blocks) == 1
    # The real formula wins; the '_chemical_formula_sum' buried in prose is ignored.
    assert blocks[0].tags["_chemical_formula_sum"] == "C13 H18 O2"


def test_sanitize_cif_text_normalizes_space_groups():
    text = "_symmetry_space_group_name_H-M P2(1)\n_space_group_name_H-M_alt P21/c\n"
    sanitized = sanitize_cif_text(text)
    assert "'P 21'" in sanitized
    assert "'P 21/c'" in sanitized


def test_cif_spacegroup_replacements_reports_applied_normalizations():
    text = "_symmetry_space_group_name_H-M P2(1)\n_space_group_name_H-M_alt P21/c\n"
    changes = cif_spacegroup_replacements(text)
    pairs = {(change["from"], change["to"]) for change in changes}
    assert ("P2(1)", "P 21") in pairs
    assert ("P21/c", "P 21/c") in pairs
    # No space-group tags -> nothing recorded.
    assert cif_spacegroup_replacements("_cell_length_a 10.1\n") == []


def test_multiline_prose_cannot_create_blocks_or_be_rewritten(tmp_path):
    text = ("data_REAL\n_note\n;\ndata_FAKE\n"
            "_symmetry_space_group_name_H-M P2(1)\n;\n_cell_length_a 10\n")
    path = tmp_path / "prose.cif"
    path.write_text(text, encoding="utf-8")
    blocks = split_ccdc_cif(path)
    assert [block.block_id for block in blocks] == ["REAL"]
    assert blocks[0].tags["_cell_length_a"] == "10"
    assert sanitize_cif_text(text) == text
    assert cif_spacegroup_replacements(text) == []


def test_write_ccdc_block(tmp_path):
    cif = tmp_path / "bundle.cif"
    out = tmp_path / "out.cif"
    cif.write_text("data_ONE\n_chemical_formula_sum 'C'\n\ndata_TWO\n_chemical_formula_sum 'H2'\n", encoding="utf-8")
    block = write_ccdc_block(cif, out, block_id="TWO")
    assert block.block_id == "TWO"
    assert out.read_text(encoding="utf-8").startswith("data_TWO")
