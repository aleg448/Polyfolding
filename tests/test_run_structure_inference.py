from crystalprobe.datahub.cif_repair import repair_cif_spacegroup_text


def test_repair_cif_spacegroup_text_normalizes_common_p21_spelling():
    text = "_space_group_name_H-M_alt        'P 1 21 1'\n"

    assert "_space_group_name_H-M_alt        'P 21'" in repair_cif_spacegroup_text(text)
