"""
Location: results/datadump.py
Purpose: Build the PEER-REVIEW data dump: every run record, every oracle item, every prompt, every
         scored cell and every reproducibility manifest, in open formats with checksums, plus a
         verifier a reviewer can run to re-derive the paper's headline numbers FROM THE DUMP alone.
         A reviewer must never have to trust our tables -- they recompute them.
Functions: iter_runs(), write_runs(), write_oracle(), write_prompts(), write_scored(),
           write_manifests(), write_coverage(), checksums(), build()
Calls: results/aggregate.py, engine/coverage.py, each leaf's task.build_prompt
Imports: argparse, csv, gzip, hashlib, importlib.util, json, sys, pathlib
Run: python3 results/datadump.py --out dist/probity-datadump
"""

import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "engine"))

import aggregate as ag   # noqa: E402
import coverage          # noqa: E402
import dump_docs         # noqa: E402
import normalize         # noqa: E402

N_RUNS = 20
# Arms to export: (suffix, temperature, arm name). The legacy arm is the published 0.7 sweep.
ARMS = [("", 0.7, "t07_legacy"), ("t01_", 0.1, "t01"), ("t07_", 0.7, "t07_rerun")]


def _open_w(path, gz):
    return gzip.open(path, "wt", encoding="utf-8") if gz else open(path, "w", encoding="utf-8")


def iter_runs(labels, arms=ARMS):
    """Every run record on disk, flattened and tagged with the four keys a reviewer needs to group
    by: leaf, model, arm, temperature. Reads the checkpoints -- the rawest artifact we hold."""
    for leaf in ag.built_leaves():
        leaf_dir = ROOT / leaf["leaf"]
        for suffix, temp, arm in arms:
            for label in labels:
                p = coverage.checkpoint_path(leaf_dir, label, suffix)
                if not p.exists():
                    continue
                with open(p, encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        rec = json.loads(line)
                        rec.pop("_key", None)     # tuple duplicate of instance_idx/run_idx
                        yield {"leaf": leaf_dir.name, "field": leaf["field"],
                                "family": leaf["family"], "model_label": label, "arm": arm,
                                "temperature": temp, **rec}


def write_runs(out, labels, gz=True):
    path = out / ("runs.jsonl.gz" if gz else "runs.jsonl")
    n, per_arm = 0, {}
    with _open_w(path, gz) as f:
        for rec in iter_runs(labels):
            f.write(json.dumps(rec, sort_keys=True) + "\n")
            n += 1
            per_arm[rec["arm"]] = per_arm.get(rec["arm"], 0) + 1
    return {"file": path.name, "rows": n, "rows_per_arm": per_arm}


def write_oracle(out, gz=True):
    """
    Ground truth, WITH the validating quote and difficulty. Shipping the quote is what lets a
    reviewer check that an answer is actually supported by the document, not just asserted.

    Also ships `truth_canonical` and `field_type`. SCORING never compares against the raw oracle
    value -- it compares against normalize.canonical(truth, type), so a numeric oracle written as
    the string "100000000" matches a model's parsed 100000000. A dump that shipped only the raw
    value would make an independent verifier undercount accuracy by 1-2 points and look like it
    had caught us in an error. Exposing the canonical form as DATA means a reviewer can both
    reproduce the number and inspect exactly what canonicalization did, without trusting our code.
    """
    path = out / ("oracle.jsonl.gz" if gz else "oracle.jsonl")
    n = 0
    with _open_w(path, gz) as f:
        for leaf in ag.built_leaves():
            d = ROOT / leaf["leaf"]
            task = _build_prompt_fn(d)
            field = leaf["field"]
            ftype = task["fields"][field].get("type", "enum")
            for i, line in enumerate(open(d / "oracle.jsonl", encoding="utf-8")):
                if not line.strip():
                    continue
                row = json.loads(line)
                f.write(json.dumps({"leaf": d.name, "field": field, "field_type": ftype,
                                     "family": leaf["family"], "instance_idx": i,
                                     "truth_canonical": normalize.canonical(row.get(field), ftype),
                                     **row}, sort_keys=True) + "\n")
                n += 1
    return {"file": path.name, "rows": n}


def _build_prompt_fn(leaf_dir):
    spec = importlib.util.spec_from_file_location(f"t_{leaf_dir.name}", leaf_dir / "task.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.TASK


def write_prompts(out, gz=True):
    """The EXACT prompt sent for every item, reconstructed by calling each leaf's own
    build_prompt on its own document -- not a description of the prompt, the prompt. Without this
    a reviewer cannot tell whether a model failed the task or the task was badly posed."""
    path = out / ("prompts.jsonl.gz" if gz else "prompts.jsonl")
    n = 0
    with _open_w(path, gz) as f:
        for leaf in ag.built_leaves():
            d = ROOT / leaf["leaf"]
            task = _build_prompt_fn(d)
            for i, line in enumerate(open(d / "oracle.jsonl", encoding="utf-8")):
                if not line.strip():
                    continue
                o = json.loads(line)
                doc = (d / "corpus" / "questions" / f"{o['id']}.txt").read_text(encoding="utf-8")
                prompt = task["build_prompt"]({"id": o["id"], "document": doc})
                f.write(json.dumps({"leaf": d.name, "instance_idx": i, "item_id": o["id"],
                                     "prompt": prompt, "document_chars": len(doc),
                                     "document_sha256": hashlib.sha256(doc.encode()).hexdigest()},
                                    sort_keys=True) + "\n")
                n += 1
    return {"file": path.name, "rows": n}


def write_scored(out, labels, gz=True):
    path = out / ("scored.jsonl.gz" if gz else "scored.jsonl")
    n = 0
    with _open_w(path, gz) as f:
        for leaf in ag.built_leaves():
            for suffix, temp, arm in ARMS:
                p = ROOT / leaf["leaf"] / coverage.scored_filename(None if not suffix else temp)
                if not p.exists():
                    continue
                blob = json.loads(p.read_text())
                for label in labels:
                    if label in blob:
                        f.write(json.dumps({"leaf": Path(leaf["leaf"]).name, "arm": arm,
                                             "model_label": label, **blob[label]},
                                            sort_keys=True) + "\n")
                        n += 1
    return {"file": path.name, "rows": n}


def write_manifests(out, labels, gz=True):
    """Reproducibility metadata per (leaf, model, arm): provider model id, routing layer, requested
    temperature, and what the provider reported back."""
    path = out / ("manifests.jsonl.gz" if gz else "manifests.jsonl")
    n = 0
    with _open_w(path, gz) as f:
        for leaf in ag.built_leaves():
            d = ROOT / leaf["leaf"]
            for suffix, _temp, arm in ARMS:
                for label in labels:
                    p = d / f"manifest_{suffix}{label}.json"
                    if not p.exists():
                        continue
                    f.write(json.dumps({"leaf": d.name, "arm": arm, "model_label": label,
                                         **json.loads(p.read_text())}, sort_keys=True) + "\n")
                    n += 1
    return {"file": path.name, "rows": n}


def write_coverage(out, labels):
    """The coverage matrix as CSV: for every (leaf, model, arm), calls OWED vs calls RECORDED.
    Owed is items x 20 from the oracle -- the spec -- so a reviewer can confirm completeness
    against something other than the data itself."""
    path = out / "coverage.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["leaf", "model_label", "arm", "temperature", "calls_owed",
                    "calls_recorded", "complete"])
        rows = 0
        for leaf in ag.built_leaves():
            d = ROOT / leaf["leaf"]
            for suffix, temp, arm in ARMS:
                for label in labels:
                    if not coverage.checkpoint_path(d, label, suffix).exists():
                        continue
                    c = coverage.cell_status(d, label, N_RUNS, suffix)
                    w.writerow([d.name, label, arm, temp, c["expected"], c["recorded"],
                                c["complete"]])
                    rows += 1
    return {"file": path.name, "rows": rows}


def checksums(out):
    """sha256 of every emitted file. A dump without checksums cannot be shown to be the dump that
    was reviewed."""
    lines = []
    for p in sorted(out.iterdir()):
        if p.name == "CHECKSUMS.sha256" or p.is_dir():
            continue
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        lines.append(f"{h.hexdigest()}  {p.name}")
    (out / "CHECKSUMS.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"file": "CHECKSUMS.sha256", "rows": len(lines)}


def complete_arms(labels):
    """
    Which arms are FROZEN and therefore safe to certify.

    A dump built over a running arm is a torn snapshot: runs.jsonl is read at one instant and the
    scored files at another, so the reviewer's verifier reports mismatches that are really just
    the sweep having advanced in between. Those look exactly like a real reproducibility failure,
    which is the worst possible thing to hand a reviewer. So an arm whose coverage is short is
    exported as DATA but excluded from `expected_numbers.json` -- we ship it, we just do not claim
    it reproduces yet.
    """
    ready, partial = [], []
    for suffix, temp, arm in ARMS:
        cells = [coverage.cell_status(ROOT / l["leaf"], lab, N_RUNS, suffix)
                 for l in ag.built_leaves() for lab in labels
                 if coverage.checkpoint_path(ROOT / l["leaf"], lab, suffix).exists()]
        if not cells:
            continue
        (ready if all(c["complete"] for c in cells) else partial).append(
            {"arm": arm, "temperature": temp, "suffix": suffix, "cells": len(cells),
             "short_cells": sum(1 for c in cells if not c["complete"])})
    return ready, partial


def build(out_dir, labels=None, gz=True):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    labels = labels or ag.canonical_lineup()
    ready, partial = complete_arms(labels)
    parts = [write_runs(out, labels, gz), write_oracle(out, gz), write_prompts(out, gz),
             write_scored(out, labels, gz), write_manifests(out, labels, gz),
             write_coverage(out, labels)]
    certify = [None if a["suffix"] == "" else a["temperature"] for a in ready]
    parts.append(dump_docs.write_expected(out, tuple(certify)))
    parts.append(dump_docs.write_readme(out))
    parts.append(dump_docs.copy_verifier(out))
    index = {"lineup": labels, "n_runs_per_item": N_RUNS,
             "arms_certified": ready, "arms_in_progress": partial,
             "files": parts}
    (out / "INDEX.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    parts.append(checksums(out))
    return index


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=str(ROOT / "dist" / "probity-datadump"))
    p.add_argument("--all-labels", action="store_true",
                    help="include every label on disk, not just the published 11")
    p.add_argument("--no-gzip", action="store_true")
    args = p.parse_args()
    labels = None
    if args.all_labels:
        seen = set()
        for leaf in ag.built_leaves():
            for f in (ROOT / leaf["leaf"]).glob("runs_*.jsonl"):
                seen.add(f.name[len("runs_"):-len(".jsonl")].replace("t01_", "").replace("t07_", ""))
        labels = sorted(seen)
    idx = build(args.out, labels, gz=not args.no_gzip)
    for a in idx["arms_certified"]:
        print(f"  CERTIFIED   arm {a['arm']}: {a['cells']} cells complete")
    for a in idx["arms_in_progress"]:
        print(f"  IN PROGRESS arm {a['arm']}: {a['short_cells']}/{a['cells']} cells short "
              f"-- exported as data, EXCLUDED from expected_numbers.json")
    for part in idx["files"]:
        extra = f"  {part.get('rows_per_arm')}" if part.get("rows_per_arm") else ""
        print(f"  {part['file']:24s} {part['rows']:>8,} rows{extra}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
