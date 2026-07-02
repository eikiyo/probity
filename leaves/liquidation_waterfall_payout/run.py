"""
Location: leaves/liquidation_waterfall_payout/run.py
Purpose: Thin shim -- run THIS leaf via shared engine/runner.py at the FAST_SET (gemma3:1b + deepseek).
Calls: engine.runner.run_leaf

WHY this file exists (rather than every leaf reimplementing its own run loop): every leaf in
this repo has an IDENTICAL run.py apart from its own directory -- all the actual logic (loading
the oracle, calling each model N times, checkpointing, scoring, writing scored.json) lives once
in engine/runner.py. This is the project's reuse-first convention (root CLAUDE.md §0.8): a leaf
is "pluggable" into the shared engine purely by exposing a task.py with the right TASK shape (see
task.py's own docstring) -- run.py's only job is to point run_leaf() at this leaf's own directory
and tell it which model tier to use.

Usage (for anyone cloning this repo and wanting to reproduce or extend results):
  cd leaves/liquidation_waterfall_payout && python3 run.py
This is resumable -- engine/harness.py checkpoints every single model call to
runs_<model-label>.jsonl as it goes, so killing and re-running this script picks up where it
left off rather than re-spending API calls / re-running the local model from scratch.

Output: writes/updates runs_gemma3-1b.jsonl, runs_deepseek-v4f.jsonl (raw per-run records) and
        scored.json (the aggregated wobble/consistency/accuracy numbers) in this directory.
Success criteria: scored.json ends up with one key per model in FAST_SET (currently
        "gemma3-1b" and "deepseek-v4f"), each holding an "accuracy" and "reliability" block --
        see engine/scorer.py's docstrings for exactly what those blocks contain.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from runner import run_leaf, FAST_SET  # noqa: E402

if __name__ == "__main__":
    run_leaf(Path(__file__).parent, model_set=FAST_SET)
