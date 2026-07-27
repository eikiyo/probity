"""
Location: engine/runner.py
Purpose: ONE shared leaf runner (reuse-first; supersedes per-leaf run.py copies). Field-agnostic —
         FIELD + CLASSES come from the leaf's task.TASK. The model SET is defined here in ONE place:
         FAST_SET (gemma3:1b + deepseek) is the per-leaf build-out set; BIG_BATCH (qwen3.5:27b,
         + hosted frontier later) is the deferred comprehensive sweep. WOBBLE is the
         headline metric; accuracy is reported beside it, never averaged.
Functions: load_instances(), run_model(), run_leaf(), main()
Calls: harness, scorer, models; <leaf>/task.TASK
Imports: sys, json, subprocess, importlib.util, pathlib
"""

import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path

ENGINE = Path(__file__).parent
sys.path.insert(0, str(ENGINE))

import harness                                       # noqa: E402
import scorer                                        # noqa: E402
import guard as guard_mod                            # noqa: E402
import manifest as manifest_mod                       # noqa: E402
import coverage                                      # noqa: E402
import routing                                       # noqa: E402
from models import OllamaClient, DeepSeekClient, OpenRouterClient, AnthropicClient  # noqa: E402

# (label, ollama_model_or_None, factory). None ollama_model => hosted (no local unload).
FAST_SET = [
    ("gemma3-1b",   "gemma3:1b", lambda: OllamaClient("gemma3:1b")),
    ("deepseek-v4f", None,       lambda: DeepSeekClient()),
]
# Deferred to ONE comprehensive sweep once every leaf exists (postponed per Eikiyo 2026-06-30).
BIG_BATCH = [
    ("qwen3.5-27b", "qwen3.5:27b",     lambda: OllamaClient("qwen3.5:27b")),
]

N_RUNS = 20
TEMPERATURE = 0.7


def openrouter_model_set(label, model_id):
    """One-model hosted set for a single OpenRouter model -- reused across the "10 recommended
    models" lineup (gemma-4-31b-it first, per Eikiyo 2026-07-02) instead of hardcoding a new
    named SET constant per hosted model. `label` must have a matching entry in
    guard.ESTIMATED_COST_PER_CALL_USD or it falls back to the most-expensive-known-cost default
    (fail closed on an unrecognized label, see guard.py's module docstring)."""
    return [(label, None, lambda: OpenRouterClient(model_id))]


def anthropic_model_set(label, model_id):
    """One-model hosted set for the direct Anthropic API -- explicitly authorized 2026-07-03
    (Sec 0.10 override, see models.AnthropicClient's docstring). Same shape as
    openrouter_model_set() so run_hosted_sweep.py's leaf/worker-parallel machinery works
    unchanged regardless of which provider backs the label."""
    return [(label, None, lambda: AnthropicClient(model_id))]


def deepseek_model_set(label, model_id=None):
    """One-model hosted set for the DIRECT DeepSeek API. Same shape as the openrouter/anthropic
    sets so run_hosted_sweep.py drives it unchanged. `model_id` is accepted and ignored: the
    published 0.7 arm ran DeepSeekClient's own default model, and letting a sweep flag silently
    swap the model would break the one thing this experiment holds fixed."""
    return [(label, None, lambda: DeepSeekClient())]


def _load_task(leaf_dir):
    spec = importlib.util.spec_from_file_location(f"task_{leaf_dir.name}", leaf_dir / "task.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TASK


def _load_scorecard():
    """results/scorecard.py lives outside engine/'s sys.path -- load it the same explicit-path
    way _load_task() loads a leaf's task.py, rather than adding a second package to sys.path."""
    results_dir = ENGINE.parent / "results"
    spec = importlib.util.spec_from_file_location("scorecard", results_dir / "scorecard.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_instances(leaf_dir, field):
    """Build (instance, ground_truth) pairs from questions + the SEPARATED oracle (file order)."""
    oracle = [json.loads(l) for l in open(leaf_dir / "oracle.jsonl") if l.strip()]
    instances = []
    for o in oracle:
        q = (leaf_dir / "corpus" / "questions" / f"{o['id']}.txt").read_text(encoding="utf-8")
        instances.append(({"id": o["id"], "document": q}, {field: o[field]}))
    return instances, oracle


def run_model(leaf_dir, task, label, factory, ollama_model, instances, guard_config=None,
              max_workers=1, temperature=None):
    """Run one model at N=20; unload local model after. Returns accuracy + reliability(wobble).
    guard_config (optional dict: max_steps/max_cost_usd/allowed_models) wraps this run with a
    BrakePedalGuard at the ACTUAL harness call-site (engine/guard.py) -- a guard that only lived
    in config and never reached the call-site would be the dead-control trap the DESIGN doc
    names. A reproducibility manifest (engine/manifest.py) is written next to the checkpoint on
    every run, guard-tripped or not, so a partial run is still reproducible from what it did do.

    `temperature` None means the LEGACY arm: sample at the module default 0.7 AND keep the
    original unsuffixed artifact names, so every existing caller (the 60 leaf run.py shims, the
    CLI, the tests) behaves exactly as before. An explicit temperature both sets the sampling
    temperature and namespaces the artifacts, so the 0.1 arm can never overwrite the 0.7 one."""
    client = factory()
    temp = TEMPERATURE if temperature is None else temperature
    suffix = coverage.artifact_suffix(temperature)
    ckpt = str(coverage.checkpoint_path(leaf_dir, label, suffix))
    g = guard_mod.BrakePedalGuard(**guard_config) if guard_config else None
    runs, stats = harness.run_harness(client, task, instances, n_runs=N_RUNS,
                                       temperature=temp, checkpoint_file=ckpt,
                                       guard=g, model_label=label, max_workers=max_workers)
    if ollama_model:
        subprocess.run(["ollama", "stop", ollama_model], capture_output=True)
    m = manifest_mod.build_manifest(leaf_name=leaf_dir.name, model_label=label, run_records=runs,
                                     task_name=task["name"], n_runs=N_RUNS, temperature=temp,
                                     extra=_routing_extra(client, temp))
    (leaf_dir / f"manifest_{suffix}{label}.json").write_text(json.dumps(m, indent=1),
                                                              encoding="utf-8")
    return {"model": getattr(client, "model", label),
            "temperature_requested": temp,
            "routing": routing.routing_for(client),
            "accuracy": scorer.score_accuracy(task, instances, runs),
            "reliability": scorer.score_runs(task, instances, runs),
            "temperature_honoured": routing.honoured_temperature(client),
            "guard": {"tripped": stats.get("guard_tripped", False),
                       "reason": stats.get("guard_reason")}}


def _routing_extra(client, temperature):
    """Manifest `extra` block: which provider path served this cell and at what requested
    temperature. Recorded per run so the paper's appendix table is regenerable from disk rather
    than reconstructed from memory of how a sweep was launched."""
    return {"routing": routing.routing_for(client),
            "model_id": getattr(client, "model", None),
            "temperature_requested": temperature}


def _guard_config_from_env():
    """Fallback source for guard_config when a caller doesn't pass one explicitly -- needed
    because probity_cli's `run` subcommand launches each leaf's run.py shim as a SEPARATE
    subprocess (see leaves/*/run.py: `run_leaf(Path(__file__).parent, model_set=FAST_SET)`,
    no guard_config arg, by design zero-touch across all 60 leaf shims). Without this, a user
    passing `--max-steps`/`--max-cost` at the CLI would set an env var that nothing ever reads
    -- the same dead-control failure mode the guard itself exists to prevent."""
    cfg = {}
    if os.environ.get("PROBITY_MAX_STEPS"):
        cfg["max_steps"] = int(os.environ["PROBITY_MAX_STEPS"])
    if os.environ.get("PROBITY_MAX_COST_USD"):
        cfg["max_cost_usd"] = float(os.environ["PROBITY_MAX_COST_USD"])
    return cfg or None


def run_leaf(leaf_dir, model_set=FAST_SET, only=None, guard_config=None, max_workers=1,
             temperature=None):
    leaf_dir = Path(leaf_dir)
    if guard_config is None:
        guard_config = _guard_config_from_env()
    task = _load_task(leaf_dir)
    field = list(task["fields"])[0]
    field_type = task["fields"][field].get("type", "enum")
    instances, oracle = load_instances(leaf_dir, field)
    field_values = task["fields"][field].get("values")
    if field_type == "number" or not field_values:
        # number, date, string, bool, or any type with no enumerable class list -- report the
        # distinct value set (or a plain count) instead of a per-class breakdown.
        vals = [o[field] for o in oracle]
        summary = f"values {sorted(set(map(str, vals)))}" if vals else "no items"
    else:
        classes = field_values
        summary = {c: sum(o[field] == c for o in oracle) for c in classes}
    print(f"{len(instances)} items  {summary}  N={N_RUNS} runs/item  field={field}\n", flush=True)
    scored = {}
    expected = coverage.expected_calls(leaf_dir, N_RUNS)
    out = leaf_dir / coverage.scored_filename(temperature)
    for label, omodel, factory in model_set:
        if only and label != only:
            continue
        print(f"=== {label} (N={N_RUNS}, temp={TEMPERATURE if temperature is None else temperature}) "
              f"===", flush=True)
        # Cap sized from what THIS leaf owes, not a flat constant. A flat cap cannot tell a
        # 1-item leaf from a 19-item one, which is how 5 cells got silently truncated in the
        # 0.7 sweep. An explicit caller-supplied guard_config still wins.
        caps = guard_config or guard_mod.caps_for_leaf(label, expected)
        res = run_model(leaf_dir, task, label, factory, omodel, instances,
                        guard_config=caps, max_workers=max_workers, temperature=temperature)
        a, r = res["accuracy"], res["reliability"]
        wob = r["field_flips"].get(field, 0.0) * 100
        print(f"  WOBBLE: {wob:.0f}% flipped across {N_RUNS} runs  |  consistency "
              f"{r['consistency_pct']:.0f}%  |  accuracy {a['accuracy_majority']*100:.0f}%", flush=True)
        # Fail closed + observable: a short cell is announced HERE, at the moment it happens,
        # instead of being discovered later by someone auditing checkpoints (root CLAUDE.md 0.7).
        cell = coverage.cell_status(leaf_dir, label, N_RUNS,
                                     coverage.artifact_suffix(temperature))
        if not cell["complete"]:
            print(f"  !! INCOMPLETE: {cell['recorded']}/{cell['expected']} calls recorded "
                  f"(short {cell['short_by']}). guard_tripped={res['guard']['tripped']} "
                  f"reason={res['guard']['reason']}", flush=True)
        print("", flush=True)
        scored[label] = res
        _merge_scored(out, scored)          # incremental, and safe against a concurrent writer
    print(f"wrote {out.name}")
    if scored:
        scorecard = _load_scorecard()
        guard_stats = _aggregate_guard_stats(scored)
        report = scorecard.build_report(leaf_dir.name, scored, guard_stats=guard_stats)
        print(scorecard.render_terminal(report))
        # Atomic: scorecard.html is keyed by LEAF too, so concurrent tracks both write it. A
        # plain write_text can interleave into corrupt HTML; a temp-file + rename means the worst
        # case is "one track's version wins", never a half-written file.
        _atomic_write(leaf_dir / "scorecard.html", scorecard.render_html(report))


def _merge_scored(out_path, new_results):
    """
    Merge one model's results into a leaf's shared scored file under an EXCLUSIVE file lock.

    Why a lock: this is a read-modify-write on a file keyed by LEAF, not by model, so every model
    that ever runs on this leaf writes the same file. Sequentially that is fine. The moment two
    drivers run concurrently -- e.g. an OpenRouter track beside a direct-API track, which is safe
    on rate limits because the providers are different -- both can read the same `prev`, each add
    only its own key, and the second write silently discards the first model's entire result. The
    checkpoints would still hold the raw calls, so the loss is recoverable, but it would be
    INVISIBLE: the scored file stays valid JSON and simply lacks a model.

    flock is advisory and per-file, so it costs nothing in the sequential case and makes the
    concurrent case correct. The lock is held across read AND write, which is the whole point --
    locking only the write would not prevent the stale read.
    """
    import fcntl
    lock_path = Path(str(out_path) + ".lock")
    with open(lock_path, "w") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            prev = json.loads(out_path.read_text()) if out_path.exists() else {}
            prev.update(new_results)
            out_path.write_text(json.dumps(prev, indent=1), encoding="utf-8")
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def _atomic_write(path, text):
    """Write via a temp file in the same directory + os.replace, which is atomic on POSIX."""
    import os
    tmp = path.with_suffix(path.suffix + f".tmp{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _aggregate_guard_stats(scored):
    """One guard line for the whole leaf's scorecard: TRIPPED if any model's run tripped
    (surface the first reason found), otherwise clean. None if no model carries guard info at
    all (an older scored.json written before T5 existed)."""
    entries = [v["guard"] for v in scored.values() if "guard" in v]
    if not entries:
        return None
    tripped = next((e for e in entries if e.get("tripped")), None)
    if tripped:
        return {"guard_tripped": True, "guard_reason": tripped.get("reason")}
    return {"guard_tripped": False, "guard_reason": None}


def main():
    if len(sys.argv) < 2:
        print("usage: python3 runner.py <leaf_dir> [--big-batch] [--only LABEL]"); return
    leaf = Path(sys.argv[1])
    if not leaf.is_absolute():
        leaf = (ENGINE.parent / "leaves" / sys.argv[1]) if not leaf.exists() else leaf
    ms = BIG_BATCH if "--big-batch" in sys.argv else FAST_SET
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    run_leaf(leaf, model_set=ms, only=only)


if __name__ == "__main__":
    main()
