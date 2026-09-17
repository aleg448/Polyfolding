from crystalprobe.core.paths import safe_filename
from pathlib import PurePosixPath
import pytest


@pytest.mark.parametrize("name", ["CON", "con.txt", "LPT1", "AUX.cif", "NUL"])
def test_safe_filename_avoids_windows_devices(name):
    assert safe_filename(name).split(".")[0].upper() not in {"CON", "LPT1", "AUX", "NUL"}


def test_filename_fallback_cannot_escape_directory():
    assert "/" not in safe_filename("", fallback="../../outside")
    assert "\\" not in safe_filename("", fallback="..\\outside")


def test_windows_separators_are_normalized_on_posix(monkeypatch):
    monkeypatch.setattr("crystalprobe.core.paths.Path", PurePosixPath)
    assert safe_filename("..\\..\\windows") == "windows"
    assert safe_filename("directory\\windows") == "windows"


def test_safe_filename_strips_directory_traversal():
    assert safe_filename("../../secret") == "secret"
    assert safe_filename("a/b/c") == "c"
    assert safe_filename("..\\..\\windows") == "windows"


def test_safe_filename_normalizes_unusual_characters():
    assert safe_filename("form I (draft)") == "form_I_draft"
    assert safe_filename("CRN01_PsiCrys") == "CRN01_PsiCrys"


def test_safe_filename_falls_back_for_empty_or_dotted_names():
    assert safe_filename("..") == "structure"
    assert safe_filename("") == "structure"
    assert safe_filename("...", fallback="block") == "block"
