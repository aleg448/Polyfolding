"""Small CIF text repairs for local-only parser compatibility."""

from __future__ import annotations


def repair_cif_spacegroup_text(text: str) -> str:
    """Normalize common CSD monoclinic P21 spellings that ASE cannot resolve."""

    return (
        text.replace("_space_group_name_H-M_alt        'P 1 21 1'", "_space_group_name_H-M_alt        'P 21'")
        .replace("_symmetry_space_group_name_H-M   'P 1 21 1'", "_symmetry_space_group_name_H-M   'P 21'")
        .replace("_space_group_name_H-M_alt 'P 1 21 1'", "_space_group_name_H-M_alt 'P 21'")
        .replace("_symmetry_space_group_name_H-M 'P 1 21 1'", "_symmetry_space_group_name_H-M 'P 21'")
    )
