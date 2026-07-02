"""
Location: tests/test_runner_integration.py
Purpose: Integration test proving T5 (guard)/T7 (scorecard)/T8 (manifest) are actually WIRED
         into engine/runner.py's real leaf-run path, not just unit-tested in isolation -- the
         exact dead-control risk the DESIGN doc calls out for the guard applies equally to
         "a scorecard/manifest module that exists but nothing ever calls."
Run: cd tests && python3 -m unittest test_runner_integration -v
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

import runner  # noqa: E402


class _FakeClient:
    def __init__(self, *a, **kw):
        pass

    def generate(self, prompt, temperature):
        return '{"participation_type": "participating"}'


def _make_leaf(tmp_path):
    leaf_dir = tmp_path / "fake_leaf"
    (leaf_dir / "corpus" / "questions").mkdir(parents=True)
    (leaf_dir / "task.py").write_text(
        'TASK = {"name": "fake_leaf", '
        '"fields": {"participation_type": {"type": "enum", '
        '"values": ["participating", "non-participating"]}}, '
        '"build_prompt": lambda i: i["document"]}\n'
    )
    oracle = [
        {"id": "a0", "participation_type": "participating"},
        {"id": "a1", "participation_type": "non-participating"},
    ]
    with open(leaf_dir / "oracle.jsonl", "w") as f:
        for o in oracle:
            f.write(json.dumps(o) + "\n")
    for o in oracle:
        (leaf_dir / "corpus" / "questions" / f"{o['id']}.txt").write_text("doc text")
    return leaf_dir


class TestManifestAndScorecardAreWiredIntoRunLeaf(unittest.TestCase):
    def test_run_leaf_writes_a_manifest_per_model(self):
        with tempfile.TemporaryDirectory() as td:
            leaf_dir = _make_leaf(Path(td))
            model_set = [("fake", None, _FakeClient)]
            # small n_runs is exercised by directly calling run_model rather than mutating the
            # module-level N_RUNS constant.
            task = runner._load_task(leaf_dir)
            instances, _ = runner.load_instances(leaf_dir, "participation_type")
            runner.N_RUNS = 2
            try:
                runner.run_model(leaf_dir, task, "fake", _FakeClient, None, instances)
            finally:
                runner.N_RUNS = 20
            manifest_path = leaf_dir / "manifest_fake.json"
            self.assertTrue(manifest_path.exists())
            m = json.loads(manifest_path.read_text())
            for required in ("leaf", "model", "data_version", "n_runs", "temperature", "timestamp"):
                self.assertIn(required, m)

    def test_run_leaf_writes_a_scorecard_html(self):
        with tempfile.TemporaryDirectory() as td:
            leaf_dir = _make_leaf(Path(td))
            model_set = [("fake", None, _FakeClient)]
            runner.N_RUNS = 2
            try:
                runner.run_leaf(leaf_dir, model_set=model_set)
            finally:
                runner.N_RUNS = 20
            scorecard_path = leaf_dir / "scorecard.html"
            self.assertTrue(scorecard_path.exists())
            html = scorecard_path.read_text()
            self.assertIn("fake_leaf", html)
            self.assertNotIn("0 tasks loaded", html)  # real items were scored, must not refuse

    def test_guard_config_actually_caps_calls_during_a_real_leaf_run(self):
        calls = {"n": 0}

        class _CountingClient(_FakeClient):
            def generate(self, prompt, temperature):
                calls["n"] += 1
                return super().generate(prompt, temperature)

        with tempfile.TemporaryDirectory() as td:
            leaf_dir = _make_leaf(Path(td))
            model_set = [("fake", None, _CountingClient)]
            runner.N_RUNS = 20  # would be 2 items x 20 runs = 40 calls without a guard
            try:
                runner.run_leaf(leaf_dir, model_set=model_set, guard_config={"max_steps": 3})
            finally:
                runner.N_RUNS = 20
            self.assertEqual(calls["n"], 3)  # guard actually stopped it, not just configured
            scored = json.loads((leaf_dir / "scored.json").read_text())
            self.assertTrue(scored["fake"]["guard"]["tripped"])


class TestGuardConfigFromEnv(unittest.TestCase):
    """cli.py's `probity-bench run --max-steps N` reaches a subprocess (each leaf's run.py
    shim), which calls run_leaf() with no guard_config -- so run_leaf must fall back to reading
    PROBITY_MAX_STEPS/PROBITY_MAX_COST_USD from the environment rather than the guard silently
    never applying through that path (same dead-control class as T5 itself)."""

    def test_env_vars_set_the_guard_when_no_explicit_config_given(self):
        import os
        old = {k: os.environ.get(k) for k in ("PROBITY_MAX_STEPS", "PROBITY_MAX_COST_USD")}
        os.environ["PROBITY_MAX_STEPS"] = "3"
        os.environ.pop("PROBITY_MAX_COST_USD", None)
        try:
            cfg = runner._guard_config_from_env()
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
        self.assertEqual(cfg, {"max_steps": 3})

    def test_no_env_vars_gives_none_unlimited_by_default(self):
        import os
        old = {k: os.environ.get(k) for k in ("PROBITY_MAX_STEPS", "PROBITY_MAX_COST_USD")}
        os.environ.pop("PROBITY_MAX_STEPS", None)
        os.environ.pop("PROBITY_MAX_COST_USD", None)
        try:
            cfg = runner._guard_config_from_env()
        finally:
            for k, v in old.items():
                if v is not None:
                    os.environ[k] = v
        self.assertIsNone(cfg)

    def test_env_var_actually_caps_a_real_run_leaf_call_with_no_explicit_config(self):
        import os
        calls = {"n": 0}

        class _CountingClient(_FakeClient):
            def generate(self, prompt, temperature):
                calls["n"] += 1
                return super().generate(prompt, temperature)

        old = os.environ.get("PROBITY_MAX_STEPS")
        os.environ["PROBITY_MAX_STEPS"] = "2"
        try:
            with tempfile.TemporaryDirectory() as td:
                leaf_dir = _make_leaf(Path(td))
                model_set = [("fake", None, _CountingClient)]
                runner.N_RUNS = 20
                try:
                    runner.run_leaf(leaf_dir, model_set=model_set)  # no explicit guard_config
                finally:
                    runner.N_RUNS = 20
        finally:
            if old is None:
                os.environ.pop("PROBITY_MAX_STEPS", None)
            else:
                os.environ["PROBITY_MAX_STEPS"] = old
        self.assertEqual(calls["n"], 2)


if __name__ == "__main__":
    unittest.main()
