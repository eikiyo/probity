"""
Location: results/dump_verify.py  (shipped INTO the dump as verify_dump.py)
Purpose: Let a reviewer re-derive the paper's headline numbers FROM THE DUMP ALONE. This file is
         deliberately STANDALONE -- it imports nothing from probity and reimplements wobble and
         accuracy from the raw run records. That independence is the point: if it imported our
         aggregation code it would only prove our code agrees with itself, which is the exact
         self-referential trap this benchmark exists to expose.
Functions: load_runs(), load_oracle(), per_item(), score_model(), main()
Imports: argparse, gzip, json, pathlib, collections   (stdlib only)
Run: python3 verify_dump.py --dump . [--expect expected_numbers.json]
"""

import argparse
import gzip
import json
from collections import defaultdict
from pathlib import Path


def _open(path):
    return gzip.open(path, "rt", encoding="utf-8") if str(path).endswith(".gz") \
        else open(path, encoding="utf-8")


def _find(dump, stem):
    for name in (f"{stem}.jsonl.gz", f"{stem}.jsonl"):
        if (dump / name).exists():
            return dump / name
    raise SystemExit(f"missing {stem}.jsonl[.gz] in {dump}")


def load_oracle(dump):
    """
    (leaf, instance_idx) -> the ground truth SCORING compares against.

    Uses `truth_canonical`, not the raw oracle value. The benchmark canonicalizes both sides
    before comparing (a numeric answer written "100000000" in the oracle must match a parsed
    100000000), and the dump ships that canonical form as data precisely so this file does not
    have to reimplement normalization. Falls back to the raw value if the field is absent, so an
    older dump still verifies -- loudly wrong beats silently skipped.
    """
    truth, field_of = {}, {}
    with _open(_find(dump, "oracle")) as f:
        for line in f:
            r = json.loads(line)
            field_of[r["leaf"]] = r["field"]
            truth[(r["leaf"], r["instance_idx"])] = r.get("truth_canonical", r.get(r["field"]))
    return truth, field_of


def per_item(dump, field_of):
    """
    Collect the answers each (arm, model, leaf, item) produced across its runs.

    A run contributes an answer ONLY from `normalized`, and ONLY when that value is not None.
    Three rules, each of which was wrong in the first draft of this file and each of which
    inflated wobble:

      1. Read `normalized`, never fall back to `parsed`. `parsed` is the pre-canonical text, so
         "68000000" and 68000000.0 would count as two different answers from one model that in
         fact said the same thing twice.
      2. A `None` normalized value is NOT an answer -- it means the response could not be
         canonicalised into the field's type. Treating None as a value makes it a distinct
         "answer" that manufactures disagreement. This hit the weak 1B models hardest, since they
         emit the most uncanonicalisable output (gemma3-1b read 44.7% wobble instead of 42.6%).
      3. A run that errored or failed to parse contributes nothing at all.

    Rules 1 and 2 mirror engine/scorer._values_for exactly. That is not a shortcut around
    independence -- the METRIC below is still computed from scratch; this only fixes which cells
    of the raw log count as "the model gave an answer", which is a data-format question, not a
    scoring question.
    """
    answers = defaultdict(list)
    with _open(_find(dump, "runs")) as f:
        for line in f:
            r = json.loads(line)
            field = field_of.get(r["leaf"])
            norm = r.get("normalized")
            if not isinstance(norm, dict) or norm.get(field) is None:
                continue
            key = (r["arm"], r["model_label"], r["leaf"], r["instance_idx"])
            answers[key].append(norm[field])
    return answers


def score_model(answers, truth):
    """
    Independent reimplementation of the two headline metrics.

      wobble   = items where the model gave MORE THAN ONE distinct answer across its runs,
                 over items it answered at least once.
      accuracy = items whose MAJORITY answer equals ground truth, over the same denominator.

    An item with zero valid runs is UNMEASURED and is excluded from both -- never counted as
    stable, which would bias wobble downward.
    """
    agg = defaultdict(lambda: {"flipped": 0, "measured": 0, "correct": 0, "leaves": set()})
    for (arm, model, leaf, idx), vals in answers.items():
        if not vals:
            continue
        a = agg[(arm, model)]
        a["measured"] += 1
        a["leaves"].add(leaf)
        if len({json.dumps(v, sort_keys=True) for v in vals}) > 1:
            a["flipped"] += 1
        counts = defaultdict(int)
        for v in vals:
            counts[json.dumps(v, sort_keys=True)] += 1
        majority = json.loads(max(counts.items(), key=lambda kv: kv[1])[0])
        if majority == truth.get((leaf, idx)):
            a["correct"] += 1
    out = {}
    for (arm, model), a in agg.items():
        out[(arm, model)] = {
            "leaves": len(a["leaves"]), "items": a["measured"],
            "wobble_pct": 100 * a["flipped"] / a["measured"] if a["measured"] else None,
            "accuracy_pct": 100 * a["correct"] / a["measured"] if a["measured"] else None,
        }
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dump", default=".", help="directory holding runs/oracle jsonl[.gz]")
    p.add_argument("--expect", default=None,
                    help="JSON of {arm: {model: {wobble_pct, accuracy_pct}}} to CHECK against")
    p.add_argument("--tolerance", type=float, default=0.5,
                    help="allowed absolute difference in percentage points")
    args = p.parse_args()
    dump = Path(args.dump)

    truth, field_of = load_oracle(dump)
    scores = score_model(per_item(dump, field_of), truth)

    by_arm = defaultdict(dict)
    for (arm, model), s in scores.items():
        by_arm[arm][model] = s
    for arm in sorted(by_arm):
        print(f"\n=== arm {arm} ===")
        print(f"{'model':22s} {'leaves':>7s} {'items':>7s} {'wobble%':>9s} {'accuracy%':>10s}")
        for model in sorted(by_arm[arm], key=lambda m: by_arm[arm][m]["wobble_pct"] or 0):
            s = by_arm[arm][model]
            print(f"{model:22s} {s['leaves']:7d} {s['items']:7d} "
                  f"{s['wobble_pct']:9.2f} {s['accuracy_pct']:10.2f}")

    if not args.expect:
        print("\nNo --expect given: numbers printed, nothing asserted.")
        return
    expected = json.loads(Path(args.expect).read_text())
    bad = []
    for arm, models in expected.items():
        for model, want in models.items():
            got = by_arm.get(arm, {}).get(model)
            if got is None:
                bad.append(f"{arm}/{model}: MISSING from dump")
                continue
            for k in ("wobble_pct", "accuracy_pct"):
                if k in want and abs(got[k] - want[k]) > args.tolerance:
                    bad.append(f"{arm}/{model} {k}: dump={got[k]:.2f} paper={want[k]:.2f}")
    print()
    if bad:
        print(f"MISMATCH ({len(bad)}):")
        for b in bad:
            print(f"  {b}")
        raise SystemExit(1)
    print(f"PASS: every published number reproduced from the dump "
          f"within {args.tolerance} percentage points.")


if __name__ == "__main__":
    main()
