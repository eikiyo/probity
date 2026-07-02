"""
Location: tests/test_harness_parallel.py
Purpose: Correctness tests for harness.run_harness()'s max_workers>1 path -- added because
         OpenRouter (hosted, no local heat/compute constraint) lets Probity run many concurrent
         calls instead of the laptop-bound sequential loop. The load-bearing property is that
         concurrency must NEVER let the brake-pedal guard overshoot its cap (a race between
         "check the cap" and "count the call" is exactly the kind of bug parallelism introduces)
         and must never corrupt the checkpoint file with interleaved partial writes.
Run: cd tests && python3 -m unittest test_harness_parallel -v
"""

import json
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

import harness   # noqa: E402
import guard as guard_mod  # noqa: E402

TASK = {
    "name": "t",
    "fields": {"participation_type": {"type": "enum",
               "values": ["participating", "non-participating", "capped"]}},
    "build_prompt": lambda i: i["document"],
}


class _SlowClient:
    """Sleeps briefly per call so concurrent workers genuinely overlap in time -- without this,
    a buggy 'parallel' implementation that's secretly sequential would still pass a naive
    call-count test."""

    def __init__(self, delay=0.01):
        self.delay = delay
        self.call_count = 0
        self._lock = threading.Lock()
        self.max_concurrent_seen = 0
        self._in_flight = 0

    def generate(self, prompt, temperature):
        with self._lock:
            self._in_flight += 1
            self.max_concurrent_seen = max(self.max_concurrent_seen, self._in_flight)
            self.call_count += 1
        time.sleep(self.delay)
        with self._lock:
            self._in_flight -= 1
        return '{"participation_type": "participating"}'


def _instances(n):
    return [({"id": f"i{k}", "document": "doc"}, {"participation_type": "participating"})
            for k in range(n)]


class TestParallelCorrectness(unittest.TestCase):
    def test_parallel_produces_one_record_per_requested_call(self):
        client = _SlowClient(delay=0.005)
        with tempfile.TemporaryDirectory() as td:
            runs, stats = harness.run_harness(
                client, TASK, _instances(5), n_runs=4, temperature=0.7,
                checkpoint_file=str(Path(td) / "runs.jsonl"), max_workers=8,
            )
        self.assertEqual(len(runs), 20)  # 5 instances x 4 runs
        self.assertEqual(client.call_count, 20)

    def test_parallel_actually_overlaps_in_time(self):
        client = _SlowClient(delay=0.03)
        with tempfile.TemporaryDirectory() as td:
            harness.run_harness(
                client, TASK, _instances(6), n_runs=1, temperature=0.7,
                checkpoint_file=str(Path(td) / "runs.jsonl"), max_workers=6,
            )
        # if truly parallel, several calls were in flight at once -- a secretly-sequential
        # implementation would never see max_concurrent_seen > 1.
        self.assertGreater(client.max_concurrent_seen, 1)

    def test_checkpoint_file_has_no_corrupted_lines_under_concurrency(self):
        client = _SlowClient(delay=0.005)
        with tempfile.TemporaryDirectory() as td:
            ckpt = Path(td) / "runs.jsonl"
            runs, _ = harness.run_harness(
                client, TASK, _instances(10), n_runs=3, temperature=0.7,
                checkpoint_file=str(ckpt), max_workers=10,
            )
            lines = ckpt.read_text().strip().split("\n")
            self.assertEqual(len(lines), 30)
            for line in lines:
                json.loads(line)  # raises if any line is interleaved/corrupted

    def test_resumed_items_are_skipped_and_not_recharged(self):
        client = _SlowClient(delay=0.005)
        g = guard_mod.BrakePedalGuard(max_steps=100)
        with tempfile.TemporaryDirectory() as td:
            ckpt = str(Path(td) / "runs.jsonl")
            harness.run_harness(client, TASK, _instances(3), n_runs=2, temperature=0.7,
                                 checkpoint_file=ckpt, max_workers=4)
            calls_after_first = client.call_count
            # second call with the SAME checkpoint should do nothing new -- everything's resumed.
            runs2, _ = harness.run_harness(client, TASK, _instances(3), n_runs=2, temperature=0.7,
                                            checkpoint_file=ckpt, max_workers=4, guard=g)
        self.assertEqual(len(runs2), 6)
        self.assertEqual(client.call_count, calls_after_first)  # no new calls made
        self.assertEqual(g.steps_taken, 0)  # guard never charged for resumed items


class TestParallelGuardNeverOvershoots(unittest.TestCase):
    """The load-bearing property: concurrent workers racing to check-then-increment the guard
    must never let total calls exceed max_steps, even with many workers hammering the same
    guard at once."""

    def test_guard_cap_holds_exactly_under_heavy_concurrency(self):
        client = _SlowClient(delay=0.01)
        g = guard_mod.BrakePedalGuard(max_steps=7)
        with tempfile.TemporaryDirectory() as td:
            runs, stats = harness.run_harness(
                client, TASK, _instances(20), n_runs=5, temperature=0.7,  # 100 possible calls
                checkpoint_file=str(Path(td) / "runs.jsonl"), guard=g,
                model_label="test-model", max_workers=16,
            )
        self.assertEqual(client.call_count, 7)
        self.assertEqual(len(runs), 7)
        self.assertEqual(g.steps_taken, 7)
        self.assertTrue(stats["guard_tripped"])

    def test_guard_cap_holds_across_repeated_runs(self):
        """Run the race many times (small N, high concurrency) -- a lock bug that only shows up
        occasionally under contention needs repetition to catch, not a single lucky pass."""
        for trial in range(15):
            client = _SlowClient(delay=0.002)
            g = guard_mod.BrakePedalGuard(max_steps=3)
            with tempfile.TemporaryDirectory() as td:
                harness.run_harness(
                    client, TASK, _instances(10), n_runs=5, temperature=0.7,
                    checkpoint_file=str(Path(td) / "runs.jsonl"), guard=g,
                    model_label="test-model", max_workers=10,
                )
            self.assertLessEqual(client.call_count, 3, f"trial {trial}: guard overshot")
            self.assertEqual(client.call_count, 3, f"trial {trial}: guard undershot")


if __name__ == "__main__":
    unittest.main()
