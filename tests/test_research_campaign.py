import json
import sqlite3
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

import crystalprobe.research.campaign as research
from crystalprobe.research.campaign import Campaign, ResearchTask, run_campaign


WORKER = '''import argparse,json,time
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--request'); p.add_argument('--output')
a=p.parse_args(); request=json.loads(Path(a.request).read_text())
mode=request['parameters'].get('mode','ok')
if mode=='timeout': time.sleep(5)
if mode=='crash': raise RuntimeError('worker failure fixture')
out=Path(a.output); artifact=out.parent/'measurement.txt'
artifact.write_text('fixture measurement')
status='blocked' if mode=='blocked' else 'succeeded'
review='verified' if mode=='promote' else 'candidate_unverified'
out.write_text(json.dumps({'execution_status':status,'review_status':review,
                          'artifacts':['measurement.txt'],'detail':mode}))
'''


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    worker = tmp_path / "worker.py"
    worker.write_text(WORKER, encoding="utf-8")
    monkeypatch.setattr(research, "_runtime", lambda *args: {"python": sys.version})
    return tmp_path, worker


def task(name="first", **kwargs):
    return ResearchTask(task_id=name, kind="conformer", parameters=kwargs.pop("parameters", {}), **kwargs)


def run(workspace, tasks, **kwargs):
    root, worker = workspace
    return run_campaign(Campaign(campaign_id="fixture", question="Does restart preserve work?", tasks=tasks),
                        root=root, output_dir=root / "outputs/campaign", worker=worker, **kwargs)


def test_resume_preserves_attempts_and_reuses_hash_valid_artifacts(workspace):
    tasks = [task(), task("second", dependencies=["first"])]
    first = run(workspace, tasks, max_jobs=1)
    assert first["status"] == "paused"
    assert first["counts"] == {"succeeded": 1, "pending": 1}
    second = run(workspace, tasks)
    assert second["counts"] == {"cached": 1, "succeeded": 1}
    third = run(workspace, tasks)
    assert third["jobs_executed"] == 0
    assert third["counts"] == {"cached": 2}
    with sqlite3.connect(workspace[0] / "outputs/campaign/registry.sqlite") as db:
        assert db.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 3
        assert db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0] == 2
    assert third["review_status"] == "candidate_unverified"
    assert third["claim_ready_count"] == 0


def test_changed_input_invalidates_only_affected_branch(workspace):
    root, _ = workspace
    input_file = root / "input.txt"
    input_file.write_text("before")
    tasks = [task(input_files=["input.txt"]), task("child", dependencies=["first"]), task("unrelated")]
    run(workspace, tasks)
    input_file.write_text("after")
    result = run(workspace, tasks)
    assert result["jobs_executed"] == 2
    assert result["tasks"]["unrelated"]["state"] == "cached"


def test_tampered_artifact_is_not_reused(workspace):
    first = run(workspace, [task()])
    artifact = next(path for path in first["tasks"]["first"]["artifacts"] if path.endswith("measurement.txt"))
    Path(artifact).write_text("tampered")
    second = run(workspace, [task()])
    assert second["jobs_executed"] == 1
    assert second["tasks"]["first"]["attempt_id"] != first["tasks"]["first"]["attempt_id"]


def test_dependency_block_does_not_stop_unrelated_work(workspace):
    result = run(workspace, [task(parameters={"mode": "blocked"}),
                             task("child", dependencies=["first"]), task("other")])
    assert result["status"] == "completed_with_issues"
    assert result["tasks"]["child"]["state"] == "dependency_blocked"
    assert result["tasks"]["other"]["state"] == "succeeded"


def test_timeout_has_bounded_attempts_and_saved_logs(workspace):
    result = run(workspace, [task(parameters={"mode": "timeout"}, timeout_seconds=0.1)])
    assert result["jobs_executed"] == 2
    assert result["counts"] == {"timeout": 1}
    assert all(Path(path).exists() for path in result["tasks"]["first"]["logs"].values())


def test_worker_cannot_promote_a_record(workspace):
    result = run(workspace, [task(parameters={"mode": "promote"})])
    assert result["tasks"]["first"]["state"] == "failed"
    assert "cannot promote" in result["tasks"]["first"]["reason"]


def test_prior_running_attempt_is_marked_interrupted(workspace):
    first = run(workspace, [task()])
    db_path = workspace[0] / "outputs/campaign/registry.sqlite"
    with sqlite3.connect(db_path) as db:
        db.execute("UPDATE attempts SET state='running'")
    second = run(workspace, [task()])
    assert second["jobs_executed"] == 1
    with sqlite3.connect(db_path) as db:
        state = db.execute("SELECT state FROM attempts WHERE attempt_id=?",
                           (first["tasks"]["first"]["attempt_id"],)).fetchone()[0]
    assert state == "interrupted"


def test_lock_prevents_two_writers(workspace):
    root, _ = workspace
    directory = root / "outputs/campaign"
    directory.mkdir(parents=True)
    with sqlite3.connect(directory / "worker_lock.sqlite") as lock:
        lock.execute("BEGIN EXCLUSIVE")
        with pytest.raises(RuntimeError, match="another campaign worker"):
            run(workspace, [task()])


def test_invalid_dag_is_rejected_before_execution():
    with pytest.raises(ValidationError, match="duplicate"):
        Campaign(campaign_id="x", question="q", tasks=[task(), task()])
    with pytest.raises(ValidationError, match="unknown dependencies"):
        Campaign(campaign_id="x", question="q", tasks=[task(dependencies=["absent"])])
    with pytest.raises(ValueError):
        Campaign(campaign_id="x", question="q", tasks=[task(dependencies=["first"])])


def test_uncacheable_model_runs_again(workspace):
    run(workspace, [task(cacheable=False)])
    result = run(workspace, [task(cacheable=False)])
    assert result["jobs_executed"] == 1


def test_stable_per_molecule_seed_does_not_depend_on_panel_order():
    from crystalprobe.research.molecules import molecule_campaign
    from tests.test_conformer_generation import _records

    first = molecule_campaign(_records())
    reordered = molecule_campaign(reversed(_records()))
    assert {t.task_id: t.parameters for t in first.tasks} == {t.task_id: t.parameters for t in reordered.tasks}


def test_missing_runtime_is_recorded_as_blocker(tmp_path):
    worker = tmp_path / "worker.py"
    worker.write_text(WORKER)
    result = run_campaign(Campaign(campaign_id="fixture", question="q", tasks=[task(python="nonexistent-python")]),
                          root=tmp_path, output_dir=tmp_path / "outputs/campaign", worker=worker)
    assert result["counts"] == {"blocked": 1}
    saved = json.loads((tmp_path / "outputs/campaign/latest.json").read_text())
    assert saved["claim_ready_count"] == 0


def test_source_and_environment_changes_invalidate_reuse(workspace, monkeypatch):
    run(workspace, [task()])
    root, worker = workspace
    worker.write_text(WORKER + "\n# new worker revision\n")
    assert run(workspace, [task()])["jobs_executed"] == 1
    monkeypatch.setattr(research, "_runtime", lambda *args: {"python": "changed environment"})
    assert run(workspace, [task()])["jobs_executed"] == 1


def test_source_changed_midrun_invalidates_attempt(workspace, monkeypatch):
    original = research._attempt

    def change_source(*args):
        result = original(*args)
        workspace[1].write_text(WORKER + "\n# modified during execution\n")
        return result

    monkeypatch.setattr(research, "_attempt", change_source)
    report = run(workspace, [task()])
    assert report["counts"] == {"invalidated": 1}
    assert report["provenance"]["source_changed_during_run"] is True
    with sqlite3.connect(workspace[0] / "outputs/campaign/registry.sqlite") as db:
        assert db.execute("SELECT state FROM attempts").fetchone()[0] == "invalidated"


@pytest.mark.parametrize("payload", ["[]", "{\"execution_status\":\"succeeded\","
                                    "\"review_status\":\"candidate_unverified\",\"artifacts\":\"bad\"}",
                                    json.dumps({"execution_status": "succeeded",
                                                "review_status": "candidate_unverified", "conformer": []})])
def test_malformed_worker_results_are_recorded(workspace, payload):
    workspace[1].write_text(WORKER + f"\nout.write_text({payload!r})\n")
    result = run(workspace, [task()])
    assert result["counts"] == {"failed": 1}


@pytest.mark.parametrize("value", [None, [], "invalid", 1])
def test_malformed_molecule_parameters_rejected_before_execution(value):
    with pytest.raises(ValidationError, match="molecule"):
        task(parameters={"molecule": value})


@pytest.mark.parametrize("cached_json", ["not json", "[]", '{"artifacts": []}',
                                       '{"artifacts": {"x": 5}}'])
def test_corrupt_cache_record_does_not_abort_run(workspace, cached_json):
    run(workspace, [task()])
    with sqlite3.connect(workspace[0] / "outputs/campaign/registry.sqlite") as db:
        db.execute("UPDATE attempts SET result_json=?", (cached_json,))
    result = run(workspace, [task()])
    assert result["counts"] == {"succeeded": 1}
    assert result["jobs_executed"] == 1
