"""Build the public CrystalProbe artifact gallery."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from crystalprobe.core.io import atomic_write_text
from crystalprobe.insight.public_cases import (
    DEFAULT_CASE_ASSET_DIR,
    DEFAULT_CASE_DOC_PATH,
    DEFAULT_CHECKLIST_PATH,
    DEFAULT_PUBLIC_CASE_PATH,
    build_public_candidate_case,
    write_public_demo_checklist,
)
from crystalprobe.insight.public_demo import (
    BackendSmokeMode,
    DEFAULT_MANIFEST,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PREDICTIONS,
    run_public_demo,
)


DEFAULT_GALLERY_PATH = Path("docs/public_demo.md")
DEFAULT_ASSET_DIR = Path("docs/assets/public_demo")

FIGURE_ORDER = [
    ("claim_gate", "Claim Gate"),
    ("pipeline", "Reliability Pipeline"),
    ("backend_readiness", "Backend Readiness"),
    ("provenance_ledger", "Provenance Ledger"),
    ("calibration_reliability", "Calibration Reliability"),
    ("energy_uncertainty", "Energy Gap And Uncertainty"),
]


def build_public_artifact(
    *,
    manifest: str | Path = DEFAULT_MANIFEST,
    predictions: str | Path = DEFAULT_PREDICTIONS,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    gallery_path: str | Path = DEFAULT_GALLERY_PATH,
    asset_dir: str | Path = DEFAULT_ASSET_DIR,
    checklist_path: str | Path = DEFAULT_CHECKLIST_PATH,
    public_case_path: str | Path = DEFAULT_PUBLIC_CASE_PATH,
    case_output_path: str | Path = DEFAULT_CASE_DOC_PATH,
    case_asset_dir: str | Path = DEFAULT_CASE_ASSET_DIR,
    backend_smoke: BackendSmokeMode = "auto",
    backend_timeout_seconds: int = 90,
) -> dict[str, Any]:
    """Regenerate the demo, copy stable SVG assets, and write the gallery."""

    report = run_public_demo(
        manifest=manifest,
        predictions=predictions,
        output_dir=output_dir,
        backend_smoke=backend_smoke,
        backend_timeout_seconds=backend_timeout_seconds,
    )
    gallery = Path(gallery_path)
    assets = Path(asset_dir)
    assets.mkdir(parents=True, exist_ok=True)

    copied_figures: dict[str, str] = {}
    for key, _title in FIGURE_ORDER:
        source = Path(report["outputs"]["figures"][key])
        target = assets / source.name
        shutil.copyfile(source, target)
        copied_figures[key] = str(target)

    atomic_write_text(gallery, public_demo_gallery_markdown(report, copied_figures, gallery_path=gallery))
    checklist = write_public_demo_checklist(report, output_path=checklist_path)
    case_result = build_public_candidate_case(
        case_path=public_case_path,
        output_path=case_output_path,
        asset_dir=case_asset_dir,
    )
    return {
        "gallery": str(gallery),
        "assets": copied_figures,
        "checklist": str(checklist),
        "candidate_case": case_result,
        "demo_report": report["outputs"]["report_markdown"],
        "demo_output_dir": str(output_dir),
    }


def public_demo_gallery_markdown(
    report: dict[str, Any],
    copied_figures: dict[str, str],
    *,
    gallery_path: Path,
) -> str:
    """Render a GitHub-visible public demo gallery."""

    lines = [
        "# CrystalProbe Public Demo Gallery",
        "",
        "This gallery is the reviewer-facing view of the public demo. The SVGs are copied from the generated demo output into `docs/assets/public_demo/` so they remain visible even though `outputs/` is ignored.",
        "",
        "## Rebuild",
        "",
        "```powershell",
        "python scripts\\build_public_artifact.py",
        "python scripts\\check_public_artifact.py",
        "```",
        "",
        f"- Demo command: `{report['demo_command']}`",
        f"- Claim gate: `{report['claim_gate']['decision']}`",
        f"- Pairs: `{report['dataset']['pairs']}`",
        f"- Evaluated: `{report['quick_benchmark']['evaluated']}`",
        f"- Skipped: `{report['quick_benchmark']['skipped']}`",
        "- Checklist: [`docs/public_demo_checklist.md`](public_demo_checklist.md)",
        "- Stronger unverified case: [`docs/cases/cposs_ibp_candidate.md`](cases/cposs_ibp_candidate.md)",
        "",
        "## Visual Summary",
        "",
    ]
    for key, title in FIGURE_ORDER:
        path = _markdown_asset_path(copied_figures[key], gallery_path=gallery_path)
        lines.extend([f"### {title}", "", f"![{title}]({path})", ""])

    lines.extend(
        [
            "## Interpretation",
            "",
            "- The claim gate blocks headline benchmark claims because the public seed records are draft/candidate evidence.",
            "- The calibration figure intentionally shows an empty verified-points state instead of inventing reliability evidence.",
            "- The energy/uncertainty figure labels current points as `draft/unverified`, so candidate data stays visibly separate from benchmark truth.",
            "- Optional backend status is execution evidence only; installed scientific stacks are useful but not required for the public demo to complete.",
            "",
            "## Generated Reports",
            "",
            f"- Public demo report: `{report['outputs']['report_markdown']}`",
            f"- Fingerprint report: `{report['outputs']['fingerprint_report_markdown']}`",
            f"- Calibration JSON: `{report['outputs']['calibration_report_json']}`",
            f"- Ledger: `{report['outputs']['ledger']}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _markdown_asset_path(path: str, *, gallery_path: Path) -> str:
    target = Path(path)
    try:
        relative = target.relative_to(gallery_path.parent)
    except ValueError:
        relative = Path("assets/public_demo") / target.name
    return relative.as_posix()
