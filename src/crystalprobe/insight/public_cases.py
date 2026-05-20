"""Public checklist and unverified candidate case rendering."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from crystalprobe.core.io import atomic_write_text
from crystalprobe.insight.figures import candidate_backend_summary_svg, write_svg


DEFAULT_CHECKLIST_PATH = Path("docs/public_demo_checklist.md")
DEFAULT_PUBLIC_CASE_PATH = Path("data/public_cases/cposs_ibp_candidate_v0.1.json")
DEFAULT_CASE_DOC_PATH = Path("docs/cases/cposs_ibp_candidate.md")
DEFAULT_CASE_ASSET_DIR = Path("docs/assets/public_cases")


def write_public_demo_checklist(
    report: dict[str, Any],
    *,
    output_path: str | Path = DEFAULT_CHECKLIST_PATH,
) -> Path:
    """Write a reviewer-oriented public demo checklist."""

    path = Path(output_path)
    atomic_write_text(path, public_demo_checklist_markdown(report))
    return path


def public_demo_checklist_markdown(report: dict[str, Any]) -> str:
    backend_rows = report.get("optional_scientific_backends", [])
    lines = [
        "# CrystalProbe Public Demo Checklist",
        "",
        "Use this checklist to evaluate the public artifact without granting it stronger scientific claims than it currently earns.",
        "",
        "## Run",
        "",
        "```powershell",
        "python scripts\\build_public_artifact.py",
        "python scripts\\check_public_artifact.py",
        "```",
        "",
        "Expected runtime: under five minutes on the dependency-light path.",
        "",
        "## Required Dependencies",
        "",
        "- Python 3.11+",
        "- Core package dependencies from `pyproject.toml`",
        "- No MACE, AIMNet2, UMA, fairchem, ASE, Docker, CCDC, or CSD dependency is required for the public demo path.",
        "",
        "## Optional Scientific Backends",
        "",
        "| Backend | Importable | Smoke status | Public-demo role |",
        "|---|---:|---|---|",
    ]
    role_by_name = {
        "ase_cif": "CIF parsing support",
        "mace_off": "optional MLIP inference smoke",
        "aimnet2": "optional MLIP inference smoke",
        "uma": "optional fairchem/UMA path",
        "fastcsp": "future CSP complement",
    }
    for row in backend_rows:
        name = str(row.get("name", "unknown"))
        lines.append(
            f"| `{name}` | `{row.get('available')}` | `{row.get('smoke_status')}` | {role_by_name.get(name, 'optional backend')} |"
        )
    lines.extend(
        [
            "",
            "## Expected Outputs",
            "",
            "- `docs/public_demo.md` embeds reviewer-visible SVGs.",
            "- `docs/assets/public_demo/*.svg` contains stable copied demo figures.",
            "- `docs/public_demo_checklist.md` records this checklist.",
            "- `docs/cases/cposs_ibp_candidate.md` records one stronger unverified example.",
            "- `outputs/public_demo/*` contains regenerated local reports and ledgers, but remains ignored.",
            "- `outputs/public_artifact_integrity.*` records the public artifact integrity check, but remains ignored.",
            "",
            "## Claim Checks",
            "",
            f"- Claim gate decision: `{report['claim_gate']['decision']}`",
            f"- Seed pairs: `{report['dataset']['pairs']}`",
            f"- Evaluated ranking pairs: `{report['quick_benchmark']['evaluated']}`",
            f"- Skipped ranking pairs: `{report['quick_benchmark']['skipped']}`",
            "- Headline benchmark claims are blocked unless records are verified.",
            "- Candidate figures must show `draft/unverified`, `candidate/unverified`, or equivalent labels.",
            "- Optional backend availability is execution evidence only, not scientific validity evidence.",
            "",
            "## Manual Review Before Public Sharing",
            "",
            "- Confirm no raw CCDC/CSD-derived coordinate files are copied into `docs/`.",
            "- Confirm every public case declares source-license, stability-evidence, disorder, curator, and reviewer blockers.",
            "- Confirm no cross-backend absolute energy comparison is presented as calibrated thermodynamics.",
            "- Confirm the public story remains reliability infrastructure, not a finished drug-discovery engine.",
            "",
            "## Automated Integrity Gate",
            "",
            "`python scripts\\check_public_artifact.py` verifies required public paths, visible unverified labels, public release-boundary classification, and absence of coordinate-style files under the public asset directories. The command exits nonzero if any check is blocked.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_public_candidate_case(
    *,
    case_path: str | Path = DEFAULT_PUBLIC_CASE_PATH,
    output_path: str | Path = DEFAULT_CASE_DOC_PATH,
    asset_dir: str | Path = DEFAULT_CASE_ASSET_DIR,
) -> dict[str, str]:
    """Write a public unverified candidate case study and copied SVG asset."""

    case = json.loads(Path(case_path).read_text(encoding="utf-8"))
    docs_path = Path(output_path)
    assets = Path(asset_dir)
    assets.mkdir(parents=True, exist_ok=True)
    figure_path = assets / f"{case['candidate_id']}_backend_summary.svg"
    write_svg(figure_path, candidate_backend_summary_svg(case))
    atomic_write_text(docs_path, public_candidate_case_markdown(case, figure_path=figure_path, output_path=docs_path))
    return {"case_doc": str(docs_path), "backend_summary": str(figure_path)}


def public_candidate_case_markdown(case: dict[str, Any], *, figure_path: Path, output_path: Path) -> str:
    figure_link = _markdown_asset_path(figure_path, output_path=output_path)
    lines = [
        f"# Public Candidate Case: {case['candidate_id']}",
        "",
        f"Status: `{case['status']}`",
        f"Evidence tier: `{case['evidence_tier']}`",
        f"Family: `{case['family']}`",
        f"Common name: `{case['common_name']}`",
        "",
        "This is a stronger unverified example for CrystalProbe's public artifact. It includes source context, model-output summaries, and explicit blockers, but it is not a verified benchmark record.",
        "",
        "## Visual Summary",
        "",
        f"![Backend summary]({figure_link})",
        "",
        "## Source Context",
        "",
    ]
    for item in case.get("source_context", []):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Why This Case",
            "",
        ]
    )
    for item in case.get("why_this_case", []):
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Model Output Summary",
            "",
            "| Backend | Lower structure | Higher structure | Gap (kJ/mol/f.u.) | Diagnostic flags |",
            "|---|---|---|---:|---|",
        ]
    )
    for row in case.get("model_outputs", []):
        flags = ", ".join(row.get("diagnostic_flags", [])) or "none"
        lines.append(
            f"| `{row['backend']}` | `{row['lower_structure']}` | `{row['higher_structure']}` | "
            f"{float(row['gap_kj_mol_per_formula_unit']):.3f} | {flags} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
        ]
    )
    for item in case.get("claim_boundary", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Promotion Blockers", ""])
    for blocker in case.get("promotion_blockers", []):
        lines.append(f"- {blocker}")
    lines.extend(["", "## Next Actions", ""])
    for action in case.get("next_actions", []):
        lines.append(f"- {action}")
    lines.extend(
        [
            "",
            "## Public Sharing Notes",
            "",
            "- This page is metadata and model-output summary only.",
            "- Do not copy raw CPOSS, CCDC, or CSD coordinate-bearing files into this public artifact.",
            "- Keep this case below verified benchmark status until all promotion blockers are resolved.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _markdown_asset_path(path: Path, *, output_path: Path) -> str:
    try:
        return path.relative_to(output_path.parent).as_posix()
    except ValueError:
        return f"../assets/public_cases/{path.name}"
