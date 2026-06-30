"""
Location: tests/test_engine.py
Purpose: Unit tests for the engine — normalizer, JSON parsing, and the accuracy + reliability
         scorers on crafted run sets (real assertions on concrete values, no toBeDefined).
Run: cd tests && python3 -m unittest -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

import normalize          # noqa: E402
import harness            # noqa: E402
import scorer             # noqa: E402

TASK = {
    "name": "t",
    "fields": {"participation_type": {"type": "enum",
               "values": ["participating", "non-participating", "capped"]}},
    "build_prompt": lambda i: i["document"],
}


def _runs(inst_idx, answers):
    """Build run records for one instance from a list of raw answers."""
    out = []
    for k, a in enumerate(answers):
        out.append({"_key": [inst_idx, k], "instance_idx": inst_idx, "run_idx": k,
                    "parsed": {"participation_type": a},
                    "normalized": {"participation_type": normalize.canonical(a, "enum")}})
    return out


class TestNormalize(unittest.TestCase):
    def test_enum_casefold(self):
        self.assertEqual(normalize.canonical("Non-Participating", "enum"), "non-participating")

    def test_number_strips_currency(self):
        self.assertEqual(normalize.canonical("$1,250,000", "number"), 1250000.0)

    def test_bool_words(self):
        self.assertTrue(normalize.canonical("Yes", "bool"))
        self.assertIsNone(normalize.canonical("maybe", "bool"))


class TestParse(unittest.TestCase):
    def test_code_fence(self):
        out = harness._parse_json_response('```json\n{"participation_type": "capped"}\n```')
        self.assertEqual(out, {"participation_type": "capped"})

    def test_empty_is_failure(self):
        self.assertIsNone(harness._parse_json_response("   "))


class TestAccuracy(unittest.TestCase):
    def test_majority_correct_strict_wrong(self):
        # 3 of 5 right -> majority correct, NOT strict-correct
        instances = [({"document": "x"}, {"participation_type": "participating"})]
        runs = _runs(0, ["participating", "participating", "participating", "capped", "non-participating"])
        a = scorer.score_accuracy(TASK, instances, runs)
        self.assertEqual(a["n_measurable"], 1)
        self.assertEqual(a["accuracy_majority"], 1.0)
        self.assertEqual(a["accuracy_strict"], 0.0)

    def test_majority_wrong(self):
        instances = [({"document": "x"}, {"participation_type": "non-participating"})]
        runs = _runs(0, ["capped", "capped", "capped", "non-participating", "non-participating"])
        a = scorer.score_accuracy(TASK, instances, runs)
        self.assertEqual(a["accuracy_majority"], 0.0)  # mode=capped != non-participating

    def test_reliability_independent_of_truth(self):
        instances = [({"document": "x"}, {"participation_type": "participating"})]
        runs = _runs(0, ["capped"] * 5)  # perfectly consistent, but WRONG
        r = scorer.score_runs(TASK, instances, runs)
        a = scorer.score_accuracy(TASK, instances, runs)
        self.assertEqual(r["consistency_pct"], 100.0)  # reliable
        self.assertEqual(a["accuracy_majority"], 0.0)  # but inaccurate


if __name__ == "__main__":
    unittest.main()
