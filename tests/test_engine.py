"""
Location: tests/test_engine.py
Purpose: Unit tests for the engine — normalizer, JSON parsing, and the accuracy + reliability
         scorers on crafted run sets (real assertions on concrete values, no toBeDefined).
Run: cd tests && python3 -m unittest -v
"""

import io
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

import normalize          # noqa: E402
import harness            # noqa: E402
import scorer             # noqa: E402
import models             # noqa: E402

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


class _FakeDeepSeekResponse:
    """Minimal stand-in for the `with urllib.request.urlopen(...) as resp:` context manager."""
    def __init__(self, body: dict):
        self._body = io.BytesIO(__import__("json").dumps(body).encode("utf-8"))

    def read(self):
        return self._body.read()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _http_error(code, reason="error"):
    return urllib.error.HTTPError(url="https://api.deepseek.com/v1/chat/completions",
                                   code=code, msg=reason, hdrs=None, fp=None)


class TestDeepSeekRetry(unittest.TestCase):
    """
    Purpose: cover the retry-on-transient-error behavior added to DeepSeekClient.generate() after
    the 2026-07-02 adversarial audit found 94% of that leaf's "parse failures" were actually raw
    HTTP 503s with zero retry, silently mismeasured as model unreliability. These tests mock
    urllib.request.urlopen so no real network call happens — they assert the RETRY DECISION logic
    itself (retry 5xx/429, don't retry 4xx, give up after _MAX_ATTEMPTS), per root CLAUDE.md
    §0.11 (new code ships with real tests in the same change, no toBeDefined-style padding).
    """

    def setUp(self):
        # Bypass the real env-var requirement in __init__ so tests don't need secrets/.env.
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key-not-real"}):
            self.client = models.DeepSeekClient()
        self.sleep_patcher = patch("models.time.sleep")  # don't actually wait during tests
        self.sleep_patcher.start()

    def tearDown(self):
        self.sleep_patcher.stop()

    def test_retries_on_503_then_succeeds(self):
        good = _FakeDeepSeekResponse({"choices": [{"message": {"content": '{"x": 1}'}}]})
        with patch("models.urllib.request.urlopen",
                    side_effect=[_http_error(503), _http_error(503), good]) as m:
            out = self.client.generate("prompt", temperature=0.7)
        self.assertEqual(out, '{"x": 1}')
        self.assertEqual(m.call_count, 3)  # 2 failed attempts + 1 success, within _MAX_ATTEMPTS

    def test_does_not_retry_on_400(self):
        with patch("models.urllib.request.urlopen", side_effect=_http_error(400, "Bad Request")) as m:
            with self.assertRaises(RuntimeError):
                self.client.generate("prompt", temperature=0.7)
        self.assertEqual(m.call_count, 1)  # no retry attempted for a non-retryable code

    def test_gives_up_after_max_attempts_on_repeated_503(self):
        with patch("models.urllib.request.urlopen",
                    side_effect=[_http_error(503), _http_error(503), _http_error(503)]) as m:
            with self.assertRaises(RuntimeError):
                self.client.generate("prompt", temperature=0.7)
        self.assertEqual(m.call_count, models.DeepSeekClient._MAX_ATTEMPTS)

    def test_rejects_zero_temperature_before_any_network_call(self):
        with patch("models.urllib.request.urlopen") as m:
            with self.assertRaises(ValueError):
                self.client.generate("prompt", temperature=0.0)
        m.assert_not_called()


if __name__ == "__main__":
    unittest.main()
