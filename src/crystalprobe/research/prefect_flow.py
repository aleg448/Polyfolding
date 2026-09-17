"""Optional Prefect observation layer; the local registry owns artifact validity."""

from __future__ import annotations

from pathlib import Path
import os
from typing import Any

from crystalprobe.research.campaign import Campaign, run_campaign


def run_prefect_campaign(
    campaign: Campaign, *, root: Path, output_dir: Path, max_jobs: int = 100, max_seconds: float = 300,
) -> dict[str, Any]:
    os.environ.setdefault("PREFECT_HOME", str(root / ".cache/prefect"))
    home = Path(os.environ["PREFECT_HOME"])
    home.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("PREFECT_SERVER_MEMO_STORE_PATH", str(home / "memo_store.toml"))
    os.environ.setdefault("PREFECT_SERVER_ANALYTICS_ENABLED", "false")
    from prefect import flow

    # Disable flow-result caching: every invocation must revalidate artifacts.
    @flow(name="crystalprobe-research-campaign", persist_result=False, retries=0)
    def execute() -> dict[str, Any]:
        return run_campaign(campaign, root=root, output_dir=output_dir,
                            max_jobs=max_jobs, max_seconds=max_seconds)

    return execute()
