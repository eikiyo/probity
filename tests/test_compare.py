"""
Location: tests/test_compare.py
Purpose: Pin results/compare.py, the file that renders the paper's headline claim. The highest-
         stakes check here is the SIGN CONVENTION: paired_diff_ci returns (arm A - arm B), so a
         positive delta means arm A wobbled MORE and reliability is better at arm B. A flip would
         invert the paper's conclusion while every table still looked plausible, so the direction
         is pinned against hand-built counts rather than trusted from reading the code.
Functions: TestVerdictSignConvention, TestSelfPairingIsANullResult, TestDroppedPairsAreDisclosed,
           TestCoverageSectionReportsHoles, TestReportRefusesToInventAnArm
Imports: sys, pytest, pathlib, compare, stats
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "results"))
sys.path.insert(0, str(ROOT / "engine"))

import compare  # noqa: E402
import stats    # noqa: E402


class TestVerdictSignConvention:
    """The direction of the headline claim. paired_diff_ci(only_a, only_b, n) estimates
    (only_a - only_b)/n, i.e. arm A's wobble minus arm B's."""

    def test_arm_a_wobbling_more_yields_a_positive_delta(self):
        # 60 items flipped ONLY in arm A, 2 only in arm B: A is clearly the wobblier arm.
        d = stats.paired_diff_ci(only_first=60, only_second=2, n_pairs=470)
        assert d.point > 0
        assert d.lo > 0, "with 60 vs 2 discordant pairs the interval must exclude zero"

    def test_arm_b_wobbling_more_yields_a_negative_delta(self):
        d = stats.paired_diff_ci(only_first=2, only_second=60, n_pairs=470)
        assert d.point < 0
        assert d.hi < 0

    def test_a_positive_delta_reads_as_lower_wobble_at_the_SECOND_arm(self):
        """With --arms 0.7 0.1, arm A is 0.7 and arm B is 0.1. If 0.7 wobbles more, the verdict
        must credit 0.1 -- that IS the paper's claim, and naming the wrong arm inverts it."""
        row = {"label": "haiku-4.5-direct", "n_pairs": 470, "dropped": 0,
               "wobble_a": stats.wilson_ci(70, 470), "wobble_b": stats.wilson_ci(12, 470),
               "delta": stats.paired_diff_ci(60, 2, 470), "discordant": (60, 2)}
        compare.paired_rows = lambda a, b: [row]
        try:
            table = compare.paired_table(0.7, 0.1)
        finally:
            import importlib
            importlib.reload(compare)
        assert "lower at t01" in table
        assert "lower at t07" not in table

    def test_an_interval_spanning_zero_says_so_explicitly(self):
        """Never let a reader infer a difference from a sign alone. 3 vs 2 discordant pairs is
        noise and must be reported as noise."""
        row = {"label": "gpt-oss-120b-or", "n_pairs": 470, "dropped": 0,
               "wobble_a": stats.wilson_ci(30, 470), "wobble_b": stats.wilson_ci(29, 470),
               "delta": stats.paired_diff_ci(3, 2, 470), "discordant": (3, 2)}
        compare.paired_rows = lambda a, b: [row]
        try:
            table = compare.paired_table(0.7, 0.1)
        finally:
            import importlib
            importlib.reload(compare)
        assert "no difference established" in table
        assert "lower at" not in table.replace("no difference established", "")


class TestSelfPairingIsANullResult:
    """An arm paired against ITSELF is the strongest available null control: the delta must be
    exactly zero and no model may be credited with a difference."""

    def test_every_model_reports_zero_delta_against_itself(self):
        rows = compare.paired_rows(None, None)
        assert len(rows) == 11
        for r in rows:
            assert r["discordant"] == (0, 0)
            assert r["delta"].point == 0.0
            assert r["delta"].lo <= 0 <= r["delta"].hi

    def test_self_paired_table_establishes_no_difference_anywhere(self):
        table = compare.paired_table(None, None)
        assert table.count("no difference established") == 11
        assert "lower at" not in table.replace("no difference established", "")


class TestDroppedPairsAreDisclosed:
    def test_the_guard_truncated_items_are_counted_and_stated_in_the_table(self):
        """16 haiku + 4 gemini items have no valid runs in the 0.7 arm. They must be excluded from
        BOTH arms of a pair and the exclusion must appear in the output -- a silently shrinking
        denominator is exactly how a self-referential coverage number gets built."""
        rows = {r["label"]: r for r in compare.paired_rows(None, None)}
        assert rows["haiku-4.5-direct"]["dropped"] == 16
        assert rows["haiku-4.5-direct"]["n_pairs"] == 454
        assert rows["gemini3-flash-or"]["dropped"] == 4
        assert rows["mistral-large-or"]["dropped"] == 0
        table = compare.paired_table(None, None)
        assert "item-pairs excluded" in table

    def test_a_model_with_no_holes_uses_the_full_item_set(self):
        rows = {r["label"]: r for r in compare.paired_rows(None, None)}
        assert rows["mistral-large-or"]["n_pairs"] == 470


class TestCoverageSectionReportsHoles:
    def test_the_legacy_arm_matrix_shows_its_five_short_cells_in_bold(self):
        text, matrix = compare.coverage_section(None)
        holes = [c for c in matrix if not c["complete"]]
        assert len(matrix) == 660, "60 leaves x 11 models"
        assert len(holes) == 5
        assert "**199/320**" in text          # safe_pre_post / haiku, rendered as a visible hole
        assert "655/660 cells complete" in text

    def test_a_complete_cell_is_not_rendered_as_a_bare_tick(self):
        """A tick cannot be distinguished from a tick-that-was-never-checked. Print the count."""
        text, _ = compare.coverage_section(None)
        assert "✅" not in text and "✓" not in text


class TestReportRefusesToInventAnArm:
    def test_an_unrun_arm_yields_no_model_rows(self):
        assert compare.suite_rows(0.42) == []
        assert compare.paired_rows(None, 0.42) == []

    def test_bands_note_on_a_real_arm_groups_overlapping_models(self):
        """The 5d deliverable: where intervals overlap, say the models are indistinguishable
        instead of implying the 3%/3%/6% ranking the data does not support."""
        note = compare.bands_note(None)
        assert "statistically indistinguishable" in note
        assert "single-linkage" in note
