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


class TestOpenRouterClient(unittest.TestCase):
    """
    Purpose: OpenRouterClient shares its retry contract with DeepSeekClient via the extracted
    _post_chat_completion() helper (rule of two, 2026-07-03) -- these tests confirm the SAME
    retry-decision behavior holds for the shared code path, plus OpenRouter-specific request
    shape (model id is caller-supplied, not hardcoded; attribution headers present).
    """

    def setUp(self):
        with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key-not-real"}):
            self.client = models.OpenRouterClient(model="google/gemma-4-31b-it")
        self.sleep_patcher = patch("models.time.sleep")
        self.sleep_patcher.start()

    def tearDown(self):
        self.sleep_patcher.stop()

    def test_missing_api_key_fails_closed(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(RuntimeError):
                models.OpenRouterClient(model="google/gemma-4-31b-it")

    def test_model_id_is_caller_supplied_not_hardcoded(self):
        self.assertEqual(self.client.model, "google/gemma-4-31b-it")
        other = models.OpenRouterClient.__new__(models.OpenRouterClient)
        other.api_key = "k"
        other.base_url = "https://openrouter.ai/api/v1/chat/completions"
        other.model = "mistralai/mistral-large-2512"
        self.assertNotEqual(other.model, self.client.model)

    def test_retries_on_503_then_succeeds(self):
        good = _FakeDeepSeekResponse({"choices": [{"message": {"content": '{"x": 1}'}}]})
        with patch("models.urllib.request.urlopen",
                    side_effect=[_http_error(503), _http_error(503), good]) as m:
            out = self.client.generate("prompt", temperature=0.7)
        self.assertEqual(out, '{"x": 1}')
        self.assertEqual(m.call_count, 3)

    def test_does_not_retry_on_400(self):
        with patch("models.urllib.request.urlopen", side_effect=_http_error(400, "Bad Request")) as m:
            with self.assertRaises(RuntimeError):
                self.client.generate("prompt", temperature=0.7)
        self.assertEqual(m.call_count, 1)

    def test_gives_up_after_max_attempts_on_repeated_503(self):
        with patch("models.urllib.request.urlopen",
                    side_effect=[_http_error(503), _http_error(503), _http_error(503)]) as m:
            with self.assertRaises(RuntimeError):
                self.client.generate("prompt", temperature=0.7)
        self.assertEqual(m.call_count, models.OpenRouterClient._MAX_ATTEMPTS)

    def test_rejects_zero_temperature_before_any_network_call(self):
        with patch("models.urllib.request.urlopen") as m:
            with self.assertRaises(ValueError):
                self.client.generate("prompt", temperature=0.0)
        m.assert_not_called()

    def test_request_carries_the_configured_model_id(self):
        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["body"] = __import__("json").loads(req.data.decode("utf-8"))
            return _FakeDeepSeekResponse({"choices": [{"message": {"content": "{}"}}]})

        with patch("models.urllib.request.urlopen", side_effect=fake_urlopen):
            self.client.generate("prompt", temperature=0.7)
        self.assertEqual(captured["body"]["model"], "google/gemma-4-31b-it")


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


class TestCheckpointFreshness(unittest.TestCase):
    """
    Purpose: cover harness._validate_checkpoint_freshness(), added after the 2026-07-02
    adversarial audit found 3 leaves silently scoring fresh answers against the WRONG items
    because a stale checkpoint (from before oracle.jsonl was edited) was trusted purely by
    positional instance_idx. These are pure unit tests -- no network, no real files -- covering
    the two fail-closed conditions and the one legitimate resume case.
    """

    def setUp(self):
        # 2 "current" instances, ids A and B, at positions 0 and 1 respectively.
        self.instances = [({"id": "A", "document": "doc a"}, {}),
                           ({"id": "B", "document": "doc b"}, {})]

    def test_position_out_of_range_raises(self):
        # A checkpoint record for instance_idx=2 makes no sense when there are only 2 instances
        # (positions 0 and 1) -- this is the exact signature found in the real incident (oracle
        # shrank after the checkpoint was written).
        stale_runs = [{"instance_idx": 2, "run_idx": 0, "item_id": "C"}]
        with self.assertRaises(harness.StaleCheckpointError):
            harness._validate_checkpoint_freshness(stale_runs, self.instances, Path("fake.jsonl"))

    def test_item_id_mismatch_at_same_position_raises(self):
        # instance_idx=0 is in range, but the checkpoint says it was item "Z" -- the CURRENT
        # instance at position 0 is "A". This is a reorder that keeps the same item COUNT (so
        # the range check alone would miss it), caught only by the id check.
        stale_runs = [{"instance_idx": 0, "run_idx": 0, "item_id": "Z"}]
        with self.assertRaises(harness.StaleCheckpointError):
            harness._validate_checkpoint_freshness(stale_runs, self.instances, Path("fake.jsonl"))

    def test_matching_ids_and_in_range_positions_do_not_raise(self):
        # The legitimate case: a real resume where nothing changed. Must NOT raise, or every
        # leaf's normal checkpoint-resume flow would break.
        fresh_runs = [{"instance_idx": 0, "run_idx": 0, "item_id": "A"},
                      {"instance_idx": 1, "run_idx": 0, "item_id": "B"}]
        harness._validate_checkpoint_freshness(fresh_runs, self.instances, Path("fake.jsonl"))  # no raise

    def test_legacy_records_without_item_id_only_get_the_range_check(self):
        # Old checkpoint records (written before this fix) have no "item_id" key at all -- they
        # can still be range-checked (positional overflow), just not identity-checked. This must
        # not crash on a missing key, and must not raise when the position is in range.
        legacy_runs = [{"instance_idx": 0, "run_idx": 0}, {"instance_idx": 1, "run_idx": 0}]
        harness._validate_checkpoint_freshness(legacy_runs, self.instances, Path("fake.jsonl"))  # no raise


if __name__ == "__main__":
    unittest.main()
