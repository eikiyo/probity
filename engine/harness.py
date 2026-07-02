"""
Location: engine/harness.py
Purpose: Run each instance N times, checkpoint per-run to JSONL (resumable). Task-dict API.
Functions: run_harness(), _execute_run(), _parse_json_response(), _checkpoint_run()
Calls: models.LLMClient, normalize.canonical()
Imports: json, pathlib, normalize
"""

import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    max_workers: int = 1,
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

    if max_workers > 1:
        return _run_harness_parallel(client, task, instances, n_runs, temperature,
                                      checkpoint_path, guard, model_label, max_workers,
                                      runs, done_keys)

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


def _run_harness_parallel(client, task, instances, n_runs, temperature, checkpoint_path,
                           guard, model_label, max_workers, runs, done_keys) -> Tuple[
        List[Dict[str, Any]], Dict[str, Any]]:
    """
    What: same contract as run_harness()'s sequential loop, but dispatches the remaining
          (instance, run) calls across a thread pool instead of one at a time. Only reached
          when max_workers > 1 -- run_harness() routes here before its serial loop starts.
    Concurrency model: ONE lock serializes the guard check (guard.before_call()) so it always
          runs BEFORE the network call, exactly like the sequential path -- a thread only ever
          calls client.generate() after it has won the lock and passed the guard, so the guard's
          cap can never be overshot even under heavy contention (see
          tests/test_harness_parallel.py's TestParallelGuardNeverOvershoots). A second
          lock-protected section after the call appends the run record and its checkpoint line
          together, so the checkpoint file never sees an interleaved/partial write. The actual
          client.generate() call happens OUTSIDE the lock so workers overlap on the slow part.
    Output: same (runs, stats) shape as the sequential path.
    """
    todo = [
        (inst_idx, run_idx, instance)
        for inst_idx, (instance, _truth) in enumerate(instances)
        for run_idx in range(n_runs)
        if (inst_idx, run_idx) not in done_keys
    ]
    total_target = len(instances) * n_runs
    lock = threading.Lock()
    label_for_guard = model_label or getattr(client, "model", "unknown")
    state = {"parse_failures": 0, "total_runs": len(done_keys),
             "guard_tripped": False, "guard_reason": None}

    def _try_start() -> bool:
        with lock:
            if state["guard_tripped"]:
                return False
            if guard is not None:
                try:
                    guard.before_call(label_for_guard)
                except guard_mod.GuardTripped as e:
                    state["guard_tripped"], state["guard_reason"] = True, e.reason
                    print(f"    GUARD TRIPPED: {e.reason} -- stopping new dispatch, "
                          f"{len(runs)}/{total_target} calls completed so far.", flush=True)
                    return False
            return True

    def _worker(inst_idx, run_idx, instance) -> None:
        if not _try_start():
            return
        record = _execute_run(client, task, instance, inst_idx, run_idx, temperature)
        with lock:
            state["total_runs"] += 1
            _print_progress(task["name"], getattr(client, "model", "?"),
                             state["total_runs"], total_target)
            if record.get("parsed") is None:
                state["parse_failures"] += 1
            _checkpoint_run(checkpoint_path, record)
            runs.append(record)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_worker, inst_idx, run_idx, instance)
                   for inst_idx, run_idx, instance in todo]
        for f in as_completed(futures):
            f.result()  # re-raise any worker exception instead of swallowing it

    return runs, {"parse_failures": state["parse_failures"], "total_runs": state["total_runs"],
                   "guard_tripped": state["guard_tripped"], "guard_reason": state["guard_reason"]}


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
        # Observable, not silent (Sec 0.7) -- this used to be caught here and written ONLY to
        # the checkpoint file's "error" field, never printed. A 2026-07-03 incident: mistral-large
        # hit 40% 429 rate-limit failures across all 9400 calls of a full sweep, and the run
        # reported "0 errored" per-leaf / no 429 ever appeared in the console log -- the ONLY
        # trace was inside 60 separate checkpoint files nobody was grepping live. Print here so a
        # sustained failure (rate-limit, outage, bad concurrency setting) is visible AS IT
        # HAPPENS, not discovered later by someone manually auditing checkpoints after the fact.
        print(f"    [{task.get('name','?')}] call failed (inst={inst_idx} run={run_idx}): {e}",
              flush=True)
        return {**base, "error": str(e), "parsed": None}
    parsed = _parse_json_response(raw)
    if parsed is None:
        parsed = _lenient_extract(raw, task["fields"])
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


def _repair_bare_division(text: str) -> str:
    """Repair one observed gemma3-1b-qat failure mode: a number field answered as an
    unevaluated bare division, e.g. {"option_pool_shuffle": 1000000 / 11000000} instead of
    a number literal -- invalid JSON (division isn't a JSON token). Scoped tight to a JSON
    VALUE position only (":" immediately before, "," or "}" immediately after, both operands
    bare unquoted digits) so a legitimate quoted string containing "/" (e.g. a vesting-format
    answer like "4yr/1yr-cliff") is never touched -- that text is inside quotes, so the
    lookbehind ":" / lookahead "[,}]" never matches around it.
    """
    def _eval(m):
        num, den = float(m.group(1)), float(m.group(2))
        if den == 0:
            return m.group(0)
        val = num / den
        return f": {val:g}"
    return re.sub(
        r':\s*(-?\d+(?:\.\d+)?)\s*/\s*(-?\d+(?:\.\d+)?)\s*(?=[,}])', _eval, text,
    )


def _lenient_extract(raw: Optional[str], fields: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    What: fallback answer extraction, tried only after _parse_json_response() fails outright.
          Added 2026-07-03 per Eikiyo: "goal is not to judge JSON, to judge reasoning of the
          financial docs" -- a model's format slip (an invalid \_ escape, a wrong-but-unique JSON
          key, a bare value with no JSON wrapper at all) is not the same failure as getting the
          financial reasoning wrong, and scoring both as one "parse failure" number conflates a
          format confound with the actual thing this benchmark exists to measure. Every leaf has
          exactly ONE scored field (verified across all 60, see task.py TASK["fields"]) -- that is
          what makes "wrong key name" and "no JSON at all" safely recoverable: there is only one
          field the model could have meant.
    Two recovery paths, in order:
      1. Repair the one invalid-escape pattern actually observed (an unnecessary backslash before
         an underscore in a JSON key) and retry via _parse_json_response()'s own candidate
         extraction (code fences, brace-scan) -- reused, not duplicated. If the resulting dict has
         the expected field name, use it; if it has exactly one key of ANY name, use that (a
         model naming the field "safe_cap_type" instead of "safe_pre_post" is a naming slip, not
         an ambiguity -- there's nothing else that key could be). A dict with 2+ keys and no name
         match is genuinely ambiguous (which key is the answer?) and is NOT guessed at.
      2. A bare-value fallback for when the model emits no JSON structure at all (e.g. "6\n" for
         a number question). Gated tight to avoid ever guessing which part of a longer answer is
         the real one: no braces anywhere in the text (a broken JSON attempt must fail closed, not
         fall through here), no internal newline, <=60 chars. Within that gate, the value must
         still parse as the field's own type (a bare number must actually BE a number; a bare enum
         word must exactly match one of the task's own allowed values) or it fails closed too.
    Output: {field_name: raw_value_string} on success (fed through the SAME normalize.canonical()
            step as a normal parse, so type coercion/fail-closed still applies downstream), or
            None if nothing can be recovered without guessing.
    """
    if not raw:
        return None
    text = raw.strip()
    if not text:
        return None
    field_name = next(iter(fields))

    repaired = _repair_bare_division(text.replace("\\_", "_"))
    obj = _parse_json_response(repaired)
    if obj is not None:
        if field_name in obj:
            return {field_name: obj[field_name]}
        if len(obj) == 1:
            return {field_name: next(iter(obj.values()))}
        return None

    if "{" in text or "}" in text or "\n" in text or len(text) > 60:
        return None

    field_type = fields[field_name].get("type")
    if field_type == "number":
        try:
            float(re.sub(r"[\$,\s]", "", text))
        except ValueError:
            return None
        return {field_name: text}
    if field_type == "bool":
        if text.lower() in ("yes", "no", "true", "false", "y", "n", "1", "0"):
            return {field_name: text}
        return None
    if field_type == "enum":
        allowed = fields[field_name].get("values") or []
        if text.lower() in {v.lower() for v in allowed}:
            return {field_name: text}
        return None
    if field_type in ("string", "date"):
        return {field_name: text}
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
