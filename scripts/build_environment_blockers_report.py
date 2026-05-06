"""Build an active Python dependency blocker report."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import json
import subprocess
from pathlib import Path

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.insight.environment import OPTIONAL_DEPENDENCIES
from crystalprobe.insight.environment import environment_blockers_markdown, environment_blockers_report


def _probe_runner(name: str, python: Path) -> dict[str, object] | None:
    if not python.exists():
        return None
    modules = [dependency["module"] for dependency in OPTIONAL_DEPENDENCIES]
    code = (
        "import importlib.util, json, sys; "
        f"mods={modules!r}; "
        "print(json.dumps({'python_executable': sys.executable, "
        "'modules': {m: importlib.util.find_spec(m) is not None for m in mods}}, sort_keys=True))"
    )
    try:
        completed = subprocess.run(
            [str(python), "-c", code],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception as exc:
        return {
            "name": name,
            "python_executable": str(python),
            "status": "probe_failed",
            "error": str(exc),
            "modules": {},
        }
    data = json.loads(completed.stdout)
    return {
        "name": name,
        "python_executable": data["python_executable"],
        "status": "probe_ok",
        "modules": data["modules"],
    }


def _configured_runners(root: Path) -> list[dict[str, object]]:
    candidates = [
        ("project_venv", root / ".venv" / "Scripts" / "python.exe"),
        ("fairchem_venv", root / ".venv-fairchem" / "Scripts" / "python.exe"),
    ]
    runners = []
    for name, python in candidates:
        row = _probe_runner(name, python)
        if row:
            runners.append(row)
    return runners


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-runner-probe", action="store_true", help="Only inspect the active Python process")
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_environment_blockers.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_environment_blockers.md"))
    args = parser.parse_args()

    report = environment_blockers_report(
        configured_runners=[] if args.no_runner_probe else _configured_runners(Path.cwd()),
    )
    atomic_write_json(args.json_out, report)
    atomic_write_text(args.md_out, environment_blockers_markdown(report))
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
