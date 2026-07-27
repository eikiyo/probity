"""
Location: results/compare.py
Purpose: The paper's temperature report. Renders, entirely from disk: the per-model suite table
         with Wilson CIs, the PAIRED 0.7-vs-0.1 delta table with Tango CIs, the per-category
         breakdown, the requested-vs-honoured temperature appendix, and the coverage matrix.
         Every number regenerates by re-running this; nothing is hand-entered.
Functions: suite_rows(), suite_table(), paired_rows(), paired_table(), category_table(),
           appendix_table(), coverage_section(), bands_note(), build_report(), main()
Calls: results/aggregate.py, results/stats.py, engine/coverage.py, engine/routing.py
Imports: argparse, json, sys, pathlib
Run: python3 results/compare.py --arms 0.7 0.1 --out results/RESULTS_T01.md
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "engine"))

import aggregate as ag   # noqa: E402
import coverage          # noqa: E402
import routing           # noqa: E402
import stats             # noqa: E402

# Display maps come from results/summary.py -- ONE definition shared with the README renderer, so
# the paired report and the published table can never call the same model by two different names.
from summary import (FAMILY_DISPLAY, MODEL_DISPLAY,   # noqa: E402,F401
                     display_name as _name, display_size)


def suite_rows(temperature):
    """Per-model wobble + accuracy with Wilson intervals, for one arm."""
    counts = ag.model_counts(temperature)
    rows = []
    for label, c in counts.items():
        rows.append({
            "label": label,
            "leaves": c["leaves"],
            "wobble": stats.wilson_ci(c["flipped"], c["measured"]),
            "accuracy": stats.wilson_ci(c["correct"], c["measurable"]),
            "n_items": c["measured"],
        })
    return sorted(rows, key=lambda r: r["wobble"].point)


def suite_table(temperature):
    lines = ["| Model | Size / routing | Tests | Items | **Wobble** ↓ (95% CI) | Accuracy (95% CI) |",
             "|---|---|---|---|---|---|"]
    for r in suite_rows(temperature):
        lines.append(f"| `{_name(r['label'])}` | {display_size(r['label'])} | {r['leaves']} | "
                      f"{r['n_items']} | "
                      f"**{stats.fmt_pct_ci(r['wobble'])}** | {stats.fmt_pct_ci(r['accuracy'])} |")
    return "\n".join(lines)


def incomplete_labels(temperature):
    """Labels whose cells are SHORT for this arm, mapped to how short. Empty for a frozen arm."""
    leaves = [ROOT / l["leaf"] for l in ag.built_leaves()]
    matrix = coverage.coverage_matrix(leaves, ag.canonical_lineup(), 20,
                                       coverage.artifact_suffix(temperature))
    return coverage.label_shortfall(matrix)


def excluded_from_pairing(temp_a, temp_b):
    """Which models may NOT be paired yet, and why. A model must be complete in BOTH arms.

    Without this, paired_rows emitted a row for a model that was mid-sweep -- gemini3-flash-or
    appeared with 336 pairs beside models with 470, formatted identically, with nothing marking it
    provisional. Generating the report at that moment would have put a number built on 36% of the
    items into the paper looking exactly as finished as the rest. n_pairs > 0 was never a
    completeness test; it only excluded a model with NO data at all.
    """
    short = {}
    for arm in (temp_a, temp_b):
        tag = coverage.arm_label(arm)
        for label, agg in incomplete_labels(arm).items():
            why = (f"{agg['short_cells']}/{agg['cells']} cells short, "
                   f"{agg['short_calls']} calls owed" if agg["started"]
                   else "not started in this arm")
            short.setdefault(label, []).append(f"{tag}: {why}")
    return short


def paired_rows(temp_a, temp_b):
    """Per-model paired delta (arm A minus arm B) over the items BOTH arms measured.

    Fails CLOSED on an unfrozen arm: a model short in either arm is excluded here and named by
    paired_table, never rendered as a finished row.
    """
    skip = excluded_from_pairing(temp_a, temp_b)
    rows = []
    for label in ag.canonical_lineup():
        if label in skip:
            continue
        p = ag.paired_counts(label, temp_a, temp_b)
        if p["n_pairs"] == 0:
            continue
        a_k = p["both"] + p["only_a"]
        b_k = p["both"] + p["only_b"]
        rows.append({
            "label": label,
            "n_pairs": p["n_pairs"],
            "dropped": p["dropped"],
            "wobble_a": stats.wilson_ci(a_k, p["n_pairs"]),
            "wobble_b": stats.wilson_ci(b_k, p["n_pairs"]),
            "delta": stats.paired_diff_ci(p["only_a"], p["only_b"], p["n_pairs"]),
            "discordant": (p["only_a"], p["only_b"]),
        })
    return sorted(rows, key=lambda r: r["delta"].point)


def paired_table(temp_a, temp_b):
    """
    The headline comparison. Delta is (arm A wobble - arm B wobble), so with A=0.7 and B=0.1 a
    NEGATIVE delta means 0.1 wobbled MORE, and a positive delta means lowering the temperature
    reduced wobble. An interval spanning 0 means the data does not establish a difference, and
    the Verdict column says exactly that rather than leaving a reader to infer it from a sign.
    """
    ta, tb = coverage.arm_label(temp_a), coverage.arm_label(temp_b)
    lines = [f"| Model | Pairs | Wobble @ {ta} | Wobble @ {tb} | **Δ ({ta} − {tb})** 95% CI | Verdict |",
             "|---|---|---|---|---|---|"]
    for r in paired_rows(temp_a, temp_b):
        d = r["delta"]
        if d.lo > 0:
            verdict = f"lower at {tb}"
        elif d.hi < 0:
            verdict = f"lower at {ta}"
        else:
            verdict = "no difference established"
        lines.append(f"| `{_name(r['label'])}` | {r['n_pairs']} | "
                      f"{stats.fmt_pct_ci(r['wobble_a'])} | {stats.fmt_pct_ci(r['wobble_b'])} | "
                      f"**{stats.fmt_pct_ci(d, signed=True)}** | {verdict} |")
    rows = paired_rows(temp_a, temp_b)
    dropped = sum(r["dropped"] for r in rows)
    if dropped:
        lines += ["", f"*{dropped} item-pairs excluded because one arm could not measure them "
                       "(no valid runs). They are excluded from BOTH arms of every pair, never "
                       "counted as stable in one and dropped from the other.*"]
    skip = excluded_from_pairing(temp_a, temp_b)
    if skip:
        lines += ["", "> **INCOMPLETE — this table is not the final result.** The following models "
                       "are still being measured and are EXCLUDED from the pairing above rather "
                       "than shown on partial data:", ""]
        lines += [f"> - `{_name(l)}` — {'; '.join(why)}" for l, why in sorted(skip.items())]
        lines += ["", "> Re-run this report once every arm is complete."]
    return "\n".join(lines)


def category_table(temperature):
    counts = ag.family_counts(temperature)
    lines = ["| Category | Tests | **Wobble** ↓ (95% CI) | Accuracy (95% CI) |", "|---|---|---|---|"]
    rows = [(FAMILY_DISPLAY.get(f, f), c) for f, c in counts.items()]
    for name, c in sorted(rows, key=lambda x: -x[1]["leaves"]):
        w = stats.wilson_ci(c["flipped"], c["measured"])
        a = stats.wilson_ci(c["correct"], c["measurable"])
        lines.append(f"| {name} | {c['leaves']} | **{stats.fmt_pct_ci(w)}** | "
                      f"{stats.fmt_pct_ci(a)} |")
    return "\n".join(lines)


def bands_note(temperature):
    """5d: where intervals overlap, say so instead of implying a ranking."""
    rows = [(r["label"], r["wobble"]) for r in suite_rows(temperature)]
    bands = stats.indistinguishable_groups(rows)
    out = ["Models whose 95% wobble intervals overlap are **statistically indistinguishable** at "
           "this sample size and are not ranked against each other:", ""]
    for i, band in enumerate(bands, 1):
        names = ", ".join(f"`{_name(b)}`" for b in band)
        out.append(f"{i}. {names}" + ("  *(single model, separated from the rest)*"
                                       if len(band) == 1 else ""))
    out += ["", "*Bands are formed by single-linkage chaining on interval overlap: membership "
                "means a model overlaps its neighbours in the band, not that every pair in the "
                "band mutually overlaps.*"]
    return "\n".join(out)


def appendix_table(temperature):
    """Requested vs honoured temperature + routing layer, read from what each cell recorded."""
    rows = []
    for label in ag.canonical_lineup():
        found = None
        for l in ag.built_leaves():
            scored = ag.leaf_scored(l["leaf"], temperature)
            if scored and label in scored:
                found = scored[label]
                break
        if not found:
            continue
        rows.append(routing.appendix_row(
            label, found.get("model"), found.get("routing", "unknown"),
            found.get("temperature_requested"), found.get("temperature_honoured")))
    return routing.render_appendix(rows)


def coverage_section(temperature):
    leaves = [ROOT / l["leaf"] for l in ag.built_leaves()]
    matrix = coverage.coverage_matrix(leaves, ag.canonical_lineup(), 20,
                                       coverage.artifact_suffix(temperature))
    return coverage.render_matrix(matrix, ag.canonical_lineup()), matrix


def build_report(temp_a, temp_b):
    ta, tb = coverage.arm_label(temp_a), coverage.arm_label(temp_b)
    cov_text, matrix = coverage_section(temp_b)
    holes = [c for c in matrix if not c["complete"]]
    out = [f"# Probity — arm {tb} results, paired against arm {ta}", "",
           "**Wobble** = the share of items where a model gave more than one answer across 20 "
           "identical runs. **Accuracy** = the share whose majority answer matched the "
           "human-validated truth. They are reported separately and never averaged.", "",
           "All intervals are 95%. Single rates use **Wilson score** intervals (not the normal "
           "approximation, which degenerates near 0 and several models sit at ~3%). Paired "
           "deltas use **Tango's score interval** for the difference of paired proportions, "
           "because both arms are measured on the same items and are therefore correlated.", "",
           f"## Suite summary @ {tb}", "", suite_table(temp_b), "",
           f"### Statistically indistinguishable groups @ {tb}", "",
           bands_note(temp_b), "",
           f"## Paired comparison: {ta} vs {tb}", "", paired_table(temp_a, temp_b), "",
           f"## By fundraising-document category @ {tb}", "", category_table(temp_b), "",
           "## Appendix: requested vs honoured temperature", "", appendix_table(temp_b), "",
           "## Coverage", "", cov_text, ""]
    if holes:
        out += [f"> **INCOMPLETE: {len(holes)} of {len(matrix)} cells are short.** Listed above in "
                 "bold. These are reported, not averaged over.", ""]
    return "\n".join(out)


def _arm(value):
    """`legacy` -> None, the unsuffixed published arm; anything else a temperature."""
    return None if str(value).lower() == "legacy" else float(value)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--arms", nargs=2, type=_arm, default=[None, 0.1],   # NOT ["legacy", ...]: argparse converts string defaults only
                    help="two arms, baseline first: a temperature, or 'legacy' for the published "
                         "unsuffixed 0.7 sweep. NOT interchangeable: `0.7` selects the t07 "
                         "namespace, which holds only the two LOCAL models re-measured on Kaggle, "
                         "so passing it here would pair 2 models and look like a finished report.")
    # NOT RESULTS_T01.md: render.py already owns that name for the 0.1 arm's per-leaf detail
    # (`RESULTS_{arm}.md`). Both defaulting to it meant whichever ran second silently replaced the
    # other's document with an unrelated one of the same name -- and it did, once.
    p.add_argument("--out", default=str(ROOT / "results" / "PAIRED_legacy_vs_t01.md"))
    args = p.parse_args()
    text = build_report(args.arms[0], args.arms[1])
    Path(args.out).write_text(text, encoding="utf-8")
    print(f"wrote {args.out} ({len(text.splitlines())} lines)")


if __name__ == "__main__":
    main()
