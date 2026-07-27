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
        assert len(rows) == len(compare.ag.canonical_lineup())
        for r in rows:
            assert r["discordant"] == (0, 0)
            assert r["delta"].point == 0.0
            assert r["delta"].lo <= 0 <= r["delta"].hi

    def test_self_paired_table_establishes_no_difference_anywhere(self):
        table = compare.paired_table(None, None)
        assert (table.count("no difference established")
                == len(compare.ag.canonical_lineup()))
        assert "lower at" not in table.replace("no difference established", "")


class TestDroppedPairsAreDisclosed:
    def test_unmeasurable_items_are_counted_and_stated_in_the_table(self):
        """The 16 haiku + 4 gemini items lost to guard TRUNCATION were backfilled 2026-07-27.
        What remains dropped are items whose every one of 20 runs was unparseable. Those must
        still be excluded from BOTH arms of a pair and disclosed in the output -- a silently
        shrinking denominator is how a self-referential coverage number gets built."""
        rows = {r["label"]: r for r in compare.paired_rows(None, None)}
        assert rows["haiku-4.5-direct"]["dropped"] == 2
        assert rows["haiku-4.5-direct"]["n_pairs"] == 468
        assert rows["gemini3-flash-or"]["dropped"] == 1
        assert rows["mistral-large-or"]["dropped"] == 0
        table = compare.paired_table(None, None)
        assert "item-pairs excluded" in table

    def test_a_model_that_answered_everything_uses_the_full_item_set(self):
        rows = {r["label"]: r for r in compare.paired_rows(None, None)}
        assert rows["mistral-large-or"]["n_pairs"] == 470


class TestCoverageSectionReportsHoles:
    def test_the_legacy_arm_matrix_is_complete_after_the_backfill(self):
        """Was: 'shows its five short cells in bold'. Those five were backfilled 2026-07-27. The
        BOLD-a-hole rendering is still pinned directly by test_render_matrix_bolds_a_short_cell
        on a synthetic matrix, so losing this instance does not lose the capability."""
        text, matrix = compare.coverage_section(None)
        measured = [c for c in matrix if c["recorded"] > 0]
        holes = [c for c in measured if not c["complete"]]
        assert len(matrix) == 60 * len(compare.ag.canonical_lineup())
        assert holes == [], "a cell with data must have ALL its data"
        # deepseek-v4p joined the lineup 2026-07-27 and completed its legacy sweep the same day,
        # so every lineup model now has data. A model with 0 recorded cells would be ABSENT, which
        # is a different state from SHORT and must never read as a hole.
        assert len(measured) == 60 * len(compare.ag.canonical_lineup())

    def test_render_matrix_bolds_a_short_cell(self):
        """The capability the test above used to cover, on synthetic data that cannot rot."""
        import coverage as cov
        matrix = [{"leaf": "l1", "label": "m", "expected": 320, "recorded": 199,
                   "complete": False, "short_by": 121}]
        assert "**199/320**" in cov.render_matrix(matrix, ["m"])

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


class TestPairingFailsClosedOnAnUnfrozenArm:
    """The defect this class exists for, found 2026-07-27 while the 0.1 arm was mid-sweep:
    paired_rows emitted a row for gemini3-flash-or built on 336 item-pairs, beside models with
    470, formatted identically and with nothing marking it provisional. `n_pairs > 0` was never a
    completeness test -- it only excluded a model with NO data at all. Generating the report at
    that moment would have put a number computed over 36% of the items into the paper looking
    exactly as finished as the rest."""

    def _matrix(self, recorded_by_label):
        return [{"leaf": f"leaf{i}", "label": lab, "expected": 180, "recorded": rec,
                 "complete": rec == 180, "short_by": 180 - rec}
                for lab, rec in recorded_by_label.items() for i in range(2)]

    def test_a_partially_measured_label_is_reported_short(self):
        short = compare.coverage.label_shortfall(self._matrix({"whole": 180, "partial": 37}))
        assert "whole" not in short, "a complete label must not be reported as short"
        assert short["partial"]["short_cells"] == 2
        assert short["partial"]["short_calls"] == 286
        assert short["partial"]["started"] is True

    def test_an_unstarted_label_is_distinguished_from_a_partial_one(self):
        """Both are excluded, but they are different facts and the report says which."""
        short = compare.coverage.label_shortfall(self._matrix({"unstarted": 0, "partial": 37}))
        assert short["unstarted"]["started"] is False
        assert short["partial"]["started"] is True

    def test_a_frozen_arm_excludes_nobody(self):
        """Positive control. A gate that excluded every model would satisfy every test above
        while making the report permanently empty -- this is what proves it discriminates."""
        assert compare.coverage.label_shortfall(self._matrix({"a": 180, "b": 180})) == {}

    def test_the_legacy_arm_pairs_every_model_against_itself(self):
        """The legacy arm IS frozen, so the gate must let all of it through. If this ever goes
        red, the gate has started excluding finished work."""
        assert compare.excluded_from_pairing(None, None) == {}
        assert len(compare.paired_rows(None, None)) == len(compare.ag.canonical_lineup())

    def test_an_excluded_model_is_named_in_the_table_not_silently_dropped(self, monkeypatch):
        """A silent exclusion is worse than a partial row: the reader cannot tell a model was
        left out at all, and a shrinking lineup reads as a complete one."""
        monkeypatch.setattr(compare, "excluded_from_pairing",
                            lambda a, b: {"minimax-m2.5-or": ["t01: 59/60 cells short"]})
        table = compare.paired_table(None, None)
        assert "INCOMPLETE" in table
        assert "minimax-m2.5" in table
        assert "59/60 cells short" in table

    def test_no_incomplete_banner_when_every_arm_is_frozen(self):
        assert "INCOMPLETE" not in compare.paired_table(None, None)


class TestNoInternalSentinelReachesTheReport:
    """`None` is the internal name for the legacy arm. It used to be interpolated raw into the
    report's own headings -- `paired against None`, `## Paired comparison: None vs 0.1` -- where a
    reviewer cannot tell whether it means the legacy arm, a missing value, or a bug. build_report
    even computed the correct label on its first line and then never used it."""

    def test_no_heading_contains_the_none_sentinel(self):
        report = compare.build_report(None, 0.1)
        offenders = [l for l in report.splitlines() if "None" in l]
        assert offenders == [], f"internal sentinel reached the report: {offenders[:3]}"

    def test_the_legacy_arm_is_named_with_its_temperature(self):
        """'legacy' alone does not tell a reader it is the 0.7 sweep."""
        assert compare.coverage.arm_label(None) == "legacy (0.7)"
        assert "0.7" in compare.build_report(None, 0.1).splitlines()[0]

    def test_an_explicit_arm_carries_both_tag_and_temperature(self):
        assert compare.coverage.arm_label(0.1) == "t01 (0.1)"

    def test_both_arms_are_named_in_the_title(self):
        title = compare.build_report(None, 0.1).splitlines()[0]
        assert "legacy (0.7)" in title and "t01 (0.1)" in title
