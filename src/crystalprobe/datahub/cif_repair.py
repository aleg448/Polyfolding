"""Small CIF text repairs for local-only parser compatibility."""

from __future__ import annotations

from crystalprobe.datahub.ccdc import sanitize_cif_text


def repair_cif_spacegroup_text(text: str) -> str:
    """Normalize common CSD monoclinic P21 spellings that ASE cannot resolve.

    Delegates to the regex-based, whitespace-tolerant normalizer in
    :func:`crystalprobe.datahub.ccdc.sanitize_cif_text` so there is a single
    implementation instead of two divergent ones. The tag/whitespace prefix of
    each matched line is preserved; only the space-group value is rewritten.
    """

    return sanitize_cif_text(text)
