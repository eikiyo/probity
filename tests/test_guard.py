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
        # Derive the cap from the table rather than hardcoding a model's price: this asserts the
        # BEHAVIOUR (trips on the call that would breach) and cannot go stale when a provider
        # changes its list price, which is exactly what happened to the old $0.002 constant.
        unit = guard_mod.per_call_cost("deepseek-v4f")
        g = guard_mod.BrakePedalGuard(max_cost_usd=unit * 2.5)   # room for exactly 2 calls
        g.before_call("deepseek-v4f")
        g.before_call("deepseek-v4f")
        with self.assertRaises(guard_mod.GuardTripped):
            g.before_call("deepseek-v4f")
        self.assertEqual(g.steps_taken, 2)


class TestPerCallCostIsDerivedNotGuessed(unittest.TestCase):
    def test_local_models_are_free(self):
        for lab in guard_mod.LOCAL_MODELS:
            self.assertEqual(guard_mod.per_call_cost(lab), 0.0)

    def test_unknown_label_returns_none_so_the_caller_fails_closed(self):
        self.assertIsNone(guard_mod.per_call_cost("some-model-nobody-has-priced"))

    def test_estimate_matches_the_price_table_arithmetic(self):
        """MACHINES COUNT: recompute one entry independently instead of trusting the constant."""
        in_usd, out_usd, starve = guard_mod.MODEL_PRICING["gemma4-31b-or"]
        expected = (584 * in_usd + 25 * out_usd + starve * 16384 * out_usd) / 1e6
        self.assertAlmostEqual(guard_mod.per_call_cost("gemma4-31b-or"), expected, places=12)

    def test_a_starving_reasoning_model_costs_more_than_its_base_rate(self):
        """minimax burned its whole budget on 536 of 9400 calls; the estimate must reflect that,
        otherwise the cap is set from a fiction."""
        base = (584 * 0.15 + 25 * 0.90) / 1e6
        self.assertGreater(guard_mod.per_call_cost("minimax-m2.5-or"), base * 2)


class TestCapsForLeafPreventTheRealTruncation(unittest.TestCase):
    """
    REGRESSION, against ground truth. These 5 (leaf, model) cells were truncated in the committed
    0.7 arm by the flat $0.20 per-leaf cap. A size-derived cap must let every one of them run to
    completion. This is the positive control: it fails on the OLD cap and passes on the new one.
    """

    REAL_TRUNCATIONS = [                 # (label, items, expected_calls, calls it actually got)
        ("gemini3-flash-or", 18, 360, 333),
        ("gemini3-flash-or", 19, 380, 333),
        ("haiku-4.5-direct", 16, 320, 199),
        ("haiku-4.5-direct", 15, 300, 199),
        ("haiku-4.5-direct", 13, 260, 199),
    ]

    def test_new_caps_allow_every_owed_call(self):
        for label, _items, expected_calls, _got in self.REAL_TRUNCATIONS:
            caps = guard_mod.caps_for_leaf(label, expected_calls)
            g = guard_mod.BrakePedalGuard(**caps)
            for _ in range(expected_calls):
                g.before_call(label)          # must not raise anywhere in the full run
            self.assertFalse(g.tripped, f"{label} @ {expected_calls} calls still trips")

    def test_the_old_flat_cap_reproduces_the_historical_truncation_exactly(self):
        """
        Proves the test above is meaningful rather than vacuously green, by replaying the OLD
        arithmetic and landing on the exact call counts history recorded. Note this reproduces
        the accumulated float error too: 199 x $0.001 sums to 0.19900000000000004, so the 200th
        call's check (0.199... + 0.001 > 0.20) is True by one ulp and the cell stops at 199, not
        the 200 that exact arithmetic predicts. That one-ulp detail is why the recorded counts
        are 199 and not 200 -- reproducing it is what makes this a real diagnosis rather than a
        plausible story.
        """
        OLD_FLAT_CAP = 0.20
        for label, _items, expected_calls, got in self.REAL_TRUNCATIONS:
            unit = guard_mod.ESTIMATED_COST_PER_CALL_USD_LEGACY[label]
            spend, n_allowed = 0.0, 0
            for _ in range(expected_calls):
                if spend + unit > OLD_FLAT_CAP:      # same strict > as BrakePedalGuard
                    break
                spend += unit
                n_allowed += 1
            self.assertEqual(n_allowed, got,
                              f"{label}: replay allowed {n_allowed}, history recorded {got}")
            self.assertLess(n_allowed, expected_calls)   # it really did truncate

    def test_cap_still_stops_a_runaway(self):
        caps = guard_mod.caps_for_leaf("mistral-large-or", 100)
        g = guard_mod.BrakePedalGuard(**caps)
        with self.assertRaises(guard_mod.GuardTripped):
            for _ in range(10_000):           # a runaway loop, far past what the leaf owes
                g.before_call("mistral-large-or")

    def test_unknown_label_gets_the_most_expensive_cap_not_a_free_pass(self):
        known = guard_mod.caps_for_leaf("gpt-oss-120b-or", 200)["max_cost_usd"]
        unknown = guard_mod.caps_for_leaf("brand-new-model", 200)["max_cost_usd"]
        self.assertGreater(unknown, known)


class TestUnknownAndLocalModelCosts(unittest.TestCase):
    """Restored to their own class after the caps tests were inserted above them (they had been
    silently absorbed into the preceding class, which still ran them but filed them wrong)."""

    def test_unknown_model_charged_conservative_default_not_free(self):
        # Cap derived from the table's own most-expensive entry rather than a magic 0.001. The
        # old constant only worked because deepseek was mispriced at $0.002; with real prices the
        # dearest model is ~$0.00095, so a $0.001 cap no longer trips and the test would have
        # passed for the wrong reason.
        cap = guard_mod._UNKNOWN_MODEL_COST_USD * 0.5      # cannot afford even one call
        g = guard_mod.BrakePedalGuard(max_cost_usd=cap)
        with self.assertRaises(guard_mod.GuardTripped):
            g.before_call("some-brand-new-hosted-model-not-in-the-table")
        self.assertEqual(g.steps_taken, 0)

    def test_unknown_model_is_priced_as_the_dearest_known_one(self):
        dearest = max(guard_mod.ESTIMATED_COST_PER_CALL_USD.values())
        self.assertEqual(guard_mod._UNKNOWN_MODEL_COST_USD, dearest)
        self.assertGreater(dearest, 0.0)

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


class TestZeroCostIsNotFalsy(unittest.TestCase):
    """
    Regression for a real bug caught in engine/preflight.py: per_call_cost() returns 0.0 for a
    local model, and `cost or DEFAULT` treats 0.0 as falsy, so every FREE model was silently
    repriced at the most-expensive-unknown rate. Callers must branch on `is None`. This pins the
    distinction the bug depended on: free (0.0) and unknown (None) are different answers.
    """

    def test_free_and_unknown_are_distinguishable(self):
        self.assertEqual(guard_mod.per_call_cost("gemma3-1b"), 0.0)
        self.assertIsNone(guard_mod.per_call_cost("no-such-model"))
        self.assertIsNot(guard_mod.per_call_cost("gemma3-1b"), None)

    def test_the_falsy_idiom_would_have_been_wrong(self):
        free = guard_mod.per_call_cost("gemma3-1b")
        wrong = free or guard_mod._UNKNOWN_MODEL_COST_USD      # the bug
        right = free if free is not None else guard_mod._UNKNOWN_MODEL_COST_USD
        self.assertGreater(wrong, 0.0)          # the bug charges for a free model
        self.assertEqual(right, 0.0)            # the fix does not

    def test_a_free_leaf_cap_is_still_positive_so_step_caps_apply(self):
        caps = guard_mod.caps_for_leaf("gemma3-1b", 380)
        self.assertEqual(caps["max_steps"], int(380 * 1.1) + 1)
        self.assertGreater(caps["max_cost_usd"], 0.0)   # floor, so a $0 model is not capped at $0
