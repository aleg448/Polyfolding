from scripts import run_structure_inference as rsi
from crystalprobe.datahub.cif_repair import repair_cif_spacegroup_text
from crystalprobe.uncertainty.base import EnergyForcePrediction
import json
import sys
from types import SimpleNamespace
import pytest


@pytest.mark.parametrize("repair", [False, True])
def test_extraction_sanitization_is_preserved_in_provenance(tmp_path, monkeypatch, repair):
    class Atoms:
        pbc = [False] * 3

        def __len__(self):
            return 1

        def get_chemical_formula(self):
            return "C"

    monkeypatch.chdir(tmp_path)
    source = tmp_path / "input.cif"
    source.write_text("data_ONE\n_symmetry_space_group_name_H-M P2(1)\n", encoding="utf-8")
    output = tmp_path / "result.json"
    argv = ["inference", str(source), "--structure-id", "one", "--cif-block", "ONE",
            "--output", str(output), "--no-local-geometry"]
    if repair:
        argv.append("--repair-cif-spacegroup")
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(rsi, "_read_atoms", lambda *args, **kwargs: Atoms())
    monkeypatch.setattr(rsi, "_adapter", lambda args: SimpleNamespace(
        predict=lambda atoms: EnergyForcePrediction(energy=0),
    ))
    assert rsi.main() == 0
    assert json.loads(output.read_text())["spacegroup_sanitization"] == [{"from": "P2(1)", "to": "P 21"}]


def test_aimnet_charge_and_cluster_flags_are_forwarded(monkeypatch):
    captured = {}

    class _FakeAIMNet2Adapter:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(rsi, "AIMNet2Adapter", _FakeAIMNet2Adapter)
    args = rsi.build_parser().parse_args(
        [
            "structure.cif",
            "--structure-id",
            "salt_cation",
            "--backend",
            "aimnet2",
            "--aimnet-charge",
            "1.0",
            "--allow-periodic-cluster",
            "--output",
            "out.json",
        ]
    )
    rsi._adapter(args)
    assert captured["charge"] == 1.0
    assert captured["allow_periodic_cluster"] is True


def test_aimnet_charge_defaults_to_neutral_non_cluster(monkeypatch):
    captured = {}

    class _FakeAIMNet2Adapter:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(rsi, "AIMNet2Adapter", _FakeAIMNet2Adapter)
    args = rsi.build_parser().parse_args(
        ["structure.cif", "--structure-id", "neutral", "--backend", "aimnet2", "--output", "out.json"]
    )
    rsi._adapter(args)
    assert captured["charge"] == 0.0
    assert captured["allow_periodic_cluster"] is False


def test_repair_cif_spacegroup_text_normalizes_common_p21_spelling():
    text = "_space_group_name_H-M_alt        'P 1 21 1'\n"

    assert "_space_group_name_H-M_alt        'P 21'" in repair_cif_spacegroup_text(text)


def test_repair_cif_spacegroup_text_is_whitespace_tolerant():
    # The previous literal-replace implementation only matched one exact spacing;
    # the consolidated regex normalizer handles single-space spellings and the
    # symmetry_ tag spelling too.
    single_space = "_symmetry_space_group_name_H-M 'P 1 21 1'\n"
    repaired = repair_cif_spacegroup_text(single_space)
    assert "'P 21'" in repaired
    assert "P 1 21 1" not in repaired
