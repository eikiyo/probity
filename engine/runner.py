"""
Location: engine/runner.py
Purpose: ONE shared leaf runner (reuse-first; supersedes per-leaf run.py copies). Field-agnostic —
         FIELD + CLASSES come from the leaf's task.TASK. The model SET is defined here in ONE place:
         FAST_SET (gemma3:1b + deepseek) is the per-leaf build-out set; BIG_BATCH (llama3.2, gemma4:12b,
         qwen3.5:27b, + hosted frontier later) is the deferred comprehensive sweep. WOBBLE is the
         headline metric; accuracy is reported beside it, never averaged.
Functions: load_instances(), run_model(), run_leaf(), main()
Calls: harness, scorer, models; <leaf>/task.TASK
Imports: sys, json, subprocess, importlib.util, pathlib
"""

import sys
import json
import subprocess
import importlib.util
from pathlib import Path

ENGINE = Path(__file__).parent
sys.path.insert(0, str(ENGINE))

import harness                                       # noqa: E402
import scorer                                        # noqa: E402
from models import OllamaClient, DeepSeekClient      # noqa: E402

# (label, ollama_model_or_None, factory). None ollama_model => hosted (no local unload).
FAST_SET = [
    ("gemma3-1b",   "gemma3:1b", lambda: OllamaClient("gemma3:1b")),
    ("deepseek-v4f", None,       lambda: DeepSeekClient()),
]
# Deferred to ONE comprehensive sweep once every leaf exists (postponed per Eikiyo 2026-06-30).
BIG_BATCH = [
    ("llama3.2-3b", "llama3.2:latest", lambda: OllamaClient("llama3.2:latest")),
    ("gemma4-12b",  "gemma4:12b",      lambda: OllamaClient("gemma4:12b")),
    ("qwen3.5-27b", "qwen3.5:27b",     lambda: OllamaClient("qwen3.5:27b")),
]

N_RUNS = 20
TEMPERATURE = 0.7


def _load_task(leaf_dir):
    spec = importlib.util.spec_from_file_location(f"task_{leaf_dir.name}", leaf_dir / "task.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TASK


def load_instances(leaf_dir, field):
    """Build (instance, ground_truth) pairs from questions + the SEPARATED oracle (file order)."""
    oracle = [json.loads(l) for l in open(leaf_dir / "oracle.jsonl") if l.strip()]
    instances = []
    for o in oracle:
        q = (leaf_dir / "corpus" / "questions" / f"{o['id']}.txt").read_text(encoding="utf-8")
        instances.append(({"id": o["id"], "document": q}, {field: o[field]}))
    return instances, oracle


def run_model(leaf_dir, task, label, factory, ollama_model, instances):
    """Run one model at N=20; unload local model after. Returns accuracy + reliability(wobble)."""
    client = factory()
    ckpt = str(leaf_dir / f"runs_{label}.jsonl")
    runs, _ = harness.run_harness(client, task, instances, n_runs=N_RUNS,
                                  temperature=TEMPERATURE, checkpoint_file=ckpt)
    if ollama_model:
        subprocess.run(["ollama", "stop", ollama_model], capture_output=True)
    return {"model": getattr(client, "model", label),
            "accuracy": scorer.score_accuracy(task, instances, runs),
            "reliability": scorer.score_runs(task, instances, runs)}


def run_leaf(leaf_dir, model_set=FAST_SET, only=None):
    leaf_dir = Path(leaf_dir)
    task = _load_task(leaf_dir)
    field = list(task["fields"])[0]
    classes = task["fields"][field]["values"]
    instances, oracle = load_instances(leaf_dir, field)
    counts = {c: sum(o[field] == c for o in oracle) for c in classes}
    print(f"{len(instances)} items  {counts}  N={N_RUNS} runs/item  field={field}\n", flush=True)
    scored = {}
    for label, omodel, factory in model_set:
        if only and label != only:
            continue
        print(f"=== {label} (N={N_RUNS}) ===", flush=True)
        res = run_model(leaf_dir, task, label, factory, omodel, instances)
        a, r = res["accuracy"], res["reliability"]
        wob = r["field_flips"].get(field, 0.0) * 100
        print(f"  WOBBLE: {wob:.0f}% flipped across {N_RUNS} runs  |  consistency "
              f"{r['consistency_pct']:.0f}%  |  accuracy {a['accuracy_majority']*100:.0f}%\n", flush=True)
        scored[label] = res
        out = leaf_dir / "scored.json"
        prev = json.loads(out.read_text()) if out.exists() else {}
        prev.update(scored)
        out.write_text(json.dumps(prev, indent=1), encoding="utf-8")  # incremental
    print("wrote scored.json")


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
