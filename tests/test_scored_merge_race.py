"""
Location: tests/test_scored_merge_race.py
Purpose: Prove engine/runner._merge_scored survives CONCURRENT writers. The leaf's scored file is
         keyed by leaf, not by model, so every model that runs on a leaf read-modify-writes the
         same file. Running an OpenRouter track beside a direct-API track (safe on rate limits,
         different providers) makes that a real race, and a lost write is INVISIBLE: the file stays
         valid JSON and simply lacks a model. Includes a positive control that demonstrates the
         UNLOCKED implementation actually does lose data, so the locked test is not vacuous.
Functions: TestConcurrentMergeKeepsEveryModel, TestUnlockedControlLosesData
Imports: json, sys, pathlib, concurrent.futures, runner
"""

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "engine"))

import runner  # noqa: E402

N_WRITERS = 12


class TestConcurrentMergeKeepsEveryModel:
    def test_twelve_concurrent_writers_all_survive(self, tmp_path):
        out = tmp_path / "scored_t01.json"

        def write(i):
            runner._merge_scored(out, {f"model-{i}": {"accuracy": i}})

        with ThreadPoolExecutor(max_workers=N_WRITERS) as ex:
            list(ex.map(write, range(N_WRITERS)))

        got = json.loads(out.read_text())
        assert set(got) == {f"model-{i}" for i in range(N_WRITERS)}, \
            f"lost {N_WRITERS - len(got)} of {N_WRITERS} models"

    def test_an_existing_model_is_preserved_not_clobbered(self, tmp_path):
        out = tmp_path / "scored_t01.json"
        out.write_text(json.dumps({"pre-existing": {"accuracy": 1}}))
        runner._merge_scored(out, {"new-model": {"accuracy": 2}})
        got = json.loads(out.read_text())
        assert set(got) == {"pre-existing", "new-model"}

    def test_re_running_the_same_model_overwrites_its_own_entry_only(self, tmp_path):
        out = tmp_path / "scored_t01.json"
        runner._merge_scored(out, {"m": {"accuracy": 1}, "other": {"accuracy": 9}})
        runner._merge_scored(out, {"m": {"accuracy": 2}})
        got = json.loads(out.read_text())
        assert got["m"]["accuracy"] == 2
        assert got["other"]["accuracy"] == 9


class TestUnlockedControlLosesData:
    """Positive control. A concurrency test that passes because the timing never collided proves
    nothing, so replay the OLD unlocked logic and show it DOES drop writes under the same load."""

    @staticmethod
    def _unlocked_merge(out_path, new_results):
        prev = json.loads(out_path.read_text()) if out_path.exists() else {}
        time.sleep(0.002)                      # widen the window the real code also has
        prev.update(new_results)
        out_path.write_text(json.dumps(prev, indent=1), encoding="utf-8")

    def test_the_unlocked_version_really_does_lose_models(self, tmp_path):
        out = tmp_path / "scored_t01.json"
        out.write_text("{}")

        def write(i):
            self._unlocked_merge(out, {f"model-{i}": {"accuracy": i}})

        with ThreadPoolExecutor(max_workers=N_WRITERS) as ex:
            list(ex.map(write, range(N_WRITERS)))

        got = json.loads(out.read_text())
        assert len(got) < N_WRITERS, (
            "the control did not reproduce the race, so the locked test above proves nothing "
            "about locking -- widen the sleep or raise N_WRITERS")


class TestAtomicWrite:
    def test_replaces_content_and_leaves_no_temp_file(self, tmp_path):
        p = tmp_path / "scorecard.html"
        p.write_text("old")
        runner._atomic_write(p, "new")
        assert p.read_text() == "new"
        assert list(tmp_path.iterdir()) == [p], "a .tmp file was left behind"

    def test_creates_the_file_when_absent(self, tmp_path):
        p = tmp_path / "scorecard.html"
        runner._atomic_write(p, "fresh")
        assert p.read_text() == "fresh"
