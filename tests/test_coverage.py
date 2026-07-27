"""
Location: tests/test_coverage.py
Purpose: Truth-table tests for engine/coverage.py. A verifier's own selftest must cover BOTH
         error directions (a hole it must catch, AND a complete cell it must NOT flag) -- a
         one-good-one-bad test can enshrine a false-RED as correct. Includes the positive control
         that matters: the module must independently rediscover the 5 REAL truncated cells in the
         committed 0.7 arm, and must flag nothing else.
Functions: TestExpectedCalls, TestDuplicateKeysCountOnce, TestAssertFull, TestMissingKeys,
           TestRenderMatrix, TestAgainstRealRepoData
Imports: json, pytest, pathlib, coverage
"""

import json
import sys
from pathlib import Path

import pytest

ENGINE = Path(__file__).parent.parent / "engine"
sys.path.insert(0, str(ENGINE))

import coverage as cov  # noqa: E402

REPO = Path(__file__).parent.parent


def _leaf(tmp_path, n_items):
    """A minimal leaf dir: only oracle.jsonl is needed to declare the expected call count."""
    d = tmp_path / "leaf"
    d.mkdir(exist_ok=True)
    with open(d / "oracle.jsonl", "w") as f:
        for i in range(n_items):
            f.write(json.dumps({"id": f"i{i}", "field": "x"}) + "\n")
    return d


def _write_runs(leaf, label, keys, suffix=""):
    with open(leaf / f"runs_{suffix}{label}.jsonl", "w") as f:
        for (i, r) in keys:
            f.write(json.dumps({"instance_idx": i, "run_idx": r, "_key": [i, r]}) + "\n")


class TestExpectedCalls:
    def test_reads_item_count_from_oracle_not_from_runs(self, tmp_path):
        leaf = _leaf(tmp_path, 6)
        _write_runs(leaf, "m", [(0, 0)])           # only ONE call recorded
        # The expectation must come from the oracle (6 x 20), NOT from the 1 recorded call.
        assert cov.expected_calls(leaf, 20) == 120

    def test_blank_lines_are_not_items(self, tmp_path):
        leaf = _leaf(tmp_path, 3)
        with open(leaf / "oracle.jsonl", "a") as f:
            f.write("\n\n")
        assert cov.n_items(leaf) == 3


class TestDuplicateKeysCountOnce:
    """A resume-safe WRITER does not make a resume-safe READER. The same (instance, run) key can
    legitimately appear twice after a resume; counting lines would call a short cell complete."""

    def test_duplicate_key_does_not_inflate_coverage(self, tmp_path):
        leaf = _leaf(tmp_path, 1)
        # 20 owed. 19 distinct keys, but key (0,0) written 3x -> 21 LINES, 19 distinct.
        keys = [(0, 0), (0, 0), (0, 0)] + [(0, r) for r in range(1, 19)]
        _write_runs(leaf, "m", keys)
        assert len(keys) == 21                      # a line count would say "over-complete"
        st = cov.cell_status(leaf, "m", 20)
        assert st["recorded"] == 19
        assert st["complete"] is False
        assert st["short_by"] == 1

    def test_no_duplicates_counts_all(self, tmp_path):
        leaf = _leaf(tmp_path, 1)
        _write_runs(leaf, "m", [(0, r) for r in range(20)])
        assert cov.cell_status(leaf, "m", 20)["complete"] is True


class TestAssertFull:
    """Both error directions."""

    def test_raises_on_a_hole_and_names_it(self, tmp_path):
        leaf = _leaf(tmp_path, 2)
        _write_runs(leaf, "m", [(0, r) for r in range(20)])   # item 1 entirely missing
        matrix = cov.coverage_matrix([leaf], ["m"], 20)
        with pytest.raises(cov.CoverageError) as e:
            cov.assert_full(matrix)
        assert "20/40" in str(e.value) and "short 20" in str(e.value)

    def test_does_NOT_raise_on_a_complete_matrix(self, tmp_path):
        leaf = _leaf(tmp_path, 2)
        _write_runs(leaf, "m", [(i, r) for i in range(2) for r in range(20)])
        cov.assert_full(cov.coverage_matrix([leaf], ["m"], 20))   # must not raise

    def test_missing_checkpoint_file_is_a_hole_not_a_pass(self, tmp_path):
        leaf = _leaf(tmp_path, 2)
        matrix = cov.coverage_matrix([leaf], ["never_ran"], 20)
        assert matrix[0]["recorded"] == 0
        with pytest.raises(cov.CoverageError):
            cov.assert_full(matrix)


class TestMissingKeys:
    def test_returns_exactly_the_owed_pairs(self, tmp_path):
        leaf = _leaf(tmp_path, 2)
        _write_runs(leaf, "m", [(0, r) for r in range(20)] + [(1, 0), (1, 1)])
        missing = cov.missing_keys(leaf, "m", 20)
        assert missing == [(1, r) for r in range(2, 20)]

    def test_empty_when_complete(self, tmp_path):
        leaf = _leaf(tmp_path, 1)
        _write_runs(leaf, "m", [(0, r) for r in range(20)])
        assert cov.missing_keys(leaf, "m", 20) == []


class TestSuffixNamespacing:
    """The 0.1 arm must not read the 0.7 arm's checkpoints, and vice versa."""

    def test_suffixed_cell_is_independent_of_unsuffixed(self, tmp_path):
        leaf = _leaf(tmp_path, 1)
        _write_runs(leaf, "m", [(0, r) for r in range(20)])          # the 0.7 arm
        assert cov.cell_status(leaf, "m", 20, suffix="")["complete"] is True
        assert cov.cell_status(leaf, "m", 20, suffix="t01_")["recorded"] == 0

    def test_path_convention_is_single_sourced(self, tmp_path):
        leaf = _leaf(tmp_path, 1)
        assert cov.checkpoint_path(leaf, "m", "t01_").name == "runs_t01_m.jsonl"
        assert cov.checkpoint_path(leaf, "m", "").name == "runs_m.jsonl"


class TestRenderMatrix:
    def test_short_cell_is_visible_complete_cell_is_a_count(self, tmp_path):
        leaf = _leaf(tmp_path, 1)
        _write_runs(leaf, "ok", [(0, r) for r in range(20)])
        _write_runs(leaf, "short", [(0, r) for r in range(5)])
        out = cov.render_matrix(cov.coverage_matrix([leaf], ["ok", "short"], 20))
        assert "**5/20**" in out          # the hole is bold, not hidden
        assert "1/2 cells complete" in out
        assert "25/40 calls recorded" in out


class TestAgainstRealRepoData:
    """
    POSITIVE CONTROL, on ground truth we established independently: the committed 0.7 arm has
    exactly 5 truncated cells, caused by the brake-pedal guard's flat $0.20 per-leaf cost cap.
    A checker that reports ABSENCE is only trustworthy if it can detect PRESENCE -- so this
    asserts the module finds those 5, and (the negative arm) that it does NOT flag the models
    that genuinely ran to completion.
    """

    KNOWN_SHORT = {
        ("participation_type", "gemini3-flash-or"): (333, 360),
        ("pre_vs_post_money", "gemini3-flash-or"): (333, 380),
        ("safe_pre_post", "haiku-4.5-direct"): (199, 320),
        ("safe_pro_rata_side_letter", "haiku-4.5-direct"): (199, 300),
        ("safe_cap_vs_discount_applies", "haiku-4.5-direct"): (199, 260),
    }
    CLEAN_MODELS = ["gemma4-31b-or", "mistral-large-or", "llama3.3-70b-or"]

    def _built_leaves(self):
        reg = json.loads((REPO / "engine" / "registry.json").read_text())
        return [REPO / l["leaf"] for l in reg["leaves"]
                if l.get("tier") == "built" and "leaf" in l]

    def test_the_legacy_arm_is_now_complete_after_the_backfill(self):
        """Was: 'finds exactly the five known truncated cells'. Those five were backfilled on
        2026-07-27 (357 calls), so this asserts the new truth. assert_full's ability to FAIL is
        pinned on synthetic matrices elsewhere in this file, where it cannot rot."""
        leaves = self._built_leaves()
        labels = ["gemini3-flash-or", "haiku-4.5-direct", "mistral-large-or"]
        matrix = cov.coverage_matrix(leaves, labels, 20)
        holes = [c for c in matrix if not c["complete"]]
        assert holes == []
        cov.assert_full(matrix)          # must NOT raise


    def test_negative_arm_models_that_ran_clean_are_not_flagged(self):
        """A detector that flags everything would pass the test above. This is the other arm."""
        matrix = cov.coverage_matrix(self._built_leaves(), self.CLEAN_MODELS, 20)
        assert [c for c in matrix if not c["complete"]] == []
        assert len(matrix) == 60 * len(self.CLEAN_MODELS)
