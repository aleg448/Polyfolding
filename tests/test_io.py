import json

from crystalprobe.core import atomic_write_json as exported_atomic_write_json
from crystalprobe.core import atomic_write_text as exported_atomic_write_text
from crystalprobe.core.io import atomic_write_json, atomic_write_text


def test_atomic_write_text_replaces_existing_file(tmp_path):
    target = tmp_path / "artifact.md"
    target.write_text("old", encoding="utf-8")

    atomic_write_text(target, "new\n")

    assert target.read_text(encoding="utf-8") == "new\n"
    assert list(tmp_path.glob("*.tmp")) == []


def test_atomic_write_json_writes_stable_json(tmp_path):
    target = tmp_path / "artifact.json"

    atomic_write_json(target, {"b": 2, "a": 1})

    assert json.loads(target.read_text(encoding="utf-8")) == {"a": 1, "b": 2}
    assert target.read_text(encoding="utf-8").startswith("{\n  \"a\"")


def test_atomic_write_text_can_run_repeated_replacements(tmp_path):
    target = tmp_path / "artifact.md"

    for index in range(20):
        atomic_write_text(target, f"value {index}\n")

    assert target.read_text(encoding="utf-8") == "value 19\n"
    assert list(tmp_path.glob("*.tmp")) == []


def test_atomic_writers_are_exported_from_core_package():
    assert exported_atomic_write_json is atomic_write_json
    assert exported_atomic_write_text is atomic_write_text
