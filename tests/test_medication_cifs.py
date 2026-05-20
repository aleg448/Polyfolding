from pathlib import Path

from crystalprobe.insight.medication_cifs import (
    extract_selected_blocks,
    medication_cif_ingestion_markdown,
    medication_cif_ingestion_report,
    medication_measurement_summary,
)


def _write_cif(path: Path) -> None:
    path.write_text(
        """
data_parent
_chemical_name_common 'parent target'
_chemical_formula_sum 'C1 H4'
_database_code_depnum_ccdc_archive 'CCDC 1'
_symmetry_space_group_name_H-M 'P 1'
_cell_length_a 4
_cell_length_b 4
_cell_length_c 4
_cell_angle_alpha 90
_cell_angle_beta 90
_cell_angle_gamma 90
_cell_formula_units_Z 1
loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
C1 C 0.0 0.0 0.0
H1 H 0.1 0.1 0.1
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_medication_cif_ingestion_indexes_selected_block(tmp_path):
    cif = tmp_path / "source.cif"
    _write_cif(cif)
    manifest = {
        "targets": [
            {
                "name": "fixture",
                "source_path": str(cif),
                "selected_blocks": [
                    {
                        "block_id": "parent",
                        "structure_id": "fixture_parent",
                        "target_role": "parent",
                        "promote_to_profile": True,
                    }
                ],
            }
        ]
    }

    report = medication_cif_ingestion_report(manifest)

    assert report["selected_block_count"] == 1
    assert report["targets"][0]["source_status"] == "coordinates_available_locally"
    assert report["targets"][0]["selected_blocks"][0]["ccdc_deposition"] == "CCDC 1"
    assert report["targets"][0]["selected_blocks"][0]["coordinate_status"] == "coordinate_bearing"
    assert "fixture_parent" in medication_cif_ingestion_markdown(report)


def test_extract_selected_blocks_writes_standalone_cif(tmp_path):
    cif = tmp_path / "source.cif"
    output = tmp_path / "out"
    _write_cif(cif)

    report = extract_selected_blocks(
        {
            "targets": [
                {
                    "name": "fixture",
                    "source_path": str(cif),
                    "selected_blocks": [{"block_id": "parent", "structure_id": "fixture_parent"}],
                }
            ]
        },
        output_dir=output,
    )

    assert report["rows"][0]["status"] == "extracted"
    assert report["rows"][0]["coordinate_status"] == "coordinate_bearing"
    assert (output / "fixture_parent.cif").is_file()


def test_medication_measurement_summary_detects_outputs(tmp_path):
    measurement_dir = tmp_path / "measurements"
    measurement_dir.mkdir()
    (measurement_dir / "fixture_parent_mace.json").write_text(
        '{"energy_ev": -1.0, "natoms": 2, "formula": "CH", '
        '"force_summary": {"max_force_ev_per_ang": 0.1}, '
        '"local_geometry": {"diagnostic_flags": ["ok"]}}',
        encoding="utf-8",
    )

    report = medication_measurement_summary(
        {
            "targets": [
                {
                    "name": "fixture",
                    "source_path": "fixture.cif",
                    "selected_blocks": [
                        {
                            "block_id": "parent",
                            "structure_id": "fixture_parent",
                            "target_role": "parent",
                            "promote_to_profile": True,
                        }
                    ],
                }
            ]
        },
        measurement_dir=measurement_dir,
    )

    assert report["measured_target_count"] == 1
    block = report["targets"][0]["blocks"][0]
    assert block["measurement_status"] == "measured_local_only"
    assert block["backend_measurements"][0]["status"] == "measured"


def test_medication_measurement_summary_records_backend_blockers(tmp_path):
    report = medication_measurement_summary(
        {
            "targets": [
                {
                    "name": "fixture",
                    "source_path": "fixture.cif",
                    "selected_blocks": [
                        {
                            "block_id": "parent",
                            "structure_id": "fixture_parent",
                            "target_role": "parent",
                            "promote_to_profile": True,
                        }
                    ],
                }
            ]
        },
        measurement_dir=tmp_path,
        backend_blockers={
            "blockers": [
                {
                    "structure_id": "fixture_parent",
                    "backend": "aimnet2",
                    "status": "pending_due_limit",
                    "reason": "limit",
                    "command": "run backend",
                }
            ]
        },
    )

    assert report["blocked_backend_count"] == 1
    aimnet2 = report["targets"][0]["blocks"][0]["backend_measurements"][1]
    assert aimnet2["status"] == "pending_due_limit"
    assert aimnet2["command"] == "run backend"
