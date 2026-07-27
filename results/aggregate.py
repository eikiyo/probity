"""
Location: results/aggregate.py
Purpose: Read one temperature ARM off disk and reduce it to the COUNTS every downstream table
         needs (flipped items / total items, correct items / measurable items), plus per-item flip
         flags so a 0.7-vs-0.1 comparison can be genuinely PAIRED. Shared by results/render.py
         (the README + RESULTS.md) and results/compare.py (the paired report) so neither
         re-implements the reduction.
Functions: canonical_lineup(), built_leaves(), leaf_scored(), per_item_flips(), model_counts(),
           family_counts(), paired_counts()
Calls: engine/coverage.py (arm -> filename convention)
Imports: json, importlib.util, pathlib, sys
"""

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "engine"))

import coverage  # noqa: E402

# The ELEVEN labels that constitute the published benchmark lineup.
#
# WHY AN EXPLICIT LIST AND NOT A HEURISTIC: render.py filtered the suite table with
# "a model counts if it ran >= 10 leaves". That worked while only the benchmark existed, but the
# fine-tune lab later wrote 43 more labels (tuned-v4*, v5-r*, qwen*, mlx-base*) into the same
# scored.json files, several of which cleared 10 leaves. Regenerating the README today would emit
# a 29-ROW table instead of 11, silently mixing training experiments into the published result.
# A lineup is an editorial decision, so it is declared, not inferred from a count.
CANONICAL_LINEUP = [
    "gemma3-1b", "deepseek-v4f", "deepseek-v4p", "gemma4-31b-or", "mistral-large-or", "minimax-m2.5-or",
    "llama3.3-70b-or", "gemma3-1b-qat", "gemini3-flash-or", "haiku-4.5-direct",
    "gpt-oss-120b-or", "gpt5-mini-or",
]


def canonical_lineup() -> List[str]:
    return list(CANONICAL_LINEUP)


def built_leaves() -> List[Dict[str, Any]]:
    """Registry entries for the 60 built leaves. The registry is the source of truth for which
    leaves count -- never a directory listing, never a hand-typed number."""
    reg = json.loads((ROOT / "engine" / "registry.json").read_text())
    return [l for l in reg["leaves"] if l.get("tier") == "built" and "leaf" in l]


def leaf_scored(leaf_rel: str, temperature: Optional[float]) -> Optional[Dict[str, Any]]:
    """That leaf's scored file for ONE arm, or None if the arm has not been run there."""
    p = ROOT / leaf_rel / coverage.scored_filename(temperature)
    return json.loads(p.read_text()) if p.exists() else None


def _field_of(leaf_rel: str) -> str:
    reg_field = {l["leaf"]: l["field"] for l in built_leaves()}
    return reg_field[leaf_rel]


def per_item_flips(res: Dict[str, Any], field: str) -> List[Optional[bool]]:
    """
    What: per-item wobble flags for one (leaf, model) cell, aligned to oracle order.
    Tri-state, deliberately: True = the answer flipped across runs, False = it held, and
          None = NOT MEASURABLE (the item recorded no valid runs at all).
    Why None instead of False: engine/scorer.py's two code paths disagree about a zero-run item.
          score_runs() skips it (`if not vals: continue`) so it is NOT counted as a flip, while
          score_accuracy() records consistency 0.0, which any `consistency < 1.0` test reads as a
          flip. Collapsing that ambiguity either way corrupts a paired comparison, so an
          unmeasured item is carried as unknown and excluded from the pairing, with the count of
          exclusions reported rather than hidden.
    """
    out: List[Optional[bool]] = []
    for row in res.get("accuracy", {}).get("per_instance", []):
        if row.get("n_valid", 0) == 0:
            out.append(None)
            continue
        detail = row.get("fields", {}).get(field)
        out.append(None if detail is None else bool(detail.get("consistency", 1.0) < 1.0))
    return out


def model_counts(temperature: Optional[float],
                  lineup: Optional[List[str]] = None) -> Dict[str, Dict[str, int]]:
    """
    Per-model COUNTS across every built leaf for one arm:
        flipped / measured  -> wobble, as a binomial over items
        correct / measurable -> accuracy
    Counts, not rates, because a Wilson interval needs k and n. Rates are recovered downstream.
    """
    lineup = lineup or canonical_lineup()
    acc: Dict[str, Dict[str, int]] = {m: {"flipped": 0, "measured": 0, "correct": 0,
                                           "measurable": 0, "leaves": 0} for m in lineup}
    for l in built_leaves():
        scored = leaf_scored(l["leaf"], temperature)
        if not scored:
            continue
        field = l["field"]
        for model in lineup:
            res = scored.get(model)
            if not res or not res.get("reliability", {}).get("measurable", True):
                continue
            flags = per_item_flips(res, field)
            a = res.get("accuracy", {})
            n_meas = a.get("n_measurable", 0)
            acc[model]["flipped"] += sum(1 for f in flags if f is True)
            acc[model]["measured"] += sum(1 for f in flags if f is not None)
            acc[model]["correct"] += int(round(a.get("accuracy_majority", 0) * n_meas))
            acc[model]["measurable"] += n_meas
            acc[model]["leaves"] += 1
    return {m: c for m, c in acc.items() if c["leaves"] > 0}


def family_counts(temperature: Optional[float],
                   lineup: Optional[List[str]] = None) -> Dict[str, Dict[str, int]]:
    """Same reduction, bucketed by registry family, averaged across every model in the lineup."""
    lineup = lineup or canonical_lineup()
    acc: Dict[str, Dict[str, int]] = {}
    for l in built_leaves():
        scored = leaf_scored(l["leaf"], temperature)
        if not scored:
            continue
        field, fam = l["field"], l["family"]
        bucket = acc.setdefault(fam, {"flipped": 0, "measured": 0, "correct": 0,
                                       "measurable": 0, "leaves": 0, "_seen": set()})
        for model in lineup:
            res = scored.get(model)
            if not res or not res.get("reliability", {}).get("measurable", True):
                continue
            flags = per_item_flips(res, field)
            a = res.get("accuracy", {})
            n_meas = a.get("n_measurable", 0)
            bucket["flipped"] += sum(1 for f in flags if f is True)
            bucket["measured"] += sum(1 for f in flags if f is not None)
            bucket["correct"] += int(round(a.get("accuracy_majority", 0) * n_meas))
            bucket["measurable"] += n_meas
            bucket["_seen"].add(l["leaf"])
    for fam, b in acc.items():
        b["leaves"] = len(b.pop("_seen"))
    return {f: b for f, b in acc.items() if b["leaves"] > 0}


def parse_failure_counts(temperature: Optional[float],
                          lineup: Optional[List[str]] = None) -> Dict[str, Dict[str, int]]:
    """
    Per model, for one arm: how many runs produced NOTHING a parser could read, and how many
    leaves were consequently dropped from the published numbers.

    Why this is a first-class metric and not diagnostics. `model_counts` refuses to score a leaf
    for a model when >30% of that leaf's runs are unparseable. That is the right call -- the
    surviving answers are too thin a sample -- but it SHRINKS THE DENOMINATOR, and wobble is a
    rate. A model that stops parsing on its hardest tests therefore looks MORE consistent, because
    the tests it failed to answer stop counting. deepseek-v4-flash is the live example: it went
    from 0% parse failures on seven leaves at 0.7 to 30-75% at 0.1, those leaves were excluded,
    and its published 0.1 wobble is computed over 426 items against 470 at 0.7.

    Reporting this beside wobble is what stops a reader mistaking "answered fewer things" for
    "answered more consistently".
    """
    lineup = lineup or canonical_lineup()
    out: Dict[str, Dict[str, int]] = {}
    for l in built_leaves():
        scored = leaf_scored(l["leaf"], temperature)
        if not scored:
            continue
        for model in lineup:
            res = scored.get(model)
            if not res:
                continue
            rel = res.get("reliability", {})
            agg = out.setdefault(model, {"failures": 0, "runs": 0, "leaves": 0,
                                          "leaves_excluded": 0})
            agg["failures"] += rel.get("parse_failure_count", 0)
            agg["runs"] += rel.get("valid_run_count", 0) + rel.get("parse_failure_count", 0)
            agg["leaves"] += 1
            if not rel.get("measurable", True):
                agg["leaves_excluded"] += 1
    return out


def paired_counts(model: str, temp_a: Optional[float],
                   temp_b: Optional[float]) -> Dict[str, int]:
    """
    What: the discordant counts driving a PAIRED wobble comparison for one model across two arms,
          matched item by item on the SAME oracle rows.
    Output: {"n_pairs", "both", "only_a", "only_b", "neither", "dropped"} where `dropped` counts
            items excluded because either arm could not measure them. Reporting `dropped` is not
            optional: a pair silently dropped is a denominator quietly shrinking, which is exactly
            how a self-referential coverage number gets built.
    """
    out = {"n_pairs": 0, "both": 0, "only_a": 0, "only_b": 0, "neither": 0, "dropped": 0}
    for l in built_leaves():
        sa, sb = leaf_scored(l["leaf"], temp_a), leaf_scored(l["leaf"], temp_b)
        if not sa or not sb:
            continue
        ra, rb = sa.get(model), sb.get(model)
        if not ra or not rb:
            continue
        fa = per_item_flips(ra, l["field"])
        fb = per_item_flips(rb, l["field"])
        for x, y in zip(fa, fb):
            if x is None or y is None:
                out["dropped"] += 1
                continue
            out["n_pairs"] += 1
            key = "both" if (x and y) else "only_a" if x else "only_b" if y else "neither"
            out[key] += 1
    return out
