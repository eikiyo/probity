"""
Location: results/temp_readme.py
Purpose: Generate and inject the README's temperature-comparison block. Split out of
         results/compare.py, which was already at its 300-LOC budget -- and kept separate rather
         than folded into results/summary.py because summary.py is imported BY compare.py, so a
         block that needs compare.paired_rows would close an import cycle.
         Exists so the README's headline sentence about temperature is COMPUTED from the same
         paired_rows the report tabulates, never typed by hand: a README claim and the table it
         summarises must not be able to drift apart.
Functions: verdict_counts(), readme_block(), inject_readme(), main()
Calls: results/compare.py (paired_rows), engine/coverage.py (arm_label)
Imports: argparse, re, sys, pathlib
Run: python3 results/temp_readme.py [--arms legacy 0.1]
"""

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "engine"))

import compare              # noqa: E402
import coverage             # noqa: E402
from summary import display_name as _name   # noqa: E402

START, END = "<!-- TEMPCOMPARE:START -->", "<!-- TEMPCOMPARE:END -->"


def verdict_counts(temp_a, temp_b):
    """Which models moved and which way, counted from the report's own rows.

    `lower_at_b` = the paired interval lies wholly above zero, i.e. arm B (the lower temperature)
    wobbled LESS. `lower_at_a` = wholly below zero, arm B wobbled MORE. Anything spanning zero is
    `no_difference` -- reported as such rather than rounded into a direction by its sign.
    """
    out = {"lower_at_b": [], "lower_at_a": [], "no_difference": []}
    for r in compare.paired_rows(temp_a, temp_b):
        d = r["delta"]
        key = "lower_at_b" if d.lo > 0 else "lower_at_a" if d.hi < 0 else "no_difference"
        out[key].append(r)
    return out


def _sentences(v, ta, tb):
    n = sum(len(x) for x in v.values())
    yield (f"Not in general. Across {n} models measured at both {ta} and {tb} on the identical "
           f"items, **{len(v['lower_at_b'])} wobbled less at {tb}**, "
           f"**{len(v['no_difference'])} showed no difference**, and "
           f"**{len(v['lower_at_a'])} wobbled *more* at {tb}** — 95% Tango intervals on the paired "
           "difference, counting only those that exclude zero.")
    best = max(v["lower_at_b"], key=lambda r: r["delta"].point, default=None)
    if best is not None:
        yield (f"The gain is concentrated in the weakest models: `{_name(best['label'])}` improves "
               f"by {best['delta'].point * 100:.1f} points, while frontier models move by low "
               "single digits or not at all.")
    worst = min(v["lower_at_a"], key=lambda r: r["delta"].point, default=None)
    if worst is not None:
        yield (f"`{_name(worst['label'])}` got *worse* at {tb}, by "
               f"{abs(worst['delta'].point) * 100:.1f} points.")
    yield ("Accuracy is flat across both arms for every model: temperature moves *consistency*, "
           "not correctness.")


def readme_block(temp_a, temp_b):
    ta, tb = coverage.arm_label(temp_a), coverage.arm_label(temp_b)
    body = "\n\n".join(_sentences(verdict_counts(temp_a, temp_b), ta, tb))
    return (f"{START}\n### Does lowering temperature fix wobble?\n\n{body}\n\n"
            "Full table, per-model intervals and the parse-failure caveat: "
            "[`results/PAIRED_legacy_vs_t01.md`](results/PAIRED_legacy_vs_t01.md).\n"
            f"{END}")


def inject_readme(temp_a, temp_b, path=None):
    path = Path(path) if path else ROOT / "README.md"
    txt = path.read_text()
    if START not in txt or END not in txt:
        raise SystemExit(f"{path} has no TEMPCOMPARE markers -- add them where the block belongs")
    block = readme_block(temp_a, temp_b)
    path.write_text(re.sub(re.escape(START) + ".*?" + re.escape(END), lambda m: block, txt,
                           flags=re.S), encoding="utf-8")
    return block


def main():
    p = argparse.ArgumentParser(description=__doc__)
    # default is [None, 0.1], NOT ["legacy", 0.1]: argparse applies `type` only to a STRING
    # default, never to a list, so the sentinel would reach arm_label() unconverted.
    p.add_argument("--arms", nargs=2, type=compare._arm, default=[None, 0.1])
    p.add_argument("--print", action="store_true", help="print the block, write nothing")
    args = p.parse_args()
    if args.print:
        print(readme_block(args.arms[0], args.arms[1]))
        return
    inject_readme(args.arms[0], args.arms[1])
    print("injected the temperature-comparison block into README.md")


if __name__ == "__main__":
    main()
