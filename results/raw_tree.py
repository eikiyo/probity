"""
Location: results/raw_tree.py
Purpose: Emit the peer-review corpus as a BROWSABLE folder tree (Eikiyo 2026-07-27), one file per
         ITEM holding all 20 runs -- so the reviewer opens ONE file and sees the four things that
         make a claim checkable side by side: the question we asked, the answer that was supposed
         to come back, the answers we actually got, and whether they agreed with each other.
         Wobble is a property OF the 20 runs of one item, so putting them in one file puts the
         evidence and the claim in the same place; one-file-per-run scattered it across 20.
         Reuses datadump.iter_runs() as the single source of run records, so this tree and the
         flat .jsonl.gz dump can never disagree about what was measured.
Functions: model_dir(), arm_dir(), question_for(), oracle_index(), item_payload(), build_tree()
Calls: results/datadump.py (iter_runs, _build_prompt_fn), results/aggregate.py, results/summary.py
Imports: argparse, collections, hashlib, itertools, json, sys, pathlib
Run: python3 results/raw_tree.py --out Raw [--models a,b] [--sample N]
"""

import argparse
import collections
import hashlib
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "engine"))

import aggregate as ag      # noqa: E402
import datadump             # noqa: E402
import normalize            # noqa: E402
import summary              # noqa: E402

# Two arms share temperature 0.7: the published Mac-measured baseline, and the Kaggle re-run of the
# two LOCAL models on a T4. Separate folders -- they are different measurements of the same
# setting, and one folder would silently overwrite one with the other.
ARM_DIRS = {"t07_legacy": "0.7", "t01": "0.1", "t07_rerun": "0.7-rerun-kaggle"}


def model_dir(label):
    """Public model name, not the internal label: a reviewer reads `claude-haiku-4.5`."""
    return summary.display_name(label).replace("/", "_")


def arm_dir(arm):
    return ARM_DIRS.get(arm, arm)


def question_for(leaf_dir, task, oracle_row):
    """THE EXACT PROMPT SENT, rebuilt by calling the leaf's own build_prompt on its own document --
    not a description of the prompt. Without it a reviewer cannot tell a model that failed the
    task from a task that was badly posed."""
    doc = (leaf_dir / "corpus" / "questions" / f"{oracle_row['id']}.txt").read_text(encoding="utf-8")
    return {"prompt_sent": task["build_prompt"]({"id": oracle_row["id"], "document": doc}),
            "document_chars": len(doc),
            "document_sha256": hashlib.sha256(doc.encode()).hexdigest()}


def oracle_index():
    """(leaf, instance_idx) -> everything known about the item before any model saw it."""
    idx = {}
    for leaf in ag.built_leaves():
        d = ROOT / leaf["leaf"]
        task = datadump._build_prompt_fn(d)
        field = leaf["field"]
        ftype = task["fields"][field].get("type", "enum")
        for i, line in enumerate(open(d / "oracle.jsonl", encoding="utf-8")):
            if not line.strip():
                continue
            row = json.loads(line)
            idx[(d.name, i)] = {
                "field": field, "field_type": ftype, "item_id": row.get("id"),
                "expected_answer": row.get(field),
                "expected_answer_canonical": normalize.canonical(row.get(field), ftype),
                "supporting_quote": row.get("anchor"), "difficulty": row.get("difficulty"),
                "company": row.get("company"),
                "question": question_for(d, task, row)}
    return idx


def _answers(runs, field):
    """The 20 replies, in run order. `normalized` is what scoring compares; a run with no
    normalized value contributed NO answer and must not read as agreement."""
    out = []
    for r in sorted(runs, key=lambda x: x.get("run_idx") or 0):
        norm = r.get("normalized") if isinstance(r.get("normalized"), dict) else None
        out.append({"run": (r.get("run_idx") or 0) + 1,
                    "answer_received": (norm or {}).get(field),
                    "answer_raw_parsed": (r.get("parsed") or {}).get(field)
                    if isinstance(r.get("parsed"), dict) else None,
                    "error": r.get("error")})
    return out


def _summary(answers, expected_canonical):
    """Did the model give the same answer every time, and was it the right one? These are the two
    columns of the paper, computed here from the very rows printed above them."""
    given = [a["answer_received"] for a in answers if a["answer_received"] is not None]
    distinct = sorted({json.dumps(g, sort_keys=True, default=str) for g in given})
    majority = collections.Counter(map(str, given)).most_common(1)
    return {"n_runs": len(answers), "n_valid": len(given),
            "n_distinct_answers": len(distinct),
            "wobbled": len(distinct) > 1,
            "majority_answer": majority[0][0] if majority else None,
            "majority_matches_expected":
                (majority[0][0] == str(expected_canonical)) if majority else None}


def item_payload(model_label, arm, temp, leaf, inst, meta, runs):
    field = meta["field"]
    answers = _answers(runs, field)
    return {
        "model": summary.display_name(model_label), "model_label": model_label,
        "temperature": temp, "arm": arm,
        "leaf": leaf, "field": field, "family": meta.get("family"),
        "instance_idx": inst, "item_id": meta["item_id"],
        "company": meta.get("company"), "difficulty": meta.get("difficulty"),
        "1_question_asked": meta["question"],
        "2_expected_answer": {"value": meta["expected_answer"],
                              "canonical": meta["expected_answer_canonical"],
                              "field_type": meta["field_type"],
                              "supporting_quote": meta.get("supporting_quote")},
        "3_answers_received": answers,
        "4_summary": _summary(answers, meta["expected_answer_canonical"]),
    }


def build_tree(out, labels, sample=None):
    """One JSON file per (model, arm, leaf, item). iter_runs yields leaf-major then arm then
    label, so consecutive records share a group and can be flushed without holding the corpus."""
    out.mkdir(parents=True, exist_ok=True)
    oracle = oracle_index()
    counts, n = collections.Counter(), 0
    keyf = lambda r: (r["model_label"], r["arm"], r["temperature"], r["leaf"])  # noqa: E731
    for (label, arm, temp, leaf), group in itertools.groupby(datadump.iter_runs(labels), keyf):
        by_item = collections.defaultdict(list)
        for rec in group:
            by_item[rec.get("instance_idx") or 0].append(rec)
        leaf_path = out / model_dir(label) / arm_dir(arm) / leaf
        leaf_path.mkdir(parents=True, exist_ok=True)
        for inst, runs in sorted(by_item.items()):
            if sample and inst >= sample:
                continue
            meta = oracle.get((leaf, inst))
            if meta is None:            # a run with no oracle row is unscoreable; skip, do not fake
                continue
            payload = item_payload(label, arm, temp, leaf, inst, meta, runs)
            (leaf_path / f"item-{inst:03d}.json").write_text(
                json.dumps(payload, indent=1, sort_keys=True, default=str), encoding="utf-8")
            counts[f"{model_dir(label)}/{arm_dir(arm)}"] += 1
            n += 1
    return {"item_files": n, "per_model_arm": dict(sorted(counts.items()))}


README = """# Probity — per-item records

One file per (model, temperature, test, item). Open any single file and you can check any single
claim, because all four pieces are in it:

    1_question_asked      the EXACT prompt sent to the model, document text included
    2_expected_answer     the human-validated answer, with the quote from the filing that supports it
    3_answers_received    all 20 replies, in order
    4_summary             did the 20 replies agree, and was the majority right

Layout:

    <model>/<temperature>/<test>/item-NNN.json

`0.7` is the published baseline. `0.1` is the paired re-measurement. `0.7-rerun-kaggle` is a
re-measurement of the two LOCAL models on a Kaggle T4, kept separate from `0.7` because it is a
different measurement of the same setting, not a replacement for it.

**Wobble**, the paper's headline metric, is `4_summary.wobbled`: the model gave more than one
distinct answer across 20 identical calls. You can verify it by reading `3_answers_received` --
the claim and its evidence are in the same file, deliberately.

## One limitation, stated plainly

`answer_received` is the answer we PARSED from the model's reply, not the model's verbatim text.
The harness kept raw text only when parsing FAILED. So you can check what we understood the model
to say, and you can check it against the truth -- but you cannot audit our parsing of a successful
reply, because the surrounding text was not retained.

This applies identically to the 0.7 baseline and the 0.1 arm, so both halves of the comparison are
affected the same way and the DIFFERENCE between them -- which is what the paper claims -- is
unaffected. We would rather state this than have you find it by grepping.

A run with `answer_received: null` contributed NO answer (transport error or unparseable reply).
It is excluded from both arms of any comparison, never counted as agreement.
"""


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default="Raw")
    p.add_argument("--models", default=None, help="comma-separated labels; default = full lineup")
    p.add_argument("--sample", type=int, default=None, help="only the first N items per leaf")
    args = p.parse_args()
    labels = args.models.split(",") if args.models else ag.canonical_lineup()
    out = Path(args.out)
    man = build_tree(out, labels, args.sample)
    (out / "README.md").write_text(README, encoding="utf-8")
    (out / "MANIFEST.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    print(f"wrote {man['item_files']} item files under {summary.rel(out)}")
    for k, v in man["per_model_arm"].items():
        print(f"  {k:44s} {v:6d}")


if __name__ == "__main__":
    main()
