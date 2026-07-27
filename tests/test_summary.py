"""
Location: tests/test_summary.py
Purpose: Pin results/summary.py and render.py's lineup filter against the committed 0.7 arm. The
         load-bearing checks are: (1) the published README numbers are reproduced exactly, so the
         extraction out of render.py changed no result; (2) the table is 11 rows and can never
         again become 29 by admitting fine-tune lab labels; (3) an UNMEASURED rate renders as an
         em-dash, never as a confident 0%; and (4) an arm that was never run yields nothing rather
         than zeros.
Functions: TestReproducesPublishedReadme, TestLineupFilterIsLive, TestBadgeAndRateSadPaths,
           TestArmIsolation, TestDisplayMapsAreShared
Imports: json, sys, pytest, pathlib, summary, render, compare
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "results"))
sys.path.insert(0, str(ROOT / "engine"))

import aggregate as ag  # noqa: E402
import summary  # noqa: E402


class TestReproducesPublishedReadme:
    """Ground truth: the two tables committed in README.md for the 0.7 arm. If the extraction out
    of render.py had changed any reduction, these would move."""

    PUBLISHED_WOBBLE = {
        "gemma3-1b": 42, "deepseek-v4f": 6, "gemma4-31b-or": 3, "mistral-large-or": 3,
        "minimax-m2.5-or": 7, "llama3.3-70b-or": 3, "gemma3-1b-qat": 34,
        "gemini3-flash-or": 3, "haiku-4.5-direct": 3, "gpt-oss-120b-or": 6, "gpt5-mini-or": 6,
        "deepseek-v4p": 4,
    }
    PUBLISHED_ACCURACY = {
        "gemma3-1b": 58, "deepseek-v4f": 95, "gemma4-31b-or": 94, "mistral-large-or": 93,
        "minimax-m2.5-or": 94, "llama3.3-70b-or": 93, "gemma3-1b-qat": 61,
        "gemini3-flash-or": 94, "haiku-4.5-direct": 93, "gpt-oss-120b-or": 94, "gpt5-mini-or": 94,
        "deepseek-v4p": 95,
    }

    def test_every_published_wobble_and_accuracy_is_reproduced(self):
        rows = {r["model"]: r for r in summary.aggregate_by_model(None)}
        assert set(rows) == set(self.PUBLISHED_WOBBLE)
        for label, w in self.PUBLISHED_WOBBLE.items():
            assert round(rows[label]["wobble"]) == w, f"{label} wobble"
            assert round(rows[label]["accuracy"]) == self.PUBLISHED_ACCURACY[label], \
                f"{label} accuracy"

    def test_every_model_covers_all_sixty_leaves(self):
        for r in summary.aggregate_by_model(None):
            assert r["leaves"] == 60, f"{r['model']} covers {r['leaves']} leaves"

    def test_rows_are_in_declared_lineup_order_not_dict_order(self):
        """Dict-insertion order is whatever the scorer happened to write. A published table's row
        order is an editorial decision and must come from the declared lineup."""
        import aggregate as ag
        got = [r["model"] for r in summary.aggregate_by_model(None)]
        assert got == [m for m in ag.canonical_lineup() if m in set(got)]


class TestLineupFilterIsLive:
    """A filter that removes nothing is indistinguishable from no filter. These prove it FIRES --
    the positive control for the '29-row table' regression."""

    def test_finetune_labels_exist_on_disk_and_are_excluded(self):
        import render
        scored = json.loads((ROOT / "leaves" / "drag_along" / "scored.json").read_text())
        kept = render._models(scored)
        assert len(scored) > 40, "fixture must contain the fine-tune labels for this to mean anything"
        assert len(kept) == len(ag.canonical_lineup())
        assert set(kept) <= set(scored)
        excluded = set(scored) - set(kept)
        assert {"tuned-v4", "mlx-base-n20"} <= excluded

    def test_suite_table_has_exactly_one_row_per_lineup_model(self):
        """Derived from canonical_lineup() rather than a literal. The lineup SIZE is declared once,
        in test_aggregate's `len(lineup) == 12`, which is the gate that fires if a model is added
        silently; restating the number here only meant five files went red when deepseek-v4p was
        added legitimately, each needing a hand edit that could as easily have been a wrong one."""
        body = summary.suite_summary_table(None).splitlines()[2:]   # drop header + separator
        assert len(body) == len(ag.canonical_lineup())


class TestBadgeAndRateSadPaths:
    def test_unmeasured_renders_as_em_dash_not_zero_percent(self):
        """A 0% wobble badge from NO data is a confident lie in the safest-looking direction --
        exactly the failure this benchmark exists to measure in models."""
        assert summary.badge(None, True) == "—"
        assert summary.badge(None, False) == "—"
        assert "0%25" not in summary.badge(None, True)

    def test_rate_of_empty_denominator_is_none_not_zero(self):
        assert summary._rate(0, 0) is None
        assert summary._rate(3, 0) is None
        assert summary._rate(0, 10) == 0.0        # a real measured zero IS zero

    @pytest.mark.parametrize("pct,lower,color", [
        (3, True, "brightgreen"), (22, True, "yellow"), (42, True, "red"),
        (95, False, "brightgreen"), (61, False, "yellow"), (58, False, "red"),
    ])
    def test_badge_colors_match_the_published_thresholds(self, pct, lower, color):
        assert color in summary.badge(pct, lower)

    def test_unknown_label_falls_back_to_the_label_itself(self):
        assert summary.display_name("brand-new-model") == "brand-new-model"
        assert summary.display_size("brand-new-model") == "?"


class TestArmIsolation:
    def test_an_unrun_arm_produces_no_rows_rather_than_zeros(self):
        assert summary.aggregate_by_model(0.42) == []
        assert summary.aggregate_by_family(0.42) == []

    def test_an_unrun_arm_table_has_a_header_and_no_data_rows(self):
        assert len(summary.suite_summary_table(0.42).splitlines()) == 2


class TestDisplayMapsAreShared:
    def test_compare_and_render_resolve_a_name_identically(self):
        """The whole point of the extraction: two reports cannot call one model by two names."""
        import compare
        import render
        for label in summary.MODEL_DISPLAY:
            assert compare._name(label) == render.display_name(label) == summary.display_name(label)

    def test_every_lineup_member_has_a_display_entry(self):
        import aggregate as ag
        missing = [m for m in ag.canonical_lineup() if m not in summary.MODEL_DISPLAY]
        assert not missing, f"lineup members with no display name: {missing}"


class TestBadgeColorMatchesItsOwnLabel:
    """A badge's colour is thresholded on the value it PRINTS, never on invisible digits. Two
    badges showing the same number must always look the same."""

    @pytest.mark.parametrize("a,b", [(84.97, 85.02), (9.98, 10.4), (29.6, 30.4), (60.4, 59.8)])
    def test_values_that_print_the_same_get_the_same_colour(self, a, b):
        # Asserted, not guarded behind an `if`: a conditional here would let the case silently
        # skip and the test would pass while checking nothing.
        assert round(a) == round(b), "test case is malformed -- these do not print the same"
        for lower in (True, False):
            assert summary.badge(a, lower) == summary.badge(b, lower), \
                f"{a} and {b} both print {round(a)}% but rendered differently"

    def test_these_cases_straddle_a_real_threshold(self):
        """Positive control: the pairs above must sit ON a colour boundary, or the test proves
        nothing about thresholds -- any two equal-rounding numbers would pass."""
        raw_pairs = [(84.97, 85.02), (9.98, 10.4), (29.6, 30.4)]
        straddles = [(a, b) for a, b in raw_pairs
                     if (a < 85 <= b) or (a < 10 <= b) or (a < 30 <= b)]
        assert len(straddles) == 3

    def test_the_real_priced_equity_value_is_self_consistent(self):
        """84.97% -- the live value that exposed this. It prints 85% and must colour as 85%."""
        b = summary.badge(84.974747, False)
        assert "-85%25-" in b
        assert "yellow" in b, "85 is not > 85, so the >85 green rule must not fire"

    def test_a_value_above_the_threshold_still_goes_green(self):
        assert "brightgreen" in summary.badge(94.99, False)
        assert "brightgreen" in summary.badge(6.45, True)
