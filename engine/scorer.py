"""
Location: engine/scorer.py
Purpose: Score RELIABILITY (run-to-run consistency, label-free) AND ACCURACY (vs a validated
         oracle answer). Both reported; never collapsed. Task-dict API.
Functions: score_runs() [reliability], score_accuracy() [vs oracle], helpers.
Calls: normalize.canonical()
Imports: collections, typing, normalize
"""

from collections import Counter
from typing import List, Dict, Any, Tuple
import normalize

_SCORABLE = ("number", "enum", "bool", "date", "string")


def _runs_by_instance(runs: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
    out: Dict[int, List[Dict[str, Any]]] = {}
    for r in runs:
        out.setdefault(r["instance_idx"], []).append(r)
    return out


def _values_for(inst_runs, field_name) -> List[Any]:
    return [
        r["normalized"][field_name]
        for r in inst_runs
        if r.get("normalized") and field_name in r["normalized"] and r["normalized"][field_name] is not None
    ]


def score_runs(task: Dict[str, Any], instances, runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """RELIABILITY: fraction of runs matching the per-field mode. Label-free."""
    fields = task["fields"]
    parse_fail = sum(1 for r in runs if r.get("parsed") is None)
    by_inst = _runs_by_instance(runs)
    scores, flips = [], {f: 0 for f in fields}
    excluded = [f for f, s in fields.items() if s["type"] not in _SCORABLE]
    for inst_idx in range(len(instances)):
        for fname, fspec in fields.items():
            if fspec["type"] not in _SCORABLE:
                continue
            vals = _values_for(by_inst.get(inst_idx, []), fname)
            if not vals:
                continue
            _, mode_count = Counter(vals).most_common(1)[0]
            consistency = mode_count / len(vals)
            scores.append(consistency)
            if consistency < 1.0:
                flips[fname] += 1
    rate = sum(scores) / len(scores) if scores else 0.0
    valid = len(runs) - parse_fail
    return {
        "task": task["name"],
        "consistency_rate": rate,
        "consistency_pct": rate * 100,
        "field_flips": {f: flips[f] / len(instances) if instances else 0.0 for f in fields if f not in excluded},
        "parse_failure_count": parse_fail,
        "parse_failure_rate": parse_fail / len(runs) if runs else 0,
        "valid_run_count": valid,
        "measurable": (parse_fail / len(runs) if runs else 1) <= 0.3 and valid >= 2 and len(scores) > 0,
        "excluded_fields": excluded,
    }


def score_accuracy(task: Dict[str, Any], instances, runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """ACCURACY vs the validated oracle answer. Majority-vote + strict (all-runs) per instance."""
    fields = task["fields"]
    by_inst = _runs_by_instance(runs)
    per_instance, maj_correct, strict_correct, measurable = [], 0, 0, 0
    for inst_idx, (_inst, truth) in enumerate(instances):
        row = _score_one_instance(fields, by_inst.get(inst_idx, []), truth, inst_idx)
        per_instance.append(row)
        if row["n_valid"] == 0:
            continue
        measurable += 1
        maj_correct += int(row["majority_correct"])
        strict_correct += int(row["strict_correct"])
    return {
        "task": task["name"],
        "n_instances": len(instances),
        "n_measurable": measurable,
        "accuracy_majority": maj_correct / measurable if measurable else 0.0,
        "accuracy_strict": strict_correct / measurable if measurable else 0.0,
        "per_instance": per_instance,
    }


def _score_one_instance(fields, inst_runs, truth, inst_idx) -> Dict[str, Any]:
    """Majority answer vs canonical(truth) for each scored field; AND over fields per instance."""
    maj_all, strict_all, n_valid_min, details = True, True, None, {}
    for fname, fspec in fields.items():
        if fspec["type"] not in _SCORABLE:
            continue
        vals = _values_for(inst_runs, fname)
        truth_c = normalize.canonical(truth.get(fname), fspec["type"]) if truth else None
        n_valid_min = len(vals) if n_valid_min is None else min(n_valid_min, len(vals))
        if not vals:
            maj_all = strict_all = False
            details[fname] = {"majority": None, "truth": truth_c, "consistency": 0.0}
            continue
        mode_val, mode_count = Counter(vals).most_common(1)[0]
        maj_all = maj_all and (mode_val == truth_c)
        strict_all = strict_all and all(v == truth_c for v in vals)
        details[fname] = {"majority": mode_val, "truth": truth_c, "consistency": mode_count / len(vals)}
    return {
        "instance_idx": inst_idx,
        "n_valid": n_valid_min or 0,
        "majority_correct": maj_all if (n_valid_min or 0) > 0 else False,
        "strict_correct": strict_all if (n_valid_min or 0) > 0 else False,
        "fields": details,
    }
