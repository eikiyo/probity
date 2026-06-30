"""
Location: engine/harness.py
Purpose: Run each instance N times, checkpoint per-run to JSONL (resumable). Task-dict API.
Functions: run_harness(), _execute_run(), _parse_json_response(), _checkpoint_run()
Calls: models.LLMClient, normalize.canonical()
Imports: json, pathlib, normalize
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from models import LLMClient
import normalize


def run_harness(
    client: LLMClient,
    task: Dict[str, Any],
    instances: List[Tuple[Dict[str, Any], Dict[str, Any]]],
    n_runs: int = 20,
    temperature: float = 0.7,
    checkpoint_file: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Run instances N times, checkpoint every run to JSONL. Resumable. Returns (runs, stats)."""
    checkpoint_path = Path(checkpoint_file or f"runs_{task['name']}.jsonl")
    runs: List[Dict[str, Any]] = []
    if checkpoint_path.exists():
        with open(checkpoint_path, "r") as f:
            runs = [json.loads(line) for line in f]
    done_keys = {tuple(r["_key"]) for r in runs if "_key" in r}

    parse_failures, total_runs = 0, 0
    total_target = len(instances) * n_runs
    for inst_idx, (instance, _truth) in enumerate(instances):
        for run_idx in range(n_runs):
            total_runs += 1
            _print_progress(task["name"], getattr(client, "model", "?"), total_runs, total_target)
            if (inst_idx, run_idx) in done_keys:
                continue
            record = _execute_run(client, task, instance, inst_idx, run_idx, temperature)
            if record.get("parsed") is None:
                parse_failures += 1
            _checkpoint_run(checkpoint_path, record)
            runs.append(record)
    return runs, {"parse_failures": parse_failures, "total_runs": total_runs}


def _execute_run(client, task, instance, inst_idx, run_idx, temperature) -> Dict[str, Any]:
    """One generation: prompt -> parse -> normalize. Fail closed (parsed=None), never silent."""
    base = {"_key": (inst_idx, run_idx), "instance_idx": inst_idx, "run_idx": run_idx}
    try:
        raw = client.generate(task["build_prompt"](instance), temperature)
    except Exception as e:
        return {**base, "error": str(e), "parsed": None}
    parsed = _parse_json_response(raw)
    if parsed is None:
        return {**base, "raw_output": (raw or "")[:200], "parsed": None}
    normalized = {
        fn: normalize.canonical(parsed[fn], fs["type"])
        for fn, fs in task["fields"].items()
        if fn in parsed
    }
    return {**base, "parsed": parsed, "normalized": normalized}


def _parse_json_response(raw_output: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from raw output. Fail closed on parse error."""
    if not raw_output or not raw_output.strip():
        return None
    text = raw_output.strip()
    if text.startswith("```"):
        text = text[3:]
        if text[:4].lower() == "json":
            text = text[4:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    candidates = [text]
    start, end = text.find("{"), text.rfind("}") + 1
    if start != -1 and end > start:
        candidates.append(text[start:end])
    for candidate in candidates:
        obj = _try_load(candidate)
        if obj is not None:
            return obj
    return None


def _try_load(candidate: str) -> Optional[Dict[str, Any]]:
    """Parse one JSON candidate; return None (never raise) so the caller tries the next."""
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def _checkpoint_run(checkpoint_file: Path, run_record: Dict[str, Any]) -> None:
    """Append a single run to the checkpoint JSONL file."""
    rec = dict(run_record)
    rec["_key"] = list(rec["_key"])  # tuple -> list for JSON
    with open(checkpoint_file, "a") as f:
        f.write(json.dumps(rec) + "\n")


def _print_progress(task_name: str, model: str, done: int, total: int) -> None:
    """Coarse progress (~every 5%) so long local-model runs are observable (heat-aware)."""
    step = max(1, total // 20)
    if done % step == 0 or done == total:
        bar = "█" * (20 * done // total) + "░" * (20 - 20 * done // total)
        print(f"    {task_name} [{model}] {bar} {done}/{total} ({100 * done // total}%)", flush=True)
