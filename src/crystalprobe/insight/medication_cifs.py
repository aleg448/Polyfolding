"""Medication CIF ingestion and measurement summaries."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from crystalprobe.datahub.ccdc import find_ccdc_block, split_ccdc_cif, write_ccdc_block


def medication_cif_ingestion_report(selection_manifest: dict[str, Any]) -> dict[str, Any]:
    """Index selected local medication CIF bundles and their selected blocks."""

    targets = [_target_report(target) for target in selection_manifest.get("targets", [])]
    selected_blocks = sum(len(target["selected_blocks"]) for target in targets)
    parseable_blocks = sum(
        1
        for target in targets
        for block in target["selected_blocks"]
        if block["parse_status"] == "ase_parseable"
    )
    return {
        "schema_version": "0.1.0",
        "status": "medication_cif_ingestion_recorded",
        "target_count": len(targets),
        "selected_block_count": selected_blocks,
        "parseable_selected_block_count": parseable_blocks,
        "targets": targets,
        "policy": [
            selection_manifest.get(
                "license_policy",
                "Treat local medication CIF files as local-only unless redistribution is reviewed.",
            ),
            "Parent medication structures are prioritized over hydrates, co-crystals, solvates, and analogues.",
            "Parseability is an ingestion check, not a scientific validation or stability claim.",
        ],
    }


def medication_cif_ingestion_markdown(report: dict[str, Any]) -> str:
    """Render medication CIF ingestion as Markdown."""

    lines = [
        "# CrystalProbe Medication CIF Ingestion",
        "",
        f"- Status: `{report['status']}`",
        f"- Targets: `{report['target_count']}`",
        f"- Selected blocks: `{report['selected_block_count']}`",
        f"- Parseable selected blocks: `{report['parseable_selected_block_count']}`",
        "",
        "## Targets",
        "",
        "| Target | Source present | Blocks | Selected | Parseable selected |",
        "|---|---|---:|---:|---:|",
    ]
    for target in report["targets"]:
        lines.append(
            f"| {target['name']} | `{target['source_present']}` | {target['block_count']} | "
            f"{len(target['selected_blocks'])} | {target['parseable_selected_block_count']} |"
        )
    for target in report["targets"]:
        lines.extend(["", f"## {target['name']}", ""])
        lines.append(f"- Source path: `{target['source_path']}`")
        lines.append(f"- Source status: `{target['source_status']}`")
        lines.append("- Selected blocks:")
        lines.extend(
            "  - "
            f"`{block['block_id']}` -> `{block['structure_id']}`; "
            f"role `{block['target_role']}`; parse `{block['parse_status']}`; "
            f"formula `{block['formula']}`; CCDC `{block['ccdc_deposition'] or 'not recorded'}`."
            for block in target["selected_blocks"]
        )
        if target["missing_selected_blocks"]:
            lines.append("- Missing selected blocks:")
            lines.extend(f"  - `{block_id}`" for block_id in target["missing_selected_blocks"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def medication_measurement_summary(
    selection_manifest: dict[str, Any],
    *,
    measurement_dir: str | Path = "outputs/medication_measurements",
    backend_blockers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Summarize local backend measurements for selected medication CIF blocks."""

    root = Path(measurement_dir)
    blocker_lookup = _backend_blocker_lookup(backend_blockers or {})
    targets = []
    for target in selection_manifest.get("targets", []):
        blocks = []
        for selected in target.get("selected_blocks", []):
            backend_rows = []
            for backend in ("mace", "aimnet2", "uma"):
                path = root / f"{selected['structure_id']}_{backend}.json"
                backend_rows.append(_measurement_row(path, backend, blocker_lookup.get((selected["structure_id"], backend))))
            measured = [row for row in backend_rows if row["status"] == "measured"]
            blocks.append(
                {
                    "block_id": selected.get("block_id"),
                    "structure_id": selected.get("structure_id"),
                    "target_role": selected.get("target_role"),
                    "promote_to_profile": bool(selected.get("promote_to_profile")),
                    "backend_measurements": backend_rows,
                    "measured_backend_count": len(measured),
                    "measurement_status": "measured_local_only" if measured else "coordinates_available_locally",
                }
            )
        targets.append(
            {
                "name": target.get("name"),
                "source_path": target.get("source_path"),
                "blocks": blocks,
                "measured_block_count": sum(1 for block in blocks if block["measured_backend_count"] > 0),
            }
        )
    return {
        "schema_version": "0.1.0",
        "status": "medication_measurement_summary_recorded",
        "measurement_dir": str(root),
        "target_count": len(targets),
        "measured_target_count": sum(1 for target in targets if target["measured_block_count"] > 0),
        "blocked_backend_count": sum(
            1
            for target in targets
            for block in target["blocks"]
            for row in block["backend_measurements"]
            if row["status"].startswith("pending_")
        ),
        "targets": targets,
        "policy": [
            "Medication structure measurements are local-only unless source licenses are reviewed.",
            "Single-structure measurements support backend-behaviour profiling, not polymorph stability claims.",
            "Analogue measurements must not be promoted as parent medication proof.",
        ],
    }


def medication_measurement_markdown(report: dict[str, Any]) -> str:
    """Render medication measurement summary as Markdown."""

    lines = [
        "# CrystalProbe Medication Measurement Summary",
        "",
        f"- Status: `{report['status']}`",
        f"- Targets: `{report['target_count']}`",
        f"- Measured targets: `{report['measured_target_count']}`",
        f"- Pending/blocked backend runs: `{report.get('blocked_backend_count', 0)}`",
        "",
        "## Measurements",
        "",
        "| Target | Structure | Role | Status | Backends | Max force flags |",
        "|---|---|---|---|---|---|",
    ]
    for target in report["targets"]:
        for block in target["blocks"]:
            measured = [row["backend"] for row in block["backend_measurements"] if row["status"] == "measured"]
            flags = sorted(
                {
                    flag
                    for row in block["backend_measurements"]
                    for flag in row.get("diagnostic_flags", [])
                }
            )
            lines.append(
                f"| {target['name']} | `{block['structure_id']}` | `{block['target_role']}` | "
                f"`{block['measurement_status']}` | {', '.join(measured) or 'none'} | {', '.join(flags) or 'none'} |"
            )
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    blocked_rows = [
        (target["name"], block["structure_id"], row)
        for target in report["targets"]
        for block in target["blocks"]
        for row in block["backend_measurements"]
        if row["status"].startswith("pending_")
    ]
    if blocked_rows:
        lines.extend(["", "## Pending Backend Runs", ""])
        lines.extend(
            f"- {target} `{structure_id}` `{row['backend']}`: `{row['status']}` - {row.get('reason', '')}"
            for target, structure_id, row in blocked_rows
        )
        commands = [row.get("command") for _, _, row in blocked_rows if row.get("command")]
        if commands:
            lines.extend(["", "## Pending Backend Commands", ""])
            lines.extend(f"- `{command}`" for command in commands)
    return "\n".join(lines).rstrip() + "\n"


def extract_selected_blocks(
    selection_manifest: dict[str, Any],
    *,
    output_dir: str | Path = "outputs/_structure_inference_blocks",
) -> dict[str, Any]:
    """Extract selected blocks to standalone CIFs for measurement."""

    root = Path(output_dir)
    rows = []
    for target in selection_manifest.get("targets", []):
        source = Path(target["source_path"])
        for selected in target.get("selected_blocks", []):
            output = root / f"{selected['structure_id']}.cif"
            try:
                block = write_ccdc_block(source, output, block_id=selected["block_id"])
                rows.append(
                    {
                        "target": target["name"],
                        "block_id": block.block_id,
                        "structure_id": selected["structure_id"],
                        "output": str(output),
                        "status": "extracted",
                        "coordinate_status": _coordinate_status(block.text),
                    }
                )
            except Exception as exc:  # pragma: no cover - exercised by integration path.
                rows.append(
                    {
                        "target": target["name"],
                        "block_id": selected.get("block_id"),
                        "structure_id": selected.get("structure_id"),
                        "output": str(output),
                        "status": "failed",
                        "error": str(exc),
                    }
                )
    return {
        "schema_version": "0.1.0",
        "status": "selected_medication_blocks_extracted",
        "output_dir": str(root),
        "rows": rows,
    }


def _target_report(target: dict[str, Any]) -> dict[str, Any]:
    source = Path(target.get("source_path", ""))
    if not source.exists():
        return {
            "name": target.get("name"),
            "source_path": str(source),
            "source_present": False,
            "source_status": "missing",
            "block_count": 0,
            "selected_blocks": [],
            "missing_selected_blocks": [row.get("block_id") for row in target.get("selected_blocks", [])],
            "parseable_selected_block_count": 0,
        }

    blocks = split_ccdc_cif(source)
    selected_reports = []
    missing = []
    for selected in target.get("selected_blocks", []):
        try:
            block = find_ccdc_block(blocks, block_id=selected["block_id"])
        except Exception:
            missing.append(selected.get("block_id"))
            continue
        selected_reports.append(_selected_block_report(block, selected))
    return {
        "name": target.get("name"),
        "source_path": str(source),
        "source_present": True,
        "source_status": "coordinates_available_locally",
        "block_count": len(blocks),
        "block_ids": [block.block_id for block in blocks],
        "selected_blocks": selected_reports,
        "missing_selected_blocks": missing,
        "parseable_selected_block_count": sum(
            1 for block in selected_reports if block["parse_status"] == "ase_parseable"
        ),
    }


def _selected_block_report(block: Any, selected: dict[str, Any]) -> dict[str, Any]:
    parse_status, parse_error = _ase_parse_status(block.text)
    tags = block.tags
    return {
        "block_id": block.block_id,
        "structure_id": selected.get("structure_id"),
        "target_role": selected.get("target_role"),
        "promote_to_profile": bool(selected.get("promote_to_profile")),
        "expected_formula": selected.get("expected_formula"),
        "formula": tags.get("_chemical_formula_sum") or tags.get("_chemical_formula_moiety") or "unknown",
        "name": tags.get("_chemical_name_common") or tags.get("_chemical_name_systematic") or "unknown",
        "space_group": tags.get("_symmetry_space_group_name_H-M") or tags.get("_space_group_name_H-M_alt"),
        "z": tags.get("_cell_formula_units_Z"),
        "ccdc_deposition": selected.get("ccdc_deposition") or tags.get("_database_code_depnum_ccdc_archive"),
        "source_index": block.source_index,
        "coordinate_status": _coordinate_status(block.text),
        "parse_status": parse_status,
        "parse_error": parse_error,
    }


def _coordinate_status(text: str) -> str:
    if "_atom_site_fract_x" in text or "_atom_site_Cartn_x" in text:
        return "coordinate_bearing"
    if "No coordinates were deposited" in text:
        return "no_deposited_coordinates"
    return "no_atom_site_coordinates"


def _ase_parse_status(text: str) -> tuple[str, str | None]:
    try:
        from ase.io import read
    except Exception as exc:
        return "ase_unavailable", str(exc)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "block.cif"
        path.write_text(text, encoding="utf-8", newline="\n")
        try:
            read(str(path))
        except Exception as exc:
            return "ase_parse_failed", str(exc)
    return "ase_parseable", None


def _measurement_row(path: Path, backend: str, blocker: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        if blocker:
            return {
                "backend": backend,
                "status": blocker.get("status", "pending_blocked"),
                "path": str(path),
                "reason": blocker.get("reason"),
                "next_action": blocker.get("next_action"),
                "command": blocker.get("command"),
            }
        return {"backend": backend, "status": "missing", "path": str(path)}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"backend": backend, "status": "unreadable", "path": str(path), "error": str(exc)}
    geometry = data.get("local_geometry") or {}
    return {
        "backend": backend,
        "status": "measured",
        "path": str(path),
        "energy_ev": data.get("energy_ev"),
        "natoms": data.get("natoms"),
        "formula": data.get("formula"),
        "max_force_ev_per_ang": (data.get("force_summary") or {}).get("max_force_ev_per_ang"),
        "diagnostic_flags": list(geometry.get("diagnostic_flags", [])),
    }


def _backend_blocker_lookup(blockers: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    lookup = {}
    for blocker in blockers.get("blockers", []):
        structure_id = blocker.get("structure_id")
        backend = blocker.get("backend")
        if structure_id and backend:
            lookup[(structure_id, backend)] = blocker
    return lookup
