"""Generate deterministic AMPETP perturbation CIFs for sensitivity studies."""

from __future__ import annotations

from pathlib import Path

from build_ccdc_sensitivity_set import main as generic_main


def main() -> int:
    import sys

    sys.argv = [
        sys.argv[0],
        str(Path("data/sources/ccdc/ccdc_amphetamine_phosphate_1036952-978407.cif")),
        "--block-id",
        "AMPETP",
        "--title",
        "AMPETP deterministic perturbation sensitivity set",
        "--output-dir",
        str(Path("outputs/ampetp_sensitivity")),
        "--manifest",
        str(Path("outputs/ampetp_sensitivity_manifest.json")),
    ]
    return generic_main()


if __name__ == "__main__":
    raise SystemExit(main())
