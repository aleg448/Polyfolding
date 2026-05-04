from crystalprobe.core.paths import portable_path


def test_portable_path_normalizes_windows_separators(tmp_path, monkeypatch):
    nested = tmp_path / "outputs" / "ampetp_sensitivity"
    nested.mkdir(parents=True)
    target = nested / "reference.cif"
    target.write_text("data_reference\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert portable_path("outputs\\ampetp_sensitivity\\reference.cif") == target.relative_to(tmp_path)
