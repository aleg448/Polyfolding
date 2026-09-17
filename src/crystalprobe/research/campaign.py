"""Single-worker research DAG with durable attempts and validated artifact reuse."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import time
import uuid
import zipfile
from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
from graphlib import TopologicalSorter
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from crystalprobe.core.io import atomic_write_json, atomic_write_text
from crystalprobe.core.ledger import file_sha256, object_sha256


class ResearchTask(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: str = Field(pattern=r"^[A-Za-z0-9_.-]+$")
    kind: Literal["conformer", "backend"]
    parameters: dict[str, Any]
    dependencies: list[str] = Field(default_factory=list)
    input_files: list[str] = Field(default_factory=list)
    python: str = sys.executable
    timeout_seconds: float = Field(default=90, gt=0, allow_inf_nan=False)
    max_attempts: int = Field(default=2, ge=1, le=5)
    cacheable: bool = True

    @model_validator(mode="after")
    def valid_parameters(self) -> ResearchTask:
        for key in ("molecule", "options"):
            if key in self.parameters and not isinstance(self.parameters[key], dict):
                raise ValueError(f"task {key} parameter must be an object")
        return self


class Campaign(BaseModel):
    model_config = ConfigDict(extra="forbid")
    campaign_id: str = Field(pattern=r"^[A-Za-z0-9_-]+$")
    question: str = Field(min_length=1)
    tasks: list[ResearchTask] = Field(min_length=1)

    @model_validator(mode="after")
    def valid_graph(self) -> Campaign:
        ids = [task.task_id for task in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate task IDs")
        for task in self.tasks:
            if set(task.dependencies) - set(ids):
                raise ValueError(f"unknown dependencies for {task.task_id}")
        tuple(TopologicalSorter({task.task_id: task.dependencies for task in self.tasks}).static_order())
        return self


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _runtime(python: str, root: Path, timeout: float = 30) -> dict[str, Any]:
    probe = subprocess.run(
        [python, "-B", "-c", "import importlib.metadata as m,json,sys; "
         "print(json.dumps({'python':sys.version,'executable':sys.executable,"
         "'packages':sorted((d.metadata['Name'],d.version) for d in m.distributions())}))"],
        cwd=root, capture_output=True, text=True, timeout=timeout, check=True,
    )
    return json.loads(probe.stdout)


def _source_hash(root: Path, worker: Path) -> str:
    files = sorted({*root.glob("src/**/*.py"), *root.glob("scripts/*.py"), worker})
    if (root / "pyproject.toml").is_file():
        files.append(root / "pyproject.toml")
    return object_sha256({str(path.relative_to(root)): file_sha256(path) for path in files})


def _hash_inputs(paths: list[str], root: Path) -> dict[str, str]:
    return {str((root / path).resolve()): file_sha256(root / path) for path in paths}


def _artifacts_valid(result: dict[str, Any]) -> bool:
    if not isinstance(result, dict):
        return False
    artifacts = result.get("artifacts", {})
    if not isinstance(artifacts, dict) or not all(
        isinstance(path, str) and isinstance(digest, str) for path, digest in artifacts.items()
    ):
        return False
    try:
        return bool(artifacts) and all(
            Path(path).is_file() and file_sha256(path) == digest for path, digest in artifacts.items()
        )
    except (OSError, ValueError):
        return False


def _reusable_result(rows: list[sqlite3.Row]) -> dict[str, Any] | None:
    for row in rows:
        try:
            result = json.loads(row[0])
            if not _artifacts_valid(result):
                continue
            payload = result.get("payload")
            if not isinstance(payload, dict) or payload.get("review_status") != "candidate_unverified":
                continue
            if payload.get("execution_status") != "succeeded":
                continue
            if any(key in payload and not isinstance(payload[key], dict) for key in ("conformer", "backend_row")):
                continue
            return result
        except (ValueError, TypeError):
            continue
    return None


def _initialize(db: sqlite3.Connection) -> None:
    db.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT,
            plan_json TEXT NOT NULL, status TEXT NOT NULL, provenance_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS attempts (
            attempt_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(run_id),
            task_id TEXT NOT NULL, fingerprint TEXT NOT NULL, state TEXT NOT NULL,
            started_at TEXT NOT NULL, finished_at TEXT, result_json TEXT
        );
        CREATE INDEX IF NOT EXISTS attempts_fingerprint ON attempts(fingerprint, state);
    """)
    db.commit()


def run_campaign(
    campaign: Campaign, *, root: Path, output_dir: Path,
    max_jobs: int = 100, max_seconds: float = 300,
    worker: Path | None = None,
) -> dict[str, Any]:
    """Execute a bounded campaign; a repeated invocation resumes valid completed work.

    A dedicated SQLite lock is held for the invocation. The operating system
    releases it on process death, while attempts live in a separate database.
    """
    if max_jobs < 1 or not 0 < max_seconds < float("inf"):
        raise ValueError("positive finite campaign budgets are required")
    root = root.resolve()
    output_dir = output_dir.resolve()
    output_dir.relative_to(root / "outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    worker = (worker or root / "scripts/run_campaign_worker.py").resolve()
    with closing(sqlite3.connect(output_dir / "worker_lock.sqlite", timeout=0.1)) as lock:
        try:
            lock.execute("BEGIN EXCLUSIVE")
        except sqlite3.OperationalError as exc:
            raise RuntimeError("another campaign worker owns this output directory") from exc
        with closing(sqlite3.connect(output_dir / "registry.sqlite")) as db:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys=ON")
            _initialize(db)
            db.execute("UPDATE attempts SET state='interrupted', finished_at=? WHERE state='running'", (_utc(),))
            db.execute("UPDATE runs SET status='interrupted', finished_at=? WHERE status='running'", (_utc(),))
            db.commit()
            return _execute(campaign, root, output_dir, worker, db, max_jobs, max_seconds)


def _execute(
    campaign: Campaign, root: Path, output_dir: Path, worker: Path, db: sqlite3.Connection,
    max_jobs: int, max_seconds: float,
) -> dict[str, Any]:
    started = time.monotonic()
    run_id = uuid.uuid4().hex
    run_dir = output_dir / "runs" / run_id
    run_dir.mkdir(parents=True)
    source_hash = _source_hash(root, worker)
    source_archive = run_dir / "source.zip"
    with zipfile.ZipFile(source_archive, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted({*root.glob("src/**/*.py"), *root.glob("scripts/*.py"), worker}):
            archive.write(path, str(path.relative_to(root)))
        if (root / "pyproject.toml").is_file():
            archive.write(root / "pyproject.toml", "pyproject.toml")
    provenance = {"source_sha256": source_hash, "source_archive": str(source_archive),
                  "source_archive_sha256": file_sha256(source_archive), "runtimes": {}}
    db.execute("INSERT INTO runs VALUES (?, ?, NULL, ?, 'running', ?)",
               (run_id, _utc(), campaign.model_dump_json(), json.dumps(provenance)))
    db.commit()
    outcomes: dict[str, dict[str, Any]] = {}
    jobs = 0
    tasks = {task.task_id: task for task in campaign.tasks}
    order = TopologicalSorter({key: task.dependencies for key, task in tasks.items()}).static_order()
    try:
        for task_id in order:
            task = tasks[task_id]
            parents = {key: outcomes[key] for key in task.dependencies}
            if any(row["state"] not in {"succeeded", "cached"} for row in parents.values()):
                outcomes[task_id] = {"state": "dependency_blocked", "dependencies": list(parents)}
                continue
            if time.monotonic() - started >= max_seconds:
                outcomes[task_id] = {"state": "pending", "reason": "wall_time_budget"}
                continue
            try:
                if task.python not in provenance["runtimes"]:
                    provenance["runtimes"][task.python] = _runtime(
                        task.python, root, min(30, max_seconds - (time.monotonic() - started)),
                    )
                inputs = _hash_inputs(task.input_files, root)
                for parent in parents.values():
                    if not _artifacts_valid(parent):
                        raise ValueError("upstream artifact changed before execution")
                    inputs.update(parent["artifacts"])
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                outcomes[task_id] = {"state": "blocked", "reason": str(exc)}
                continue
            fingerprint = object_sha256({
                "task": task.model_dump(), "inputs": inputs, "source": source_hash,
                "runtime": provenance["runtimes"][task.python],
            })
            cached = db.execute(
                "SELECT result_json FROM attempts WHERE fingerprint=? AND state='succeeded' "
                "ORDER BY started_at DESC", (fingerprint,),
            ).fetchall() if task.cacheable else []
            reusable = _reusable_result(cached)
            if reusable:
                outcomes[task_id] = {**reusable, "state": "cached"}
                continue
            outcomes[task_id] = {"state": "pending", "reason": "job_budget"}
            for _ in range(task.max_attempts):
                remaining = max_seconds - (time.monotonic() - started)
                if jobs >= max_jobs or remaining <= 0:
                    break
                jobs += 1
                result = _attempt(task, parents, inputs, fingerprint, run_id, run_dir, worker,
                                  root, db, min(task.timeout_seconds, remaining))
                outcomes[task_id] = result
                if result["state"] not in {"timeout", "worker_failed"}:
                    break
    finally:
        try:
            source_changed = _source_hash(root, worker) != source_hash
        except OSError as exc:
            source_changed = True
            provenance["source_validation_error"] = str(exc)
        provenance["source_changed_during_run"] = source_changed
        if source_changed:
            db.execute("UPDATE attempts SET state='invalidated' WHERE run_id=? AND state='succeeded'", (run_id,))
            for row in outcomes.values():
                if row["state"] in {"succeeded", "cached"}:
                    row.update(state="invalidated", reason="source changed during campaign")
        followups = []
        for task_id, row in outcomes.items():
            parameters = tasks[task_id].parameters
            row["molecule"] = parameters.get("molecule", {}).get("common_name", parameters.get("molecule_id", ""))
            payload = row.get("payload", {})
            measurement = payload.get("backend_row", payload.get("conformer", {}))
            signature = measurement.get("issue_signature", "none")
            if row["state"] in {"failed", "worker_failed", "timeout", "blocked"} or signature != "none":
                followups.append({"task_id": task_id, "molecule": row["molecule"], "issue_signature": signature,
                                  "action": "inspect_failure" if row["state"] in {"failed", "worker_failed", "timeout"}
                                  else "resolve_blocker" if row["state"] == "blocked" else "inspect_warning"})
        counts = dict(Counter(row["state"] for row in outcomes.values()))
        complete = len(outcomes) == len(tasks) and not counts.get("pending")
        status = "completed" if complete else "paused"
        if any(row["state"] not in {"succeeded", "cached"} for row in outcomes.values()) and complete:
            status = "completed_with_issues"
        report = {
            "schema_version": "0.1.0", "campaign_id": campaign.campaign_id, "run_id": run_id,
            "question": campaign.question, "status": status, "counts": counts, "jobs_executed": jobs,
            "elapsed_seconds": time.monotonic() - started, "tasks": outcomes, "provenance": provenance,
            "followups": followups,
            "review_status": "candidate_unverified", "claim_ready_count": 0,
            "limitations": ["Execution and sanity checks are not experimental verification.",
                            "Single-worker local execution; no distributed or exactly-once execution guarantee.",
                            "Timeout bounds the direct worker process, not arbitrary descendant processes."],
        }
        atomic_write_json(run_dir / "evidence_packet.json", report)
        atomic_write_text(run_dir / "evidence_packet.md", campaign_markdown(report))
        atomic_write_json(output_dir / "latest.json", report)
        db.execute("UPDATE runs SET finished_at=?, status=?, provenance_json=? WHERE run_id=?",
                   (_utc(), status, json.dumps(provenance), run_id))
        db.commit()
    return report


def _attempt(
    task: ResearchTask, parents: dict[str, Any], inputs: dict[str, str], fingerprint: str,
    run_id: str, run_dir: Path, worker: Path, root: Path, db: sqlite3.Connection, timeout: float,
) -> dict[str, Any]:
    attempt_id = uuid.uuid4().hex
    directory = run_dir / "attempts" / attempt_id
    directory.mkdir(parents=True)
    request = {"kind": task.kind, "parameters": task.parameters, "parents": parents, "input_hashes": inputs}
    atomic_write_json(directory / "request.json", request)
    result_path = directory / "result.json"
    command = [task.python, "-B", str(worker), "--request", str(directory / "request.json"),
               "--output", str(result_path)]
    db.execute("INSERT INTO attempts VALUES (?, ?, ?, ?, 'running', ?, NULL, NULL)",
               (attempt_id, run_id, task.task_id, fingerprint, _utc()))
    db.commit()
    result = {"attempt_id": attempt_id, "fingerprint": fingerprint, "command": command,
              "state": "worker_failed", "artifacts": {}}
    try:
        with (directory / "stdout.log").open("w", encoding="utf-8") as stdout, \
                (directory / "stderr.log").open("w", encoding="utf-8") as stderr:
            process = subprocess.run(command, cwd=root, stdout=stdout, stderr=stderr, timeout=timeout, check=False)
        if process.returncode:
            result["reason"] = f"worker exit code {process.returncode}"
        else:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("worker result must be an object")
            state = payload.get("execution_status")
            if state not in {"succeeded", "blocked", "failed"}:
                raise ValueError("worker must declare a valid execution_status")
            if payload.get("review_status") != "candidate_unverified":
                raise ValueError("campaign workers cannot promote evidence")
            for key in ("conformer", "backend_row"):
                if key in payload and not isinstance(payload[key], dict):
                    raise ValueError(f"worker {key} must be an object")
            artifacts = {str(result_path): file_sha256(result_path)}
            declared = payload.get("artifacts", [])
            if not isinstance(declared, list) or not all(isinstance(path, str) for path in declared):
                raise ValueError("worker artifacts must be a list of paths")
            for relative in declared:
                path = (directory / relative).resolve()
                path.relative_to(directory.resolve())
                artifacts[str(path)] = file_sha256(path)
            if any(file_sha256(path) != digest for path, digest in inputs.items()):
                raise ValueError("input changed during execution")
            result.update(state=state, payload=payload, artifacts=artifacts)
    except subprocess.TimeoutExpired:
        result.update(state="timeout", reason="worker exceeded time budget")
    except (OSError, ValueError, TypeError) as exc:
        result.update(state="failed", reason=str(exc))
    result["logs"] = {name: str(directory / name) for name in ("stdout.log", "stderr.log")}
    db.execute("UPDATE attempts SET state=?, finished_at=?, result_json=? WHERE attempt_id=?",
               (result["state"], _utc(), json.dumps(result), attempt_id))
    db.commit()
    return result


def campaign_markdown(report: dict[str, Any]) -> str:
    lines = ["# Research Campaign Evidence Packet", "", f"Question: {report['question']}", "",
             f"Execution: `{report['status']}`. Evidence: `candidate_unverified`. Claim-ready records: **0**.",
             "", "| Molecule | Task | Execution | Detail |", "|---|---|---|---|"]
    for task_id, row in report["tasks"].items():
        detail = row.get("reason", row.get("payload", {}).get("detail", ""))
        detail = str(detail).replace("|", "/").replace("\n", " ")
        molecule = str(row.get("molecule", "")).replace("|", "/").replace("\n", " ")
        lines.append(f"| {molecule} | `{task_id}` | `{row['state']}` | {detail} |")
    lines.extend(["", "## Follow-up Queue", ""])
    for item in report.get("followups", []):
        lines.append(f"- `{item['task_id']}`: `{item['action']}` ({item['issue_signature']}).")
    lines.extend(["", "## Limitations", "", *[f"- {line}" for line in report["limitations"]]])
    return "\n".join(lines) + "\n"
