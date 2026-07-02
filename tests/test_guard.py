"""
Location: tests/test_guard.py
Purpose: Unit + integration tests for engine/guard.py -- the brake-pedal runtime cap. Verifies
         the DESIGN doc's guard invariant directly: "the guard always trips before exceeding its
         configured cap" (never after), and that it is wired to the actual runner call-site, not
         just decorative config (the dead-control sad-path the DESIGN doc names explicitly).
Run: cd tests && python3 -m unittest test_guard -v
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

import guard as guard_mod          # noqa: E402
import harness                     # noqa: E402


class TestBrakePedalGuardSteps(unittest.TestCase):
    def test_allows_calls_up_to_the_cap(self):
        g = guard_mod.BrakePedalGuard(max_steps=3)
        for _ in range(3):
            g.before_call("gemma3-1b")  # must not raise
        self.assertEqual(g.steps_taken, 3)
        self.assertFalse(g.tripped)

    def test_trips_before_the_call_that_would_exceed_the_cap(self):
        g = guard_mod.BrakePedalGuard(max_steps=3)
        for _ in range(3):
            g.before_call("gemma3-1b")
        with self.assertRaises(guard_mod.GuardTripped):
            g.before_call("gemma3-1b")
        # the 4th call must NOT have been counted as taken -- cap enforced pre-call, not post.
        self.assertEqual(g.steps_taken, 3)
        self.assertTrue(g.tripped)

    def test_stays_tripped_on_repeated_calls_same_reason(self):
        g = guard_mod.BrakePedalGuard(max_steps=1)
        g.before_call("gemma3-1b")
        with self.assertRaises(guard_mod.GuardTripped) as first:
            g.before_call("gemma3-1b")
        with self.assertRaises(guard_mod.GuardTripped) as second:
            g.before_call("gemma3-1b")
        self.assertEqual(first.exception.reason, second.exception.reason)

    def test_no_cap_configured_never_trips_on_steps(self):
        g = guard_mod.BrakePedalGuard()
        for _ in range(1000):
            g.before_call("gemma3-1b")
        self.assertFalse(g.tripped)


class TestBrakePedalGuardCost(unittest.TestCase):
    def test_trips_before_exceeding_cost_cap(self):
        # deepseek-v4f costs $0.002/call (ESTIMATED_COST_PER_CALL_USD) -- cap at $0.005 allows
        # exactly 2 calls (spend 0.004) then must trip on the 3rd (would be 0.006 > 0.005).
        g = guard_mod.BrakePedalGuard(max_cost_usd=0.005)
        g.before_call("deepseek-v4f")
        g.before_call("deepseek-v4f")
        with self.assertRaises(guard_mod.GuardTripped):
            g.before_call("deepseek-v4f")
        self.assertEqual(g.steps_taken, 2)

    def test_unknown_model_charged_conservative_default_not_free(self):
        g = guard_mod.BrakePedalGuard(max_cost_usd=0.001)
        with self.assertRaises(guard_mod.GuardTripped):
            g.before_call("some-brand-new-hosted-model-not-in-the-table")
        self.assertEqual(g.steps_taken, 0)

    def test_local_models_free_never_trip_cost_cap(self):
        g = guard_mod.BrakePedalGuard(max_cost_usd=0.0001)
        for _ in range(500):
            g.before_call("gemma3-1b")
        self.assertFalse(g.tripped)


class TestBrakePedalGuardAllowedModels(unittest.TestCase):
    def test_trips_immediately_on_disallowed_model(self):
        g = guard_mod.BrakePedalGuard(allowed_models=frozenset({"gemma3-1b"}))
        with self.assertRaises(guard_mod.GuardTripped):
            g.before_call("deepseek-v4f")

    def test_allowed_model_passes(self):
        g = guard_mod.BrakePedalGuard(allowed_models=frozenset({"gemma3-1b"}))
        g.before_call("gemma3-1b")  # must not raise


class _RunawayClient:
    """A model client that never stops answering -- simulates the runaway-agent sad path the
    DESIGN doc names ("runner calls a paid model API in a loop with no cap")."""

    def __init__(self):
        self.call_count = 0

    def generate(self, prompt, temperature):
        self.call_count += 1
        return '{"participation_type": "participating"}'


class TestGuardWiredIntoHarness(unittest.TestCase):
    """Integration: the guard must wrap the REAL runner call-site (harness.run_harness), not
    just exist as an unused config object -- this is the specific dead-control risk the DESIGN
    doc's gaps-sadpath table calls out by name."""

    TASK = {
        "name": "t",
        "fields": {"participation_type": {"type": "enum",
                   "values": ["participating", "non-participating", "capped"]}},
        "build_prompt": lambda i: i["document"],
    }

    def test_run_harness_stops_at_the_cap_and_reports_the_trip(self):
        instances = [({"id": f"i{k}", "document": "doc"}, {"participation_type": "participating"})
                     for k in range(10)]  # 10 instances x 20 runs = 200 calls requested
        client = _RunawayClient()
        g = guard_mod.BrakePedalGuard(max_steps=5)
        with tempfile.TemporaryDirectory() as td:
            runs, stats = harness.run_harness(
                client, self.TASK, instances, n_runs=20, temperature=0.7, guard=g,
                model_label="gemma3-1b", checkpoint_file=str(Path(td) / "runs.jsonl"),
            )
        # exactly 5 calls were actually made -- the runaway agent did NOT get to run all 200.
        self.assertEqual(client.call_count, 5)
        self.assertEqual(len(runs), 5)
        self.assertTrue(stats["guard_tripped"])
        self.assertIn("max_steps", stats["guard_reason"])

    def test_run_harness_without_a_guard_is_unaffected(self):
        instances = [({"id": "i0", "document": "doc"}, {"participation_type": "participating"})]
        client = _RunawayClient()
        with tempfile.TemporaryDirectory() as td:
            runs, stats = harness.run_harness(
                client, self.TASK, instances, n_runs=3, temperature=0.7,
                checkpoint_file=str(Path(td) / "runs.jsonl"),
            )
        self.assertEqual(client.call_count, 3)
        self.assertFalse(stats["guard_tripped"])


if __name__ == "__main__":
    unittest.main()
