"""Integrity checks for the public CrystalProbe artifact surface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from crystalprobe.insight.release import release_boundary_report


PUBLIC_DEMO_ASSETS = [
    "docs/assets/public_demo/claim_gate.svg",
    "docs/assets/public_demo/pipeline.svg",
    "docs/assets/public_demo/backend_readiness.svg",
    "docs/assets/public_demo/provenance_ledger.svg",
    "docs/assets/public_demo/calibration_reliability.svg",
    "docs/assets/public_demo/energy_uncertainty.svg",
]
PUBLIC_CASE_ASSETS = [
    "docs/assets/public_cases/ibp_ibp01_psicrys_vs_ibp06_psicrys_backend_summary.svg",
]
PUBLIC_DOCS = [
    "docs/public_demo.md",
    "docs/public_demo_checklist.md",
    "docs/cases/cposs_ibp_candidate.md",
]
PUBLIC_DATA = [
    "data/public_cases/cposs_ibp_candidate_v0.1.json",
]
PUBLIC_ARTIFACT_PATHS = PUBLIC_DOCS + PUBLIC_DEMO_ASSETS + PUBLIC_CASE_ASSETS + PUBLIC_DATA
FORBIDDEN_PUBLIC_SUFFIXES = {".cif", ".pdb", ".mol2", ".sdf", ".xyz"}


def public_artifact_integrity_report(*, root: str | Path = ".") -> dict[str, Any]:
    """Check the public artifact surface for drift and claim-boundary safety."""

    root_path = Path(root)
    checks = [
        _required_paths_check(root_path),
        _public_suffix_check(root_path),
        _gallery_link_check(root_path),
        _unverified_label_check(root_path),
        _case_claim_boundary_check(root_path),
        _release_boundary_check(),
    ]
    blocked = [check for check in checks if check["status"] != "passed"]
    return {
        "schema_version": "0.1.0",
        "status": "public_artifact_integrity_passed" if not blocked else "public_artifact_integrity_blocked",
        "blocked_check_count": len(blocked),
        "public_paths": PUBLIC_ARTIFACT_PATHS,
        "checks": checks,
        "policy": [
            "Public demo artifacts must be visible from docs/ because outputs/ is intentionally ignored.",
            "Candidate examples must carry explicit unverified labels and promotion blockers.",
            "No raw or coordinate-bearing crystallographic source files should be copied into the public docs/assets surface.",
            "Public case metadata must stay inside candidate-public release-boundary classification.",
        ],
    }


def public_artifact_integrity_markdown(report: dict[str, Any]) -> str:
    """Render the public artifact integrity report as Markdown."""

    lines = [
        "# CrystalProbe Public Artifact Integrity",
        "",
        f"- Status: `{report['status']}`",
        f"- Blocked checks: `{report['blocked_check_count']}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for check in report["checks"]:
        lines.append(f"| `{check['check']}` | `{check['status']}` | {check['detail']} |")
    lines.extend(["", "## Public Paths", ""])
    lines.extend(f"- `{path}`" for path in report["public_paths"])
    lines.extend(["", "## Policy", ""])
    lines.extend(f"- {item}" for item in report["policy"])
    return "\n".join(lines).rstrip() + "\n"


def _required_paths_check(root: Path) -> dict[str, str]:
    missing = [path for path in PUBLIC_ARTIFACT_PATHS if not (root / path).exists()]
    return {
        "check": "required_public_paths",
        "status": "blocked" if missing else "passed",
        "detail": "missing: " + ", ".join(missing) if missing else f"{len(PUBLIC_ARTIFACT_PATHS)} required paths present",
    }


def _public_suffix_check(root: Path) -> dict[str, str]:
    scanned_roots = [root / "docs" / "assets" / "public_demo", root / "docs" / "assets" / "public_cases"]
    forbidden = []
    for scanned_root in scanned_roots:
        if not scanned_root.exists():
            continue
        for path in scanned_root.rglob("*"):
            if path.is_file() and path.suffix.lower() in FORBIDDEN_PUBLIC_SUFFIXES:
                forbidden.append(path.relative_to(root).as_posix())
    return {
        "check": "no_coordinate_bearing_public_assets",
        "status": "blocked" if forbidden else "passed",
        "detail": "forbidden files: " + ", ".join(forbidden) if forbidden else "no coordinate-style files in public asset dirs",
    }


def _gallery_link_check(root: Path) -> dict[str, str]:
    gallery_path = root / "docs" / "public_demo.md"
    if not gallery_path.exists():
        return {"check": "public_gallery_links", "status": "blocked", "detail": "docs/public_demo.md missing"}
    text = gallery_path.read_text(encoding="utf-8")
    expected = [
        "assets/public_demo/claim_gate.svg",
        "assets/public_demo/pipeline.svg",
        "assets/public_demo/backend_readiness.svg",
        "assets/public_demo/provenance_ledger.svg",
        "assets/public_demo/calibration_reliability.svg",
        "assets/public_demo/energy_uncertainty.svg",
        "public_demo_checklist.md",
        "cases/cposs_ibp_candidate.md",
    ]
    missing = [item for item in expected if item not in text]
    return {
        "check": "public_gallery_links",
        "status": "blocked" if missing else "passed",
        "detail": "missing links: " + ", ".join(missing) if missing else "gallery links required docs and figures",
    }


def _unverified_label_check(root: Path) -> dict[str, str]:
    required = {
        "docs/assets/public_demo/energy_uncertainty.svg": "draft/unverified",
        "docs/cases/cposs_ibp_candidate.md": "candidate_unverified",
        "docs/assets/public_cases/ibp_ibp01_psicrys_vs_ibp06_psicrys_backend_summary.svg": "candidate/unverified",
    }
    missing = []
    for path, marker in required.items():
        file_path = root / path
        if not file_path.exists() or marker not in file_path.read_text(encoding="utf-8"):
            missing.append(f"{path}:{marker}")
    return {
        "check": "unverified_labels_visible",
        "status": "blocked" if missing else "passed",
        "detail": "missing markers: " + ", ".join(missing) if missing else "draft and candidate unverified labels are visible",
    }


def _case_claim_boundary_check(root: Path) -> dict[str, str]:
    path = root / "data" / "public_cases" / "cposs_ibp_candidate_v0.1.json"
    if not path.exists():
        return {"check": "public_case_claim_boundary", "status": "blocked", "detail": "public case JSON missing"}
    case = json.loads(path.read_text(encoding="utf-8"))
    blockers = " ".join(case.get("promotion_blockers", [])).lower()
    boundary = " ".join(case.get("claim_boundary", [])).lower()
    required_blockers = ["stability", "citation", "license", "disorder", "curator", "reviewer"]
    missing_blockers = [item for item in required_blockers if item not in blockers]
    required_boundary = ["experimental stability", "verified polymorph benchmark", "coordinate-bearing"]
    missing_boundary = [item for item in required_boundary if item not in boundary]
    status_ok = case.get("status") == "candidate_unverified"
    missing = missing_blockers + missing_boundary
    if not status_ok:
        missing.append("status=candidate_unverified")
    return {
        "check": "public_case_claim_boundary",
        "status": "blocked" if missing else "passed",
        "detail": "missing: " + ", ".join(missing) if missing else "case status, blockers, and claim boundary are explicit",
    }


def _release_boundary_check() -> dict[str, str]:
    report = release_boundary_report(artifact_paths=PUBLIC_ARTIFACT_PATHS)
    bad = [record for record in report["records"] if record["category"] != "candidate_public"]
    return {
        "check": "public_release_boundary",
        "status": "blocked" if bad else "passed",
        "detail": (
            "non-public: " + ", ".join(f"{record['path']}={record['category']}" for record in bad)
            if bad
            else f"{len(report['records'])} public artifact paths classify as candidate_public"
        ),
    }
