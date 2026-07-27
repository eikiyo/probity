"""
Location: tests/test_stats.py
Purpose: Validate results/stats.py against INDEPENDENT oracles, not against itself. Three kinds:
         (1) an algebraic oracle -- a Wilson bound must satisfy the score equation it is defined
             as the root of, which is a different computation from the closed form used to produce
             it; (2) invariants a correct estimator must obey regardless of implementation
             (symmetry, sign, containment, monotonicity in n); (3) a COVERAGE SIMULATION against a
             known true difference, which is the only check that would actually catch a mis-ported
             formula. Seeded, so it is deterministic.
Functions: TestWilsonAgainstScoreEquation, TestWilsonEdges, TestWilsonCoverage, TestSignConvention,
           TestPairedInvariants, TestPairedCoverage, TestIndistinguishableGroups, TestFormatting
Imports: random, sys, pytest, pathlib, stats
"""

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "results"))

import stats  # noqa: E402

Z95 = stats.z_for(0.95)


class TestWilsonAgainstScoreEquation:
    """
    The Wilson interval is DEFINED as the set of p where |p_hat - p| / sqrt(p(1-p)/n) <= z.
    stats.wilson_ci computes it by closed form. Recomputing that score at the returned bounds is
    an independent route to the same truth: if the closed form were mis-transcribed, the score at
    the bound would not come back as z.
    """

    @pytest.mark.parametrize("k,n", [(1, 470), (14, 470), (27, 470), (235, 470), (3, 20), (19, 20)])
    def test_score_at_each_bound_equals_z(self, k, n):
        iv = stats.wilson_ci(k, n, 0.95)
        p_hat = k / n
        for bound in (iv.lo, iv.hi):
            score = abs(p_hat - bound) / ((bound * (1 - bound) / n) ** 0.5)
            assert score == pytest.approx(Z95, abs=1e-9)

    def test_point_estimate_lies_inside(self):
        iv = stats.wilson_ci(14, 470)
        assert iv.lo < iv.point < iv.hi


class TestWilsonEdges:
    def test_zero_successes_is_not_a_zero_width_interval(self):
        """The Wald interval would return [0, 0] here: 'this model never wobbles, with
        certainty', from 470 observations. That is the false claim Wilson exists to avoid."""
        iv = stats.wilson_ci(0, 470)
        assert iv.lo == 0.0
        assert iv.hi > 0.0
        wald_half = Z95 * ((0.0 * 1.0 / 470) ** 0.5)
        assert wald_half == 0.0 and iv.hi > wald_half   # mutation proof vs the wrong estimator

    def test_all_successes_is_bounded_at_one(self):
        """Wilson's upper bound at k=n is exactly 1 in exact arithmetic; in floats it lands one
        ulp below, so this asserts approximately-1 rather than a bit pattern."""
        iv = stats.wilson_ci(470, 470)
        assert iv.hi == pytest.approx(1.0, abs=1e-12)
        assert iv.lo < 1.0

    def test_never_escapes_unit_interval(self):
        for k in (0, 1, 2, 469, 470):
            iv = stats.wilson_ci(k, 470)
            assert 0.0 <= iv.lo <= iv.hi <= 1.0

    def test_no_data_returns_full_ignorance_not_confident_zero(self):
        assert stats.wilson_ci(0, 0) == stats.Interval(0.0, 0.0, 1.0)

    def test_more_data_narrows_the_interval(self):
        wide = stats.wilson_ci(3, 100)
        narrow = stats.wilson_ci(30, 1000)          # same rate, 10x the data
        assert (narrow.hi - narrow.lo) < (wide.hi - wide.lo)

    def test_rejects_impossible_counts(self):
        with pytest.raises(ValueError):
            stats.wilson_ci(11, 10)


class TestWilsonCoverage:
    """A 95% interval must contain the truth about 95% of the time. Seeded."""

    def test_covers_at_about_95_percent_at_a_probity_like_rate(self):
        rng = random.Random(20260727)
        p_true, n, sims, hits = 0.03, 470, 2000, 0
        for _ in range(sims):
            k = sum(1 for _ in range(n) if rng.random() < p_true)
            iv = stats.wilson_ci(k, n)
            hits += iv.lo <= p_true <= iv.hi
        assert 0.93 <= hits / sims <= 0.98, f"coverage {hits/sims:.3f}"


class TestSignConvention:
    """paired_diff_ci(only_first, only_second, n) must estimate p_first - p_second. Getting this
    backwards would silently flip the sign of every delta in the paper."""

    def test_first_arm_higher_gives_a_positive_point(self):
        iv = stats.paired_diff_ci(only_first=30, only_second=10, n_pairs=470)
        assert iv.point == pytest.approx(20 / 470)
        assert iv.lo > 0                      # a real, positive difference

    def test_second_arm_higher_gives_a_negative_point(self):
        iv = stats.paired_diff_ci(only_first=10, only_second=30, n_pairs=470)
        assert iv.point == pytest.approx(-20 / 470)
        assert iv.hi < 0


class TestPairedInvariants:
    def test_swapping_arms_mirrors_the_interval(self):
        a = stats.paired_diff_ci(30, 10, 470)
        b = stats.paired_diff_ci(10, 30, 470)
        assert a.point == pytest.approx(-b.point)
        assert a.lo == pytest.approx(-b.hi, abs=1e-6)
        assert a.hi == pytest.approx(-b.lo, abs=1e-6)

    def test_equal_discordance_straddles_zero_symmetrically(self):
        iv = stats.paired_diff_ci(15, 15, 470)
        assert iv.point == 0.0
        assert iv.lo < 0 < iv.hi
        assert iv.lo == pytest.approx(-iv.hi, abs=1e-6)

    def test_no_discordant_pairs_is_a_zero_difference_with_a_real_interval(self):
        """Every item behaved identically in both arms. The difference is exactly 0, but the
        interval must still have width: 470 agreeing items do not prove the rates are equal."""
        iv = stats.paired_diff_ci(0, 0, 470)
        assert iv.point == 0.0
        assert iv.lo < 0 < iv.hi

    def test_point_estimate_always_inside_its_interval(self):
        for b, c in [(0, 0), (1, 0), (0, 1), (5, 12), (60, 3), (40, 20)]:
            iv = stats.paired_diff_ci(b, c, 470)
            assert iv.lo <= iv.point <= iv.hi, f"{b},{c}"

    def test_bounds_stay_in_minus_one_to_one(self):
        for b, c in [(0, 160), (160, 0), (80, 80)]:
            iv = stats.paired_diff_ci(b, c, 160)
            assert -1.0 <= iv.lo <= iv.hi <= 1.0

    def test_more_pairs_narrows_the_interval(self):
        wide = stats.paired_diff_ci(4, 2, 47)
        narrow = stats.paired_diff_ci(40, 20, 470)   # same rates, 10x the data
        assert (narrow.hi - narrow.lo) < (wide.hi - wide.lo)

    def test_rejects_discordance_exceeding_n(self):
        with pytest.raises(ValueError):
            stats.paired_diff_ci(300, 300, 470)


class TestPairedCoverage:
    """
    The real validation. Simulate paired items from a KNOWN joint distribution, so the true
    difference is known exactly, and check the interval covers it about 95% of the time. A
    mis-ported score formula shows up here as coverage well away from 0.95, which none of the
    invariant tests above would catch.
    """

    def _coverage(self, p11, p10, p01, n_pairs, sims, seed):
        rng = random.Random(seed)
        p00 = 1 - p11 - p10 - p01
        cells, weights = ("11", "10", "01", "00"), (p11, p10, p01, p00)
        truth = p10 - p01
        hits = 0
        for _ in range(sims):
            draw = rng.choices(cells, weights=weights, k=n_pairs)
            b = draw.count("10")
            c = draw.count("01")
            iv = stats.paired_diff_ci(b, c, n_pairs)
            hits += iv.lo <= truth <= iv.hi
        return hits / sims

    def test_covers_a_known_difference_at_probity_scale(self):
        # wobble 3.0% at 0.7 vs 1.5% at 0.1, strongly correlated -- the shape we expect.
        cov = self._coverage(p11=0.010, p10=0.020, p01=0.005,
                              n_pairs=470, sims=1200, seed=11)
        assert 0.92 <= cov <= 0.995, f"paired coverage {cov:.3f}"

    def test_covers_a_true_zero_difference(self):
        cov = self._coverage(p11=0.015, p10=0.015, p01=0.015,
                              n_pairs=470, sims=1200, seed=12)
        assert 0.92 <= cov <= 0.995, f"paired coverage under H0 {cov:.3f}"


class TestIndistinguishableGroups:
    def test_overlapping_models_form_one_band(self):
        rows = [("a", stats.wilson_ci(14, 470)), ("b", stats.wilson_ci(15, 470)),
                ("c", stats.wilson_ci(13, 470))]
        assert stats.indistinguishable_groups(rows) == [["c", "a", "b"]]

    def test_a_clearly_worse_model_splits_off(self):
        rows = [("small", stats.wilson_ci(199, 470)), ("big", stats.wilson_ci(14, 470))]
        bands = stats.indistinguishable_groups(rows)
        assert bands == [["big"], ["small"]]

    def test_bands_are_ordered_by_point_estimate(self):
        rows = [("hi", stats.wilson_ci(199, 470)), ("lo", stats.wilson_ci(14, 470)),
                ("mid", stats.wilson_ci(100, 470))]
        assert [b[0] for b in stats.indistinguishable_groups(rows)] == ["lo", "mid", "hi"]

    def test_empty_input(self):
        assert stats.indistinguishable_groups([]) == []


class TestFormatting:
    def test_renders_a_table_cell(self):
        """Expected values hand-derived from the Wilson definition, NOT read back off the
        implementation: p=14/470=0.0297872, z=1.959964, denom=1+z^2/n=1.0081734,
        center=0.0335992, half=(z/denom)*sqrt(p(1-p)/n + z^2/4n^2)=0.0157742
        -> lo=0.0178250 (1.8%), hi=0.0493734 (4.9%)."""
        assert stats.fmt_pct_ci(stats.wilson_ci(14, 470)) == "3.0% [1.8, 4.9]"

    def test_none_is_a_dash_not_a_zero(self):
        assert stats.fmt_pct_ci(None) == "-"

    def test_signed_positive_gets_a_plus(self):
        out = stats.fmt_pct_ci(stats.paired_diff_ci(30, 10, 470), signed=True)
        assert out.startswith("+")

    def test_counts_from_rate_roundtrips(self):
        assert stats.counts_from_rate(14 / 470, 470) == 14
        assert stats.counts_from_rate(0.0, 470) == 0
