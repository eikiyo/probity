"""
Location: engine/coverage.py
Purpose: Assert a (leaf, model) cell actually recorded every call it OWED, measured against an
         INDEPENDENTLY DECLARED source (items x n_runs, read from the leaf's own oracle.jsonl) --
         never against a number derived from the recorded data itself.
Functions: expected_calls(), recorded_keys(), missing_keys(), cell_status(), coverage_matrix(),
           assert_full(), render_matrix()
Calls: none (pure; the caller decides how to report)
Imports: json, pathlib
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


class CoverageError(RuntimeError):
    """Raised when a coverage assertion fails. Fail closed: a hole is reported explicitly, never
    averaged over (DESIGN sad-path rows 1 and 2)."""


def n_items(leaf_dir: Path) -> int:
    """Item count from the leaf's own oracle.jsonl -- the spec, not the result."""
    return sum(1 for line in open(leaf_dir / "oracle.jsonl", encoding="utf-8") if line.strip())


def expected_calls(leaf_dir: Path, n_runs: int) -> int:
    """
    What: how many model calls this leaf OWES one model = (oracle items) x n_runs.
    Why this exists: the pre-existing "Response rate" column in RESULTS.md computed
          attempted = valid_run_count + parse_failure_count. BOTH are counted from run records
          that EXIST on disk, so a call that was never made appears in neither. On 2026-07-03
          that printed "332/333 (100%)" for a cell owing 360 calls -- a perfect score derived
          from its own truncated data. Same family as the PMP `earned === max` failure: a total
          checked against itself. This reads the count from oracle.jsonl instead.
    """
    return n_items(leaf_dir) * n_runs


def recorded_keys(checkpoint_path: Path) -> Set[Tuple[int, int]]:
    """
    What: the DISTINCT set of (instance_idx, run_idx) keys a checkpoint file actually holds.
    Why a SET and not a line count: these files are append-only and resume-safe, so a resumed run
          appends a fresh record beside whatever was already there and the same key can legitimately
          appear twice. Counting lines would report a double-counted cell as over-complete -- and on
          a cell that had ALSO lost calls, as exactly complete, hiding the hole. Dedup by key first,
          then count. Pinned by tests/test_coverage.py::TestDuplicateKeysCountOnce.
    """
    keys: Set[Tuple[int, int]] = set()
    if not checkpoint_path.exists():
        return keys
    with open(checkpoint_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            idx, run = rec.get("instance_idx"), rec.get("run_idx")
            if idx is not None and run is not None:
                keys.add((int(idx), int(run)))
    return keys


def arm_tag(temperature: float) -> str:
    """
    What: the short arm name for a temperature, e.g. 0.7 -> "t07", 0.1 -> "t01".
    Why here: this is the ONE definition of the convention. The runner (writing artifacts), the
          coverage assert (finding them) and the renderer (reading them) all call this, so they
          cannot drift apart -- a mismatch would silently make a full cell look absent.
    """
    digits = f"{temperature:g}".replace("0.", "0", 1).replace(".", "")
    return f"t{digits}"


def arm_label(temperature: Optional[float]) -> str:
    """
    The HUMAN-facing name for an arm, for headings and table columns.

    `None` is an internal sentinel meaning "the legacy unsuffixed 0.7 sweep". Interpolating it
    raw produced report headings that read `paired against None` and `## Paired comparison: None
    vs 0.1` -- a reviewer cannot tell whether that means the legacy arm, a missing value, or a
    bug. The legacy arm's temperature is spelled out because "legacy" alone does not say 0.7.
    """
    if temperature is None:
        return "legacy (0.7)"
    return f"{arm_tag(temperature)} ({temperature})"


def artifact_suffix(temperature: Optional[float]) -> str:
    """Filename infix for an arm. None = the LEGACY unsuffixed arm (the published 0.7 sweep from
    2026-07-02/03), which keeps its original `runs_<label>.jsonl` / `scored.json` names and is
    never overwritten. Any explicit temperature gets its own namespace."""
    return "" if temperature is None else f"{arm_tag(temperature)}_"


def scored_filename(temperature: Optional[float]) -> str:
    """`scored.json` for the legacy arm, `scored_t01.json` / `scored_t07.json` for the new ones."""
    return "scored.json" if temperature is None else f"scored_{arm_tag(temperature)}.json"


def checkpoint_path(leaf_dir: Path, label: str, suffix: str = "") -> Path:
    """The ONE place the checkpoint filename convention is defined, so the runner, the coverage
    assert and the backfill can never disagree about which file a cell lives in."""
    return leaf_dir / f"runs_{suffix}{label}.jsonl"


def missing_keys(leaf_dir: Path, label: str, n_runs: int,
                  suffix: str = "") -> List[Tuple[int, int]]:
    """The exact (instance_idx, run_idx) pairs a cell still owes -- drives a TARGETED backfill
    rather than re-running (and re-billing) a whole cell."""
    have = recorded_keys(checkpoint_path(leaf_dir, label, suffix))
    return [(i, r) for i in range(n_items(leaf_dir)) for r in range(n_runs) if (i, r) not in have]


def cell_status(leaf_dir: Path, label: str, n_runs: int, suffix: str = "") -> Dict[str, Any]:
    """One (leaf, model) cell's coverage record. `complete` is True only when every owed key is
    present, not when a line count happens to match."""
    expected = expected_calls(leaf_dir, n_runs)
    recorded = len(recorded_keys(checkpoint_path(leaf_dir, label, suffix)))
    return {"leaf": leaf_dir.name, "label": label, "expected": expected, "recorded": recorded,
            "complete": recorded == expected, "short_by": expected - recorded}


def coverage_matrix(leaf_dirs: Iterable[Path], labels: Iterable[str], n_runs: int,
                     suffix: str = "") -> List[Dict[str, Any]]:
    """Every (leaf, model) cell's status -- deliverable 6's matrix, one row per cell."""
    labels = list(labels)
    return [cell_status(d, lab, n_runs, suffix) for d in leaf_dirs for lab in labels]


def label_shortfall(matrix: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    """
    Per label: how many of its cells are short, and by how many calls. A label absent from the
    result is complete for this arm.

    This is the distinction a paired report lives on. A label with SOME data is not a label with
    ENOUGH data, and a delta computed over a fraction of the items renders identically to one
    computed over all of them -- same columns, same formatting, no marker. Callers use this to
    exclude-and-name rather than to average over a moving denominator.
    """
    out: Dict[str, Dict[str, int]] = {}
    for c in matrix:
        if c["complete"]:
            continue
        agg = out.setdefault(c["label"],
                             {"short_cells": 0, "short_calls": 0, "cells": 0, "recorded": 0})
        agg["short_cells"] += 1
        agg["short_calls"] += c["short_by"]
    for c in matrix:
        if c["label"] in out:
            out[c["label"]]["cells"] += 1
            out[c["label"]]["recorded"] += c["recorded"]
    # `started` separates a model MID-SWEEP from one that has never run in this arm. Both are
    # excluded from a paired report, but they are different facts: an unstarted model is work not
    # yet done, a partial one is work in flight whose numbers would look finished if rendered.
    for agg in out.values():
        agg["started"] = agg["recorded"] > 0
    return out


def assert_full(matrix: List[Dict[str, Any]]) -> None:
    """Fail closed on ANY hole: raises CoverageError naming every incomplete cell and how short
    it is. A hole is reported, never averaged over."""
    holes = [c for c in matrix if not c["complete"]]
    if not holes:
        return
    lines = [f"  {c['leaf']} / {c['label']}: {c['recorded']}/{c['expected']} "
             f"(short {c['short_by']})" for c in holes]
    raise CoverageError(
        f"coverage incomplete: {len(holes)} of {len(matrix)} cells short\n" + "\n".join(lines))


def render_matrix(matrix: List[Dict[str, Any]], labels: Optional[List[str]] = None) -> str:
    """Markdown coverage matrix (rows = leaves, cols = models). A complete cell shows its call
    count; a short cell shows recorded/expected in bold so a hole is visible, never a bare tick."""
    labels = labels or sorted({c["label"] for c in matrix})
    by_leaf: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for c in matrix:
        by_leaf.setdefault(c["leaf"], {})[c["label"]] = c
    out = ["| Leaf | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
    for leaf in sorted(by_leaf):
        out.append(f"| {leaf} | " + " | ".join(_cell_text(by_leaf[leaf].get(lab))
                                                for lab in labels) + " |")
    total = sum(c["recorded"] for c in matrix)
    owed = sum(c["expected"] for c in matrix)
    full = sum(1 for c in matrix if c["complete"])
    out += ["", f"**{full}/{len(matrix)} cells complete · {total}/{owed} calls recorded**"]
    return "\n".join(out)


def _cell_text(cell: Optional[Dict[str, Any]]) -> str:
    if cell is None:
        return "**absent**"
    return str(cell["recorded"]) if cell["complete"] else f"**{cell['recorded']}/{cell['expected']}**"
