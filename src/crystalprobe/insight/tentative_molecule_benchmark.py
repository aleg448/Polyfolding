"""Tentative molecule-panel benchmark and bug-signature reporting."""

from __future__ import annotations

import csv
import importlib.util
import json
import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from crystalprobe.foundry.adapters import all_adapter_availability
from crystalprobe.insight.conformer_generation import conformer_generation_report


CLAIM_BOUNDARY = "tentative_software_benchmark_not_scientific_evidence"


@dataclass(frozen=True)
class MoleculeRecord:
    molecule_id: str
    common_name: str
    smiles: str
    source_set: str
    stress_tags: tuple[str, ...]
    expected_bug_surfaces: tuple[str, ...]
    claim_boundary: str = CLAIM_BOUNDARY

    def as_dict(self) -> dict[str, Any]:
        return {
            "molecule_id": self.molecule_id,
            "common_name": self.common_name,
            "smiles": self.smiles,
            "source_set": self.source_set,
            "stress_tags": list(self.stress_tags),
            "expected_bug_surfaces": list(self.expected_bug_surfaces),
            "claim_boundary": self.claim_boundary,
        }


BENCHMARK_ROW_COLUMNS = [
    "row_id",
    "molecule_id",
    "common_name",
    "tool",
    "tool_type",
    "status",
    "issue_signature",
    "detail",
    "claim_boundary",
    "metrics_json",
]

BUG_SIGNATURE_COLUMNS = [
    "issue_signature",
    "severity",
    "count",
    "example_ids",
    "detail",
]


def load_molecule_panel(*paths: str | Path) -> list[MoleculeRecord]:
    """Load one or more molecule-panel files.

    JSON files may use the molecule bug-hunt catalog shape. CSV files use the
    source-controlled larger-panel shape. Duplicate molecule IDs are ignored
    after the first occurrence so stress fixtures remain stable.
    """

    records: list[MoleculeRecord] = []
    seen: set[str] = set()
    for path_like in paths:
        path = Path(path_like)
        for record in _load_panel_path(path):
            if record.molecule_id not in seen:
                seen.add(record.molecule_id)
                records.append(record)
    return records


def build_tentative_molecule_benchmark(records: Iterable[MoleculeRecord]) -> dict[str, Any]:
    """Run dependency-light molecule checks and optional backend preflights."""

    molecules = list(records)
    rows: list[dict[str, Any]] = []
    for molecule in molecules:
        rows.append(_lexical_row(molecule))
    rows.extend(_rdkit_rows(molecules))
    conformers = conformer_generation_report(molecules)
    rows.extend(_conformer_benchmark_rows(conformers))
    rows.extend(_backend_preflight_rows(conformers["counts"]["generated_count"]))

    signatures = _bug_signatures(rows)
    status = "tentative_molecule_benchmark_recorded"
    if any(row["status"] == "failed" for row in rows):
        status = "tentative_molecule_benchmark_found_issues"

    counts = Counter(row["status"] for row in rows)
    tool_counts = Counter(row["tool"] for row in rows)
    molecule_counts = Counter(row.source_set for row in molecules)
    return {
        "schema_version": "0.1.0",
        "status": status,
        "purpose": (
            "Tentative software benchmark for molecule ingestion, SMILES featurization, optional dependency "
            "visibility, and structured bug-signature discovery."
        ),
        "claim_boundary": CLAIM_BOUNDARY,
        "candidate_payload_enabled": True,
        "counts": {
            "molecule_count": len(molecules),
            "tool_row_count": len(rows),
            "passed_count": counts.get("passed", 0),
            "failed_count": counts.get("failed", 0),
            "blocked_count": counts.get("blocked", 0),
            "skipped_count": counts.get("skipped", 0),
            "warning_count": counts.get("warning", 0),
            "claim_ready_count": 0,
            "bug_signature_count": len(signatures),
        },
        "source_sets": dict(sorted(molecule_counts.items())),
        "tool_counts": dict(sorted(tool_counts.items())),
        "conformer_generation": {
            "status": conformers["status"],
            "generated_count": conformers["counts"]["generated_count"],
            "blocked_count": conformers["counts"]["blocked_count"],
            "failed_count": conformers["counts"]["failed_count"],
            "coordinate_payload_enabled": conformers["coordinate_payload_enabled"],
        },
        "molecules": [molecule.as_dict() for molecule in molecules],
        "benchmark_rows": rows,
        "bug_signatures": signatures,
        "policy": [
            "This is a tentative software benchmark, not a scientific validation benchmark.",
            "Rows may show parser, dependency, or input-readiness failures; those are bug-hunt signals.",
            "RDKit conformer generation is used when available, but generated conformers are software inputs, not experimental structures.",
            "Optional scientific backends are preflighted, but conformer-ready rows do not prove MLIP execution.",
            "No molecule-panel row can support stability, formulation, or drug-discovery claims.",
            "A verified calibration slice is still required before headline benchmark claims.",
        ],
    }


def tentative_molecule_benchmark_markdown(report: dict[str, Any]) -> str:
    """Render the tentative molecule benchmark report."""

    lines = [
        "# CrystalProbe Tentative Molecule Benchmark",
        "",
        f"- Status: `{report['status']}`",
        f"- Molecules: `{report['counts']['molecule_count']}`",
        f"- Tool rows: `{report['counts']['tool_row_count']}`",
        f"- Passed rows: `{report['counts']['passed_count']}`",
        f"- Failed rows: `{report['counts']['failed_count']}`",
        f"- Blocked rows: `{report['counts']['blocked_count']}`",
        f"- Warning rows: `{report['counts']['warning_count']}`",
        f"- Claim-ready rows: `{report['counts']['claim_ready_count']}`",
        f"- Generated conformers: `{report['conformer_generation']['generated_count']}`",
        f"- Candidate payload enabled: `{report['candidate_payload_enabled']}`",
        f"- Claim boundary: `{report['claim_boundary']}`",
        "",
        "## Source Sets",
        "",
        "| Source set | Molecules |",
        "|---|---:|",
    ]
    for source_set, count in sorted(report["source_sets"].items()):
        lines.append(f"| `{source_set}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Tool Summary",
            "",
            "| Tool | Rows |",
            "|---|---:|",
        ]
    )
    for tool, count in sorted(report["tool_counts"].items()):
        lines.append(f"| `{tool}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Bug Signatures",
            "",
            "| Signature | Severity | Count | Examples | Detail |",
            "|---|---|---:|---|---|",
        ]
    )
    for signature in report["bug_signatures"]:
        examples = ", ".join(signature["example_ids"])
        lines.append(
            f"| `{signature['issue_signature']}` | `{signature['severity']}` | "
            f"`{signature['count']}` | {examples} | {signature['detail']} |"
        )

    lines.extend(
        [
            "",
            "## Sample Benchmark Rows",
            "",
            "| Molecule | Tool | Status | Signature | Detail |",
            "|---|---|---|---|---|",
        ]
    )
    for row in report["benchmark_rows"][:30]:
        lines.append(
            f"| `{row['molecule_id']}` | `{row['tool']}` | `{row['status']}` | "
            f"`{row['issue_signature']}` | {row['detail']} |"
        )

    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {line}" for line in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def write_tentative_molecule_benchmark_sqlite(report: dict[str, Any], path: str | Path) -> None:
    """Write benchmark rows and bug signatures to SQLite."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    with sqlite3.connect(output) as connection:
        row_columns = ", ".join(f"{column} TEXT" for column in BENCHMARK_ROW_COLUMNS)
        sig_columns = ", ".join(f"{column} TEXT" for column in BUG_SIGNATURE_COLUMNS)
        connection.execute(f"CREATE TABLE molecule_benchmark_rows ({row_columns})")
        connection.execute(f"CREATE TABLE bug_signatures ({sig_columns})")
        row_placeholders = ", ".join("?" for _ in BENCHMARK_ROW_COLUMNS)
        sig_placeholders = ", ".join("?" for _ in BUG_SIGNATURE_COLUMNS)
        connection.executemany(
            f"INSERT INTO molecule_benchmark_rows ({', '.join(BENCHMARK_ROW_COLUMNS)}) VALUES ({row_placeholders})",
            [_sqlite_row(row, BENCHMARK_ROW_COLUMNS) for row in report["benchmark_rows"]],
        )
        connection.executemany(
            f"INSERT INTO bug_signatures ({', '.join(BUG_SIGNATURE_COLUMNS)}) VALUES ({sig_placeholders})",
            [_sqlite_row(row, BUG_SIGNATURE_COLUMNS) for row in report["bug_signatures"]],
        )
        connection.execute("CREATE INDEX idx_molecule_benchmark_tool ON molecule_benchmark_rows(tool)")
        connection.execute("CREATE INDEX idx_molecule_benchmark_status ON molecule_benchmark_rows(status)")
        connection.execute("CREATE INDEX idx_bug_signature ON bug_signatures(issue_signature)")


def _load_panel_path(path: Path) -> list[MoleculeRecord]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return _load_json_panel(path)
    if suffix == ".csv":
        return _load_csv_panel(path)
    raise ValueError(f"Unsupported molecule panel file type: {path}")


def _load_json_panel(path: Path) -> list[MoleculeRecord]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [
        MoleculeRecord(
            molecule_id=str(row["molecule_id"]),
            common_name=str(row["common_name"]),
            smiles=str(row["smiles"]),
            source_set=path.stem,
            stress_tags=tuple(str(tag) for tag in row.get("stress_tags", [])),
            expected_bug_surfaces=tuple(str(surface) for surface in row.get("expected_bug_surfaces", [])),
            claim_boundary="software_stress_fixture_not_scientific_evidence",
        )
        for row in payload.get("molecules", [])
    ]


def _load_csv_panel(path: Path) -> list[MoleculeRecord]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            MoleculeRecord(
                molecule_id=str(row["molecule_id"]),
                common_name=str(row["common_name"]),
                smiles=str(row["smiles"]),
                source_set=str(row.get("source_set") or path.stem),
                stress_tags=_split_list(row.get("stress_tags", "")),
                expected_bug_surfaces=_split_list(row.get("expected_bug_surfaces", "")),
                claim_boundary=str(row.get("claim_boundary") or CLAIM_BOUNDARY),
            )
            for row in reader
        ]


def _lexical_row(molecule: MoleculeRecord) -> dict[str, Any]:
    smiles = molecule.smiles
    issues = []
    if not smiles.strip():
        issues.append("empty_smiles")
    if smiles.count("(") != smiles.count(")"):
        issues.append("unbalanced_parentheses")
    if smiles.count("[") != smiles.count("]"):
        issues.append("unbalanced_brackets")
    ring_digits = _ring_digits_outside_brackets(smiles)
    odd_ring_digits = sorted({digit for digit in ring_digits if ring_digits.count(digit) % 2})
    if odd_ring_digits:
        issues.append("unpaired_ring_digit")
    status = "failed" if issues else "passed"
    detail = "Lexical SMILES checks passed." if not issues else "; ".join(issues)
    return _row(
        molecule=molecule,
        tool="smiles_lexical",
        tool_type="featurizer",
        status=status,
        issue_signature="none" if not issues else "smiles_lexical_failure",
        detail=detail,
        metrics={
            "smiles_length": len(smiles),
            "component_count": smiles.count(".") + 1,
            "bracket_count": smiles.count("["),
            "ring_digit_count": len(ring_digits),
            "has_stereochemistry": "@" in smiles or "/" in smiles or "\\" in smiles,
        },
    )


def _rdkit_rows(molecules: list[MoleculeRecord]) -> list[dict[str, Any]]:
    if importlib.util.find_spec("rdkit") is None:
        return [
            _tool_blocker_row(
                tool="rdkit_smiles",
                tool_type="featurizer",
                issue_signature="optional_featurizer_missing_dependency",
                detail="RDKit is not importable in the active Python environment.",
            )
        ]

    from rdkit import Chem
    from rdkit.Chem import Descriptors

    rows = []
    for molecule in molecules:
        try:
            mol = Chem.MolFromSmiles(molecule.smiles)
            if mol is None:
                rows.append(
                    _row(
                        molecule=molecule,
                        tool="rdkit_smiles",
                        tool_type="featurizer",
                        status="failed",
                        issue_signature="rdkit_parse_failure",
                        detail="RDKit returned no molecule for the SMILES string.",
                        metrics={},
                    )
                )
                continue
            rows.append(
                _row(
                    molecule=molecule,
                    tool="rdkit_smiles",
                    tool_type="featurizer",
                    status="passed",
                    issue_signature="none",
                    detail="RDKit parsed the SMILES string.",
                    metrics={
                        "heavy_atom_count": int(mol.GetNumHeavyAtoms()),
                        "formal_charge": int(Chem.GetFormalCharge(mol)),
                        "ring_count": int(mol.GetRingInfo().NumRings()),
                        "molecular_weight": float(Descriptors.MolWt(mol)),
                    },
                )
            )
        except Exception as exc:  # pragma: no cover - defensive for optional dependency internals
            rows.append(
                _row(
                    molecule=molecule,
                    tool="rdkit_smiles",
                    tool_type="featurizer",
                    status="failed",
                    issue_signature="rdkit_exception",
                    detail=f"{type(exc).__name__}: {exc}",
                    metrics={},
                )
            )
    return rows


def _backend_preflight_rows(conformer_ready_count: int) -> list[dict[str, Any]]:
    rows = []
    for availability in all_adapter_availability():
        if availability.name == "ase_cif":
            tool_type = "structure_parser"
        else:
            tool_type = "scientific_backend"
        if availability.available and conformer_ready_count > 0:
            rows.append(
                _tool_blocker_row(
                    tool=availability.name,
                    tool_type=tool_type,
                    issue_signature="backend_execution_not_requested",
                    detail=(
                        f"{availability.name} is importable and {conformer_ready_count} generated conformer inputs "
                        "are available; backend execution is intentionally not run by this tentative benchmark."
                    ),
                    status="skipped",
                )
            )
        elif availability.available:
            rows.append(
                _tool_blocker_row(
                    tool=availability.name,
                    tool_type=tool_type,
                    issue_signature="backend_blocked_no_generated_conformers",
                    detail=(
                        f"{availability.name} is importable, but no generated conformers are available for backend "
                        "execution in this environment."
                    ),
                    status="blocked",
                )
            )
        else:
            rows.append(
                _tool_blocker_row(
                    tool=availability.name,
                    tool_type=tool_type,
                    issue_signature="optional_backend_missing_dependency",
                    detail=availability.blocker or f"{availability.name} is unavailable.",
                    status="blocked",
                )
            )
    return rows


def _conformer_benchmark_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in report["rows"]:
        status = "passed" if row["status"] == "generated" else row["status"]
        rows.append(
            {
                "row_id": f"rdkit_conformer:{row['molecule_id']}",
                "molecule_id": row["molecule_id"],
                "common_name": row["common_name"],
                "tool": "rdkit_conformer",
                "tool_type": "conformer_generator",
                "status": status,
                "issue_signature": row["issue_signature"],
                "detail": row["detail"],
                "claim_boundary": row["claim_boundary"],
                "metrics": {
                    "atom_count": row["atom_count"],
                    "heavy_atom_count": row["heavy_atom_count"],
                    "coordinate_payload": row["coordinate_payload"],
                },
                "metrics_json": json.dumps(
                    {
                        "atom_count": row["atom_count"],
                        "heavy_atom_count": row["heavy_atom_count"],
                        "coordinate_payload": row["coordinate_payload"],
                    },
                    sort_keys=True,
                ),
            }
        )
    return rows


def _bug_signatures(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        signature = row["issue_signature"]
        if signature == "none":
            continue
        grouped.setdefault(signature, []).append(row)
    signatures = []
    for signature, group in sorted(grouped.items()):
        statuses = {row["status"] for row in group}
        severity = "info"
        if "failed" in statuses:
            severity = "failure"
        elif "warning" in statuses:
            severity = "warning"
        elif "blocked" in statuses:
            severity = "blocked"
        elif "skipped" in statuses:
            severity = "skipped"
        example_ids = [row["molecule_id"] or row["tool"] for row in group[:5]]
        signatures.append(
            {
                "issue_signature": signature,
                "severity": severity,
                "count": len(group),
                "example_ids": example_ids,
                "detail": group[0]["detail"],
            }
        )
    return signatures


def _row(
    *,
    molecule: MoleculeRecord,
    tool: str,
    tool_type: str,
    status: str,
    issue_signature: str,
    detail: str,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "row_id": f"{tool}:{molecule.molecule_id}",
        "molecule_id": molecule.molecule_id,
        "common_name": molecule.common_name,
        "tool": tool,
        "tool_type": tool_type,
        "status": status,
        "issue_signature": issue_signature,
        "detail": detail,
        "claim_boundary": molecule.claim_boundary,
        "metrics": metrics,
        "metrics_json": json.dumps(metrics, sort_keys=True),
    }


def _tool_blocker_row(
    *,
    tool: str,
    tool_type: str,
    issue_signature: str,
    detail: str,
    status: str = "blocked",
) -> dict[str, Any]:
    return {
        "row_id": f"{tool}:preflight",
        "molecule_id": "",
        "common_name": "",
        "tool": tool,
        "tool_type": tool_type,
        "status": status,
        "issue_signature": issue_signature,
        "detail": detail,
        "claim_boundary": CLAIM_BOUNDARY,
        "metrics": {},
        "metrics_json": "{}",
    }


def _split_list(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(";") if part.strip())


def _ring_digits_outside_brackets(smiles: str) -> list[str]:
    digits: list[str] = []
    bracket_depth = 0
    for character in smiles:
        if character == "[":
            bracket_depth += 1
            continue
        if character == "]":
            bracket_depth = max(0, bracket_depth - 1)
            continue
        if bracket_depth == 0 and character.isdigit():
            digits.append(character)
    return digits


def _sqlite_row(row: dict[str, Any], columns: list[str]) -> tuple[str, ...]:
    values = []
    for column in columns:
        value = row[column]
        if isinstance(value, (dict, list)):
            values.append(json.dumps(value, sort_keys=True))
        else:
            values.append(str(value))
    return tuple(values)
