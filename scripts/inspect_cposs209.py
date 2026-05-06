"""Inspect the locally downloaded CPOSS209 supplemental CIF bundle."""

from __future__ import annotations

try:
    from scripts import _path_bootstrap  # noqa: F401
except ImportError:
    import _path_bootstrap  # noqa: F401

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from ase.io import read
from crystalprobe.datahub.cposs209 import index_cposs_directory, summarize_cposs_records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("zip_path", type=Path, default=Path("data/sources/cposs209/cg5c00255_si_004.zip"), nargs="?")
    args = parser.parse_args()

    zip_path = args.zip_path
    extract_dir = zip_path.with_suffix("")
    with zipfile.ZipFile(zip_path) as archive:
        members = [{"name": item.filename, "size": item.file_size} for item in archive.infolist()]
    cif_paths = sorted(extract_dir.glob("*.cif"))
    first = read(str(cif_paths[0]), index=0) if cif_paths else None
    cposs_records = index_cposs_directory(extract_dir) if extract_dir.exists() else []
    report = {
        "zip_path": str(zip_path),
        "bytes": zip_path.stat().st_size,
        "md5": hashlib.md5(zip_path.read_bytes()).hexdigest(),
        "members": members,
        "extracted_cifs": [str(path) for path in cif_paths],
        "index_summary": summarize_cposs_records(cposs_records),
        "first_structure": None
        if first is None
        else {
            "file": str(cif_paths[0]),
            "natoms": len(first),
            "formula": first.get_chemical_formula(),
            "cellpar": first.cell.cellpar().tolist(),
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
