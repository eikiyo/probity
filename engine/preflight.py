"""
Location: engine/preflight.py
Purpose: Prove the whole 0.1 call path works BEFORE a 169,200-call sweep spends real money.
         Makes exactly ONE call per model (11 calls, ~1 cent total) against a real leaf prompt at
         the target temperature, and reports latency, parse success, and the provider's own
         reported token usage -- which is also the only way to replace the ESTIMATED completion
         cost with a measured one, since the harness never recorded usage during the 0.7 sweep.
Functions: probe_one(), main()
Calls: models.*, runner.<model sets>
Imports: argparse, json, sys, time, pathlib
Run: python3 engine/preflight.py --temperature 0.1 [--plan-only]
"""

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

ENGINE = Path(__file__).parent
sys.path.insert(0, str(ENGINE))

import coverage                                                        # noqa: E402
import guard as guard_mod                                              # noqa: E402
import routing                                                         # noqa: E402
from models import (AnthropicClient, DeepSeekClient, OllamaClient,      # noqa: E402
                     OpenRouterClient)

REPO = ENGINE.parent

# The published lineup, with the client each label is served by. This is the ONE place the
# label -> (client, model id) mapping for the sweep is written down; the sweeps are launched
# from it so a typo cannot put a model on the wrong routing layer mid-experiment.
LINEUP = [
    ("gemma3-1b",        "ollama",     "gemma3:1b"),
    ("gemma3-1b-qat",    "ollama",     "gemma3:1b-it-qat"),
    ("deepseek-v4f",     "deepseek",   "deepseek-v4-flash"),
    ("deepseek-v4p",     "deepseek",   "deepseek-v4-pro"),
    ("haiku-4.5-direct", "anthropic",  "claude-haiku-4-5-20251001"),
    ("gemma4-31b-or",    "openrouter", "google/gemma-4-31b-it"),
    ("mistral-large-or", "openrouter", "mistralai/mistral-large-2512"),
    ("minimax-m2.5-or",  "openrouter", "minimax/minimax-m2.5"),
    ("llama3.3-70b-or",  "openrouter", "meta-llama/llama-3.3-70b-instruct"),
    ("gemini3-flash-or", "openrouter", "google/gemini-3-flash-preview"),
    ("gpt-oss-120b-or",  "openrouter", "openai/gpt-oss-120b"),
    ("gpt5-mini-or",     "openrouter", "openai/gpt-5-mini"),
]

HOSTED = {"deepseek", "anthropic", "openrouter"}


def build_client(kind, model_id):
    if kind == "ollama":
        return OllamaClient(model_id)
    if kind == "deepseek":
        return DeepSeekClient()
    if kind == "anthropic":
        return AnthropicClient(model_id)
    return OpenRouterClient(model_id)


def sample_prompt():
    """A REAL prompt from a real leaf, not a synthetic 'say ok'. A smoke test that does not
    exercise the actual prompt shape proves the credential works and nothing else."""
    import importlib.util
    leaf = REPO / "leaves" / "drag_along"
    spec = importlib.util.spec_from_file_location("task_smoke", leaf / "task.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    oracle = [json.loads(l) for l in open(leaf / "oracle.jsonl") if l.strip()][0]
    doc = (leaf / "corpus" / "questions" / f"{oracle['id']}.txt").read_text(encoding="utf-8")
    return mod.TASK, mod.TASK["build_prompt"]({"id": oracle["id"], "document": doc})


def probe_one(label, kind, model_id, prompt, task, temperature):
    """One real call. Returns a row describing what actually happened, never an assumption."""
    row = {"label": label, "routing": kind, "model_id": model_id, "ok": False,
            "seconds": None, "parsed": False, "answer": None, "error": None}
    try:
        client = build_client(kind, model_id)
    except Exception as e:
        row["error"] = f"client init failed: {e}"
        return row
    row["routing"] = routing.routing_for(client)
    t0 = time.time()
    try:
        raw = client.generate(prompt, temperature)
    except Exception as e:
        row["seconds"] = round(time.time() - t0, 2)
        row["error"] = str(e)[:200]
        return row
    row["seconds"] = round(time.time() - t0, 2)
    row["ok"] = True
    import harness
    parsed = harness._parse_json_response(raw) or harness._lenient_extract(raw, task["fields"])
    row["parsed"] = parsed is not None
    row["answer"] = (json.dumps(parsed) if parsed else (raw or "")[:80])
    row["raw_chars"] = len(raw or "")
    return row


def or_balance():
    """Read-only GET. Probing the balance before a bulk paid run is standing practice here: a
    quota wall at item N wastes the N-1 already-spent calls with no clean resume marker."""
    import os
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        return None
    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/credits",
                                      headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode())["data"]
        return d["total_credits"] - d["total_usage"]
    except Exception:
        return None


def total_plan(temperature):
    """Calls and estimated spend for a FULL arm across the whole lineup, before anything runs."""
    leaves = [REPO / l for l in _built_leaf_paths()]
    owed = sum(coverage.expected_calls(d, 20) for d in leaves)
    rows = []
    for label, kind, _mid in LINEUP:
        done = sum(len(coverage.recorded_keys(coverage.checkpoint_path(
            d, label, coverage.artifact_suffix(temperature)))) for d in leaves)
        # `is None`, NOT `or`: per_call_cost returns 0.0 for a local Ollama model, and 0.0 is
        # FALSY, so `cost or DEFAULT` silently reprices every free local model at the
        # most-expensive-unknown rate ($0.00095/call = $8.94 for a full arm that actually costs
        # nothing). Caught here by the plan printing $8.94 against gemma3-1b.
        cost = guard_mod.per_call_cost(label)
        if cost is None:
            cost = guard_mod._UNKNOWN_MODEL_COST_USD
        rows.append((label, kind, owed, done, owed - done, (owed - done) * cost))
    return rows


def _built_leaf_paths():
    reg = json.loads((REPO / "engine" / "registry.json").read_text())
    return [l["leaf"] for l in reg["leaves"] if l.get("tier") == "built" and "leaf" in l]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--temperature", type=float, required=True)
    p.add_argument("--plan-only", action="store_true", help="print the plan, make ZERO calls")
    p.add_argument("--skip-local", action="store_true",
                    help="skip ollama labels (they run on Kaggle, not this machine)")
    args = p.parse_args()

    rows = total_plan(args.temperature)
    hosted_cost = sum(r[5] for r in rows if r[1] in HOSTED)
    print(f"=== PLAN: full arm at temp={args.temperature} "
          f"(namespace {coverage.artifact_suffix(args.temperature)}) ===")
    print(f"{'label':20s} {'routing':11s} {'owed':>7s} {'done':>7s} {'to run':>7s} {'est $':>8s}")
    for label, kind, owed, done, todo, cost in rows:
        print(f"{label:20s} {kind:11s} {owed:7d} {done:7d} {todo:7d} {cost:8.2f}")
    print(f"{'TOTAL (hosted only)':32s} {sum(r[4] for r in rows if r[1] in HOSTED):15d} "
          f"{hosted_cost:16.2f}")
    bal = or_balance()
    if bal is not None:
        print(f"OpenRouter balance: ${bal:.2f}")
    if args.plan_only:
        print("\n--plan-only: no calls made.")
        return

    task, prompt = sample_prompt()
    print(f"\n=== SMOKE: 1 real call per model at temp={args.temperature} "
          f"(prompt {len(prompt)} chars from leaves/drag_along) ===")
    results = []
    for label, kind, model_id in LINEUP:
        if args.skip_local and kind == "ollama":
            print(f"{label:20s} SKIPPED (runs on Kaggle)")
            continue
        r = probe_one(label, kind, model_id, prompt, task, args.temperature)
        results.append(r)
        status = "ok" if r["ok"] and r["parsed"] else ("UNPARSED" if r["ok"] else "FAIL")
        print(f"{label:20s} {status:9s} {str(r['seconds']):>7}s  {r['answer'] or r['error']}")

    bad = [r for r in results if not (r["ok"] and r["parsed"])]
    print(f"\nsmoke: {len(results) - len(bad)}/{len(results)} models answered and parsed")
    if bad:
        print("NOT READY -- fix these before launching the sweep:")
        for r in bad:
            print(f"  - {r['label']}: {r['error'] or 'returned unparseable output'}")
        sys.exit(1)
    print("READY.")


if __name__ == "__main__":
    main()
