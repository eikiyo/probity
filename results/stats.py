"""
Location: results/stats.py
Purpose: Confidence intervals for Probity's rates. Pure stdlib (the repo has ZERO third-party
         deps and stays that way). Two estimators, both chosen because the rates here sit near 0
         (several models wobble at ~3%), where the normal approximation is invalid:
           - wilson_ci()      : single proportion (wobble / accuracy), Wilson (1927) score interval
           - paired_diff_ci() : difference of PAIRED proportions (0.7 vs 0.1 on the SAME items),
                                Tango (1998) asymptotic score interval
         Ported from the verified reference implementation in R's PropCIs (scoreci.mp), NOT
         reconstructed from memory -- per the search-first law, a load-bearing formula is read
         from a primary source or it is not written.
References: Wilson, E.B. (1927) JASA 22:209-212.
            Tango, T. (1998) Statistics in Medicine 17:891-908.
            Agresti, A. & Min, Y. (2005) Statistics in Medicine 24(5):729-740.
Functions: z_for(), wilson_ci(), paired_diff_ci(), _tango_core(), indistinguishable_groups(),
           fmt_pct_ci()
Imports: statistics, typing
"""

from statistics import NormalDist
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple


class Interval(NamedTuple):
    """point estimate + closed interval, all on the 0..1 scale (not percent)."""
    point: float
    lo: float
    hi: float

    def pct(self) -> "Interval":
        return Interval(self.point * 100, self.lo * 100, self.hi * 100)


def z_for(conf_level: float = 0.95) -> float:
    """Two-sided normal quantile. Uses stdlib NormalDist.inv_cdf rather than a hand-typed
    constant or a rational approximation copied from memory."""
    if not 0 < conf_level < 1:
        raise ValueError(f"conf_level must be in (0,1), got {conf_level}")
    return NormalDist().inv_cdf(1 - (1 - conf_level) / 2)


def wilson_ci(k: int, n: int, conf_level: float = 0.95) -> Interval:
    """
    What: Wilson score interval for a single binomial proportion k/n.
    Why NOT Wald: the Wald interval p +/- z*sqrt(p(1-p)/n) degenerates exactly where this
          benchmark lives. At k=0 it returns the zero-width interval [0,0] ("this model NEVER
          wobbles, with certainty"), which is a false claim from 470 observations, and near 3%
          it can dip below zero. Wilson is bounded in [0,1] by construction and stays sane at
          k=0 and k=n.
    Output: Interval(point=k/n, lo, hi). n=0 yields (0,0,1): no data means no knowledge, which
            is the honest fail-closed answer, not a confident zero.
    """
    if n < 0 or k < 0 or k > n:
        raise ValueError(f"need 0 <= k <= n, got k={k}, n={n}")
    if n == 0:
        return Interval(0.0, 0.0, 1.0)
    z = z_for(conf_level)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z / denom) * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return Interval(p, max(0.0, center - half), min(1.0, center + half))


def _tango_score(delta: float, b: int, c: int, n: int) -> float:
    """The score statistic at a hypothesised difference `delta`, with the constrained MLE q21
    solved from its quadratic. Faithful port of PropCIs::scoreci.mp's inner computation."""
    pa = 2 * n
    pb = -b - c + (2 * n - c + b) * delta
    pc = -b * delta * (1 - delta)
    q21 = ((pb * pb - 4 * pa * pc) ** 0.5 - pb) / (2 * pa)
    var = n * (2 * q21 + delta * (1 - delta))
    if var <= 0:
        return float("inf")
    return (c - b - n * delta) / (var ** 0.5)


def _tango_bound(b: int, c: int, n: int, z: float, upper: bool) -> float:
    """One bound, by the same bisection PropCIs uses: start at the point estimate and halve the
    step, keeping the last delta whose |score| is still inside z."""
    proot = (c - b) / n
    dp = (1 - proot) if upper else (1 + proot)
    bound = 1.0 if upper else -1.0
    for _ in range(50):
        dp *= 0.5
        trial = proot + dp if upper else proot - dp
        score = _tango_score(trial, b, c, n)
        if abs(score) < z:
            proot = trial
        bound = trial
        if dp < 1e-7 or abs(z - score) < 1e-6:
            break
    return bound


def _tango_core(b: int, c: int, n: int, conf_level: float) -> Tuple[float, float]:
    """Interval for (c-b)/n, matching PropCIs::scoreci.mp's argument convention exactly.
    Degenerate arms are pinned as in the reference: c==n -> upper 1, b==n -> lower -1."""
    z = z_for(conf_level)
    ul = 1.0 if c == n else _tango_bound(b, c, n, z, upper=True)
    ll = -1.0 if b == n else _tango_bound(b, c, n, z, upper=False)
    return ll, ul


def paired_diff_ci(only_first: int, only_second: int, n_pairs: int,
                    conf_level: float = 0.95) -> Interval:
    """
    What: CI for (p_first - p_second) where both proportions are measured on the SAME n_pairs
          items -- e.g. wobble at temp 0.7 vs temp 0.1 over the identical 470 oracle items.
    Args: only_first  = items positive in the FIRST arm only   (discordant pairs, b)
          only_second = items positive in the SECOND arm only  (discordant pairs, c)
          n_pairs     = total items (concordant pairs included; they carry no information about
                        the difference but do set the sample size)
    Why paired and not two independent Wilson intervals: the arms share items, so they are
          correlated; treating them as independent inflates the interval and understates a real
          effect. Only the DISCORDANT counts drive the difference, which is why the estimator
          takes b, c and n rather than the full 2x2 table.
    Sign: PropCIs::scoreci.mp(b, c, n) estimates (c-b)/n, so the arguments are swapped here to
          return (only_first - only_second)/n. Pinned by TestSignConvention.
    """
    if n_pairs <= 0:
        return Interval(0.0, -1.0, 1.0)
    if only_first + only_second > n_pairs:
        raise ValueError(f"discordant pairs {only_first}+{only_second} exceed n={n_pairs}")
    point = (only_first - only_second) / n_pairs
    lo, hi = _tango_core(b=only_second, c=only_first, n=n_pairs, conf_level=conf_level)
    return Interval(point, lo, hi)


def indistinguishable_groups(rows: Sequence[Tuple[str, Interval]]) -> List[List[str]]:
    """
    What: partitions labels into bands whose intervals overlap, so a table can say "these are
          statistically indistinguishable" instead of implying a ranking the data cannot support.
    Method: sort by point estimate, then single-linkage chaining -- a new band starts only when
          an interval does NOT overlap the running band's intersection. Interval overlap is not
          transitive, so this is chaining, and the caller must describe it as such: membership
          means "overlaps its neighbours in this band", not "every pair mutually overlaps".
    Output: list of bands, each a list of labels, ordered by point estimate.
    """
    if not rows:
        return []
    ordered = sorted(rows, key=lambda r: r[1].point)
    bands: List[List[str]] = [[ordered[0][0]]]
    cur_lo, cur_hi = ordered[0][1].lo, ordered[0][1].hi
    for label, iv in ordered[1:]:
        if iv.lo <= cur_hi and cur_lo <= iv.hi:
            bands[-1].append(label)
            cur_lo, cur_hi = max(cur_lo, iv.lo), min(cur_hi, iv.hi)
        else:
            bands.append([label])
            cur_lo, cur_hi = iv.lo, iv.hi
    return bands


def fmt_pct_ci(iv: Optional[Interval], decimals: int = 1, signed: bool = False) -> str:
    """"3.0% [1.8, 4.9]" for a table cell. None renders as an em-free dash, never as 0."""
    if iv is None:
        return "-"
    p = iv.pct()
    sign = "+" if (signed and p.point > 0) else ""
    return f"{sign}{p.point:.{decimals}f}% [{p.lo:.{decimals}f}, {p.hi:.{decimals}f}]"


def counts_from_rate(rate: float, n: int) -> int:
    """Recover the integer success count from a stored rate x item count. Probity's scored.json
    persists field_flips as a RATE, so the CI layer has to rebuild k. Rounds to nearest, which is
    exact whenever the rate really was k/n (it always is here)."""
    return int(round(rate * n))
