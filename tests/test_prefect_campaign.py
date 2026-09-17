import sys
from types import SimpleNamespace

from crystalprobe.research.campaign import Campaign, ResearchTask
from crystalprobe.research import prefect_flow


def test_optional_flow_revalidates_instead_of_caching_the_campaign(monkeypatch, tmp_path):
    observed = {}

    def flow(**options):
        observed.update(options)
        return lambda function: function

    def run(*args, **kwargs):
        observed["budgets"] = (kwargs["max_jobs"], kwargs["max_seconds"])
        return {"status": "completed_with_issues"}

    monkeypatch.setitem(sys.modules, "prefect", SimpleNamespace(flow=flow))
    monkeypatch.setattr(prefect_flow, "run_campaign", run)
    monkeypatch.setenv("PREFECT_HOME", str(tmp_path / "prefect"))
    monkeypatch.delenv("PREFECT_SERVER_MEMO_STORE_PATH", raising=False)
    campaign = Campaign(campaign_id="fixture", question="q", tasks=[
        ResearchTask(task_id="one", kind="conformer", parameters={}),
    ])
    result = prefect_flow.run_prefect_campaign(
        campaign, root=tmp_path, output_dir=tmp_path / "outputs/campaign", max_jobs=2, max_seconds=5,
    )
    assert result["status"] == "completed_with_issues"
    assert observed["persist_result"] is False
    assert observed["retries"] == 0
    assert observed["budgets"] == (2, 5)
