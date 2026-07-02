"""
Location: tests/test_manifest.py
Purpose: Blind tests for engine/manifest.py (DESIGN T8), derived from the DESIGN doc's
         gaps-sadpath T8 row -- "the repro manifest omits a field a re-run needs... CI re-runs
         from the manifest and must reproduce the score bit-for-bit; a missing/non-matching
         field fails the build" -- and oracle-independence invariant (2): "score is deterministic
         for a fixed model+seed+data-version."
Run: cd tests && python3 -m unittest test_manifest -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

import manifest as manifest_mod  # noqa: E402
import scorer                    # noqa: E402

TASK = {
    "name": "t",
    "fields": {"participation_type": {"type": "enum",
               "values": ["participating", "non-participating", "capped"]}},
    "build_prompt": lambda i: i["document"],
}
INSTANCES = [
    ({"id": "i0", "document": "doc0"}, {"participation_type": "participating"}),
    ({"id": "i1", "document": "doc1"}, {"participation_type": "non-participating"}),
]
RUNS = [
    {"_key": [0, 0], "instance_idx": 0, "run_idx": 0, "item_id": "i0",
     "parsed": {"participation_type": "participating"},
     "normalized": {"participation_type": "participating"}},
    {"_key": [1, 0], "instance_idx": 1, "run_idx": 0, "item_id": "i1",
     "parsed": {"participation_type": "non-participating"},
     "normalized": {"participation_type": "non-participating"}},
]


class TestManifestRequiredFields(unittest.TestCase):
    """A field a re-run needs but the manifest omits is a fail-the-build class of bug -- pin
    every field this contract requires to exist and be non-empty."""

    def test_has_every_required_field(self):
        m = manifest_mod.build_manifest(
            leaf_name="leaf_x", model_label="gemma3-1b", run_records=RUNS,
            task_name="t", n_runs=20, temperature=0.7,
        )
        for required in ("leaf", "model", "data_version", "n_runs", "temperature", "timestamp"):
            self.assertIn(required, m)
            self.assertTrue(m[required] not in (None, ""), f"{required} must not be empty")

    def test_timestamp_can_be_injected_for_reproducible_manifests(self):
        m = manifest_mod.build_manifest(
            leaf_name="leaf_x", model_label="gemma3-1b", run_records=RUNS,
            task_name="t", n_runs=20, temperature=0.7, timestamp="2026-07-02T00:00:00+00:00",
        )
        self.assertEqual(m["timestamp"], "2026-07-02T00:00:00+00:00")


class TestDataVersionIsAContentHash(unittest.TestCase):
    def test_same_run_records_give_the_same_data_version(self):
        m1 = manifest_mod.build_manifest("leaf_x", "gemma3-1b", RUNS, "t", 20, 0.7,
                                          timestamp="2026-07-02T00:00:00+00:00")
        m2 = manifest_mod.build_manifest("leaf_x", "gemma3-1b", RUNS, "t", 20, 0.7,
                                          timestamp="2026-07-02T00:00:00+00:00")
        self.assertEqual(m1["data_version"], m2["data_version"])

    def test_different_run_records_give_a_different_data_version(self):
        tampered = RUNS[:1] + [{**RUNS[1], "normalized": {"participation_type": "participating"}}]
        m1 = manifest_mod.build_manifest("leaf_x", "gemma3-1b", RUNS, "t", 20, 0.7)
        m2 = manifest_mod.build_manifest("leaf_x", "gemma3-1b", tampered, "t", 20, 0.7)
        self.assertNotEqual(m1["data_version"], m2["data_version"])


class TestVerifyManifestReproducesTheScore(unittest.TestCase):
    """The CI-facing contract: re-scoring from the manifest's referenced run data must
    reproduce the score bit-for-bit, and any drift must fail closed (return False), never
    silently pass."""

    def test_verify_passes_against_the_exact_same_run_records(self):
        m = manifest_mod.build_manifest("leaf_x", "gemma3-1b", RUNS, "t", 20, 0.7)
        self.assertTrue(manifest_mod.verify_manifest(m, RUNS))

    def test_verify_fails_closed_if_run_records_drift(self):
        m = manifest_mod.build_manifest("leaf_x", "gemma3-1b", RUNS, "t", 20, 0.7)
        drifted = RUNS[:1] + [{**RUNS[1], "normalized": {"participation_type": "capped"}}]
        self.assertFalse(manifest_mod.verify_manifest(m, drifted))

    def test_rescoring_from_manifest_referenced_data_matches_original_score(self):
        original_score = scorer.score_accuracy(TASK, INSTANCES, RUNS)
        m = manifest_mod.build_manifest("leaf_x", "gemma3-1b", RUNS, "t", 20, 0.7)
        self.assertTrue(manifest_mod.verify_manifest(m, RUNS))
        rescored = scorer.score_accuracy(TASK, INSTANCES, RUNS)
        self.assertEqual(original_score, rescored)


if __name__ == "__main__":
    unittest.main()
