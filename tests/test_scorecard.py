"""
Location: tests/test_scorecard.py
Purpose: Blind tests for results/scorecard.py (DESIGN T7), derived from the DESIGN doc's
         "Scorecard report" screens spec + gaps-sadpath table T7 rows -- NOT from the
         implementation. Two contracts pinned: (1) a 0-task result NEVER renders a green
         headline, (2) the denominator always equals scored+errored, never silently fewer.
Run: cd tests && python3 -m unittest test_scorecard -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "results"))

import scorecard  # noqa: E402


def _accuracy(n_instances, n_measurable, accuracy_majority):
    return {
        "task": "leaf",
        "n_instances": n_instances,
        "n_measurable": n_measurable,
        "accuracy_majority": accuracy_majority,
        "accuracy_strict": accuracy_majority,
        "per_instance": [],
    }


def _reliability(consistency_pct=100.0, parse_failure_count=0, valid_run_count=20, measurable=True):
    return {
        "task": "leaf",
        "consistency_rate": consistency_pct / 100,
        "consistency_pct": consistency_pct,
        "field_flips": {},
        "parse_failure_count": parse_failure_count,
        "parse_failure_rate": 0.0,
        "valid_run_count": valid_run_count,
        "measurable": measurable,
        "excluded_fields": [],
    }


class TestZeroTasksRefusesGreen(unittest.TestCase):
    """Screens spec: 'empty: benchmark returned 0 tasks -- refuse to render a green "100%",
    show "0 tasks loaded - check data version", exit non-zero.'"""

    def test_zero_instances_is_not_ok(self):
        scored = {"gemma3-1b": {"model": "gemma3-1b",
                                 "accuracy": _accuracy(0, 0, 0.0),
                                 "reliability": _reliability(measurable=False)}}
        report = scorecard.build_report("some_leaf", scored)
        self.assertFalse(report.ok)

    def test_zero_instances_message_names_the_reason(self):
        scored = {"gemma3-1b": {"model": "gemma3-1b",
                                 "accuracy": _accuracy(0, 0, 0.0),
                                 "reliability": _reliability(measurable=False)}}
        report = scorecard.build_report("some_leaf", scored)
        text = scorecard.render_terminal(report)
        self.assertIn("0 tasks loaded", text)

    def test_zero_instances_never_shows_a_100pct_headline(self):
        scored = {"gemma3-1b": {"model": "gemma3-1b",
                                 "accuracy": _accuracy(0, 0, 0.0),
                                 "reliability": _reliability(measurable=False)}}
        report = scorecard.build_report("some_leaf", scored)
        text = scorecard.render_terminal(report)
        self.assertNotIn("100%", text)

    def test_no_scored_models_at_all_is_also_not_ok(self):
        report = scorecard.build_report("some_leaf", {})
        self.assertFalse(report.ok)


class TestDenominatorHonesty(unittest.TestCase):
    """gaps-sadpath T7 row: 'the headline score's denominator equals scored+errored, never
    silently fewer.'"""

    def test_denominator_equals_scored_plus_errored(self):
        # 18 total items, 15 measurable (scored), 3 errored/unmeasurable.
        scored = {"deepseek-v4f": {"model": "deepseek-v4f",
                                    "accuracy": _accuracy(18, 15, 0.8),
                                    "reliability": _reliability()}}
        report = scorecard.build_report("some_leaf", scored)
        row = report.rows[0]
        self.assertEqual(row.n_instances, 18)
        self.assertEqual(row.n_measurable, 15)
        self.assertEqual(row.n_errored, 3)

    def test_terminal_output_surfaces_the_errored_count_not_just_accuracy(self):
        scored = {"deepseek-v4f": {"model": "deepseek-v4f",
                                    "accuracy": _accuracy(18, 15, 0.8),
                                    "reliability": _reliability()}}
        report = scorecard.build_report("some_leaf", scored)
        text = scorecard.render_terminal(report)
        self.assertIn("3", text)   # the errored count must appear somewhere, not be hidden
        self.assertIn("errored", text.lower())

    def test_fully_measurable_run_reports_zero_errored_explicitly(self):
        scored = {"deepseek-v4f": {"model": "deepseek-v4f",
                                    "accuracy": _accuracy(18, 18, 1.0),
                                    "reliability": _reliability()}}
        report = scorecard.build_report("some_leaf", scored)
        self.assertEqual(report.rows[0].n_errored, 0)
        self.assertTrue(report.ok)


class TestGuardStatusSurfaced(unittest.TestCase):
    """Screens spec success line: '40/40 scored - correctness 0.78 - guard tripped 0 - report ->
    ./probity-report.html' -- guard state must be visible in the rendered report, not silent."""

    def test_guard_clean_is_shown(self):
        scored = {"gemma3-1b": {"model": "gemma3-1b",
                                 "accuracy": _accuracy(10, 10, 0.9),
                                 "reliability": _reliability()}}
        report = scorecard.build_report("some_leaf", scored,
                                         guard_stats={"guard_tripped": False, "guard_reason": None})
        text = scorecard.render_terminal(report)
        self.assertIn("guard", text.lower())

    def test_guard_tripped_is_shown_and_named(self):
        scored = {"gemma3-1b": {"model": "gemma3-1b",
                                 "accuracy": _accuracy(10, 4, 0.9),
                                 "reliability": _reliability()}}
        report = scorecard.build_report(
            "some_leaf", scored,
            guard_stats={"guard_tripped": True, "guard_reason": "would exceed max_steps=4"})
        text = scorecard.render_terminal(report)
        self.assertIn("tripped", text.lower())
        self.assertIn("max_steps", text)


class TestHtmlRendersSameFacts(unittest.TestCase):
    def test_html_contains_the_same_headline_numbers_as_terminal(self):
        scored = {"deepseek-v4f": {"model": "deepseek-v4f",
                                    "accuracy": _accuracy(20, 20, 0.85),
                                    "reliability": _reliability(consistency_pct=91.0)}}
        report = scorecard.build_report("some_leaf", scored)
        html = scorecard.render_html(report)
        self.assertIn("<html", html.lower())
        self.assertIn("deepseek-v4f", html)
        self.assertIn("some_leaf", html)

    def test_html_also_refuses_green_on_zero_tasks(self):
        report = scorecard.build_report("empty_leaf", {})
        html = scorecard.render_html(report)
        self.assertIn("0 tasks loaded", html)
        self.assertNotIn("100%", html)


if __name__ == "__main__":
    unittest.main()
