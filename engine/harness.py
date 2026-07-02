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
import guard as guard_mod


class StaleCheckpointError(RuntimeError):
    """
    Raised when a checkpoint file's recorded instance_idx values no longer fit the CURRENT
    instances list (fewer items than before, or an id mismatch at some position) -- see the
    module docstring's "WHY item_id / staleness checking exists" section for the full story
    and the real incident that motivated this.
    """
    pass


def run_harness(
    client: LLMClient,
    task: Dict[str, Any],
    instances: List[Tuple[Dict[str, Any], Dict[str, Any]]],
    n_runs: int = 20,
    temperature: float = 0.7,
    checkpoint_file: Optional[str] = None,
    guard: Optional["guard_mod.BrakePedalGuard"] = None,
    model_label: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    What: runs every instance N times, checkpointing each individual model call to a JSONL file
          as it goes (so a killed/interrupted run can resume instead of re-spending API calls or
          re-burning local-model compute from position zero).
    Why the staleness check exists (added 2026-07-02, after an adversarial audit found REAL
          corrupted results): this function's resume logic used to trust ANY existing checkpoint
          record purely by its POSITIONAL instance_idx, with no way to tell whether oracle.jsonl
          had been edited (items added/removed/reordered) since that checkpoint was written. If a
          leaf's oracle.jsonl shrank from 6 items to 4 (a real, confirmed case:
          leaves/post_money_valuation), the OLD checkpoint still had 20 stale records for
          positions 0-5; the next run against the NEW 4-item oracle would see positions 0-3
          "already done" and silently reuse those stale answers -- which were originally recorded
          against DIFFERENT real documents than whatever now sits at those same positions. This
          was VERIFIED, not theoretical: two independent models (gemma3:1b and deepseek-v4-flash)
          both scored the exact wrong answer for one item, and that wrong answer was an EXACT
          match for a NEIGHBORING item's true value -- the unmistakable signature of an index
          shift, not two coincidental model failures. A repo-wide sweep found 3 leaves with this
          exact corruption signature (post_money_valuation, flag_full_ratchet, and
          securities_exemption -- the last already independently flagged in vault/mistakes.md for
          an unrelated 124-item mislabeling incident that also left a stale 124-position
          checkpoint behind).
    Output: (runs, stats) -- runs is the full list of run records (old + newly executed this
            call); stats is {"parse_failures": int, "total_runs": int} for this invocation only.
    Success criteria / fail-closed behavior: if ANY existing checkpoint record's instance_idx is
            >= len(instances) (proof the oracle shrank since that checkpoint was written), OR if
            a checkpoint record carries an "item_id" that doesn't match the CURRENT instance at
            that position (proof of a reorder, even without shrinkage), this function raises
            StaleCheckpointError immediately and does NOT execute any new model calls or silently
            drop the mismatched records -- per root CLAUDE.md §0.7 ("fail closed, never silent"),
            an ambiguous/stale checkpoint must stop the run and force a human decision (typically:
            move the old runs_<model>.jsonl aside and re-run fresh), not silently produce a
            corrupted scored.json that LOOKS complete and clean.
    """
    checkpoint_path = Path(checkpoint_file or f"runs_{task['name']}.jsonl")
    runs: List[Dict[str, Any]] = []
    if checkpoint_path.exists():
        with open(checkpoint_path, "r") as f:
            runs = [json.loads(line) for line in f]

    _validate_checkpoint_freshness(runs, instances, checkpoint_path)
    done_keys = {tuple(r["_key"]) for r in runs if "_key" in r}

    parse_failures, total_runs = 0, 0
    total_target = len(instances) * n_runs
    guard_tripped, guard_reason = False, None
    label_for_guard = model_label or getattr(client, "model", "unknown")
    for inst_idx, (instance, _truth) in enumerate(instances):
        for run_idx in range(n_runs):
            if (inst_idx, run_idx) in done_keys:
                total_runs += 1
                _print_progress(task["name"], getattr(client, "model", "?"), total_runs, total_target)
                continue
            if guard is not None:
                try:
                    guard.before_call(label_for_guard)
                except guard_mod.GuardTripped as e:
                    guard_tripped, guard_reason = True, e.reason
                    print(f"    GUARD TRIPPED: {e.reason} -- stopping run, {len(runs)}/{total_target} "
                          f"calls completed.", flush=True)
                    return runs, {"parse_failures": parse_failures, "total_runs": total_runs,
                                   "guard_tripped": guard_tripped, "guard_reason": guard_reason}
            total_runs += 1
            _print_progress(task["name"], getattr(client, "model", "?"), total_runs, total_target)
            record = _execute_run(client, task, instance, inst_idx, run_idx, temperature)
            if record.get("parsed") is None:
                parse_failures += 1
            _checkpoint_run(checkpoint_path, record)
            runs.append(record)
    return runs, {"parse_failures": parse_failures, "total_runs": total_runs,
                   "guard_tripped": guard_tripped, "guard_reason": guard_reason}


def _validate_checkpoint_freshness(runs, instances, checkpoint_path) -> None:
    """
    What: cross-checks every existing checkpoint record against the CURRENT instances list before
          any of it is trusted for resume. Two independent checks, either one fails closed:
          (1) POSITION-RANGE check (works on old AND new-format records alike): does any
              checkpoint record reference an instance_idx that doesn't exist in the current
              instances list at all? This alone would have caught all 3 real incidents found on
              2026-07-02's audit (all 3 involved an oracle SHRINKING after the checkpoint was
              written).
          (2) IDENTITY check (only possible for records written after this fix, which now store
              "item_id"): for records whose instance_idx IS in range, does the checkpoint's
              item_id match the id of the CURRENT instance at that same position? This catches a
              reorder that keeps the same item COUNT (which check #1 alone would miss).
    Why a separate function instead of inlining this in run_harness(): this is a pure
          validate-or-raise check with no side effects (doesn't touch the network, doesn't write
          anything) -- keeping it separate makes it independently testable (see
          tests/test_engine.py's TestCheckpointFreshness) without needing to mock an LLM client.
    Output: None on success (checkpoint is safe to resume from). Raises StaleCheckpointError with
            a specific, actionable message (which position, what it expected vs found) on failure.
    """
    n_instances = len(instances)
    for r in runs:
        idx = r.get("instance_idx")
        if idx is None:
            continue
        if idx >= n_instances:
            raise StaleCheckpointError(
                f"{checkpoint_path}: checkpoint references instance_idx={idx}, but the current "
                f"oracle only has {n_instances} item(s). This means oracle.jsonl was edited "
                f"(items removed/reordered) AFTER this checkpoint was written -- resuming would "
                f"silently score fresh answers against the wrong items. Move or delete "
                f"{checkpoint_path.name} (and its matching scored.json entry) and re-run this "
                f"leaf fresh."
            )
        recorded_id = r.get("item_id")
        if recorded_id is not None:
            current_id = instances[idx][0].get("id")
            if recorded_id != current_id:
                raise StaleCheckpointError(
                    f"{checkpoint_path}: checkpoint position {idx} was recorded for item "
                    f"'{recorded_id}', but the current oracle has '{current_id}' at that "
                    f"position -- oracle.jsonl was reordered. Move or delete "
                    f"{checkpoint_path.name} (and its matching scored.json entry) and re-run "
                    f"this leaf fresh."
                )


def _execute_run(client, task, instance, inst_idx, run_idx, temperature) -> Dict[str, Any]:
    """One generation: prompt -> parse -> normalize. Fail closed (parsed=None), never silent.
    Stores item_id (the instance's real oracle id, not just its positional index) so a FUTURE
    resume can validate identity, not just position -- see _validate_checkpoint_freshness()."""
    base = {"_key": (inst_idx, run_idx), "instance_idx": inst_idx, "run_idx": run_idx,
            "item_id": instance.get("id")}
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
    """Parse one JSON candidate; return None (never raise) so the caller tries the next.
    Fail closed on a non-dict parse (e.g. a model emitting a bare number/string/list instead
    of the requested JSON object) -- that is a parse failure, not a usable result."""
    try:
        obj = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


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
