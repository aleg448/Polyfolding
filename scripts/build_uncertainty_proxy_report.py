"""Build uncalibrated uncertainty-proxy report from disagreement artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from crystalprobe.uncertainty.proxy import disagreement_uncertainty_proxy, uncertainty_proxy_markdown


DEFAULT_REPORTS = [
    Path("outputs/ampetp_backend_disagreement.json"),
    Path("outputs/cposs_high_priority_backend_disagreement.json"),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="append", type=Path, default=[])
    parser.add_argument("--json-out", type=Path, default=Path("outputs/crystalprobe_uncertainty_proxy_v0.json"))
    parser.add_argument("--md-out", type=Path, default=Path("outputs/crystalprobe_uncertainty_proxy_v0.md"))
    args = parser.parse_args()

    paths = args.report or DEFAULT_REPORTS
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in paths if path.exists()]
    proxy = disagreement_uncertainty_proxy(reports)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(proxy, indent=2, sort_keys=True), encoding="utf-8", newline="\n")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(uncertainty_proxy_markdown(proxy), encoding="utf-8", newline="\n")
    print(json.dumps({"json": str(args.json_out), "markdown": str(args.md_out)}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
