"""
Location: kaggle-arm/pull_results.py
Purpose: Extract a track-C kernel's arm-results.tgz into leaves/ WITHOUT ever writing a
         legacy-namespace file. The kernel is supposed to produce only t01_/t07_ artifacts
         (pack.sh ships inputs only, so it has no legacy results to hand back), but "supposed to"
         is not a control: a future edit to pack.sh's exclude list, or an ARMS entry of None
         instead of 0.7, would put `scored.json` / `runs_<label>.jsonl` in the tarball, and
         extracting those over the repo would overwrite the published 0.7 baseline -- the one
         thing this whole experiment must not do. So the guard lives at the EXTRACT end, where
         the damage would actually happen, and refuses the whole archive rather than skipping
         the offending member (a partial extract of an archive we do not trust is not a repair).
Functions: legacy_members(), verify_archive(), extract(), main()
Calls: tarfile, pathlib
Imports: argparse, re, sys, tarfile, pathlib
Run: python3 kaggle-arm/pull_results.py arm-results.tgz [--into leaves] [--dry-run]
"""

import argparse
import re
import sys
import tarfile
from pathlib import Path

# A results file with NO arm infix belongs to the legacy 0.7 sweep. Anything the kernel legitimately
# produces carries one (`runs_t01_<label>.jsonl`, `scored_t07.json`).
LEGACY_RUNS = re.compile(r"(^|/)runs_(?!t\d+_)[^/]+\.jsonl$")
LEGACY_SCORED = re.compile(r"(^|/)scored\.json$")
ESCAPES = re.compile(r"^/|(^|/)\.\.(/|$)")


def legacy_members(names):
    """Members that would land on a legacy-arm path. Empty means the archive is safe to extract."""
    return [n for n in names if LEGACY_RUNS.search(n) or LEGACY_SCORED.search(n)]


def escaping_members(names):
    """Absolute paths and `..` traversal. A tarball from a remote runner is untrusted input, and
    an extract that can write outside `--into` can overwrite anything in the repo."""
    return [n for n in names if ESCAPES.search(n)]


def verify_archive(path):
    """Returns (ok, problems). Fails CLOSED: an archive we cannot read is not an archive we trust."""
    try:
        with tarfile.open(path, "r:gz") as tf:
            names = tf.getnames()
    except Exception as ex:                      # noqa: BLE001 -- reported, never swallowed
        return False, [f"cannot read {path}: {ex}"]
    if not names:
        return False, [f"{path} is empty -- a kernel that produced nothing is a failed kernel"]
    problems = []
    for n in legacy_members(names):
        problems.append(f"LEGACY-ARM FILE: {n} would overwrite the published 0.7 baseline")
    for n in escaping_members(names):
        problems.append(f"PATH ESCAPE: {n}")
    return (not problems), problems


SHARED_SCORED = re.compile(r"(^|/)scored(_t\d+)?\.json$")


def is_shared(name):
    """`scored*.json` is ONE file per leaf holding EVERY model label. `runs_*`/`manifest_*` carry
    their label in the filename and so belong to exactly one model."""
    return bool(SHARED_SCORED.search(name))


def merge_scored(existing_path, incoming_bytes):
    """Union an incoming leaf's scored file into the one on disk, by model label.

    A tar extract REPLACES. The kernel starts from a clean slate (pack.sh ships inputs only), so
    its scored_t01.json holds exactly one label -- and extracting that over a local file holding
    ten would delete the entire hosted arm's scoring in one silent move, across all 60 leaves.
    The legacy guard above does not catch this: scored_t01.json IS arm-namespaced and passes.

    Delegates to runner._merge_scored so the merge is the SAME operation the sweep performs
    (exclusive flock held across read AND write, atomic replace) rather than a second
    implementation that could diverge from it.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "engine"))
    import runner
    import json
    incoming = json.loads(incoming_bytes)
    before = set(json.loads(existing_path.read_text())) if existing_path.exists() else set()
    runner._merge_scored(existing_path, incoming)
    after = set(json.loads(existing_path.read_text()))
    assert before <= after, f"merge DROPPED labels from {existing_path}: {sorted(before - after)}"
    return {"added": sorted(after - before), "kept": sorted(before), "updated":
            sorted(before & set(incoming))}


def extract(path, into, dry_run=False):
    ok, problems = verify_archive(path)
    if not ok:
        for p in problems:
            print(f"  REFUSED: {p}", file=sys.stderr)
        raise SystemExit(
            f"refusing to extract {path}: {len(problems)} problem(s). The archive is rejected "
            "whole -- not partially extracted -- because an archive containing a legacy-arm file "
            "is one whose producer we no longer trust to have namespaced anything correctly.")
    with tarfile.open(path, "r:gz") as tf:
        members = [m for m in tf.getmembers() if m.isfile()]
        shared = [m for m in members if is_shared(m.name)]
        direct = [m for m in members if not is_shared(m.name)]
        if dry_run:
            print(f"{path}: {len(members)} files -- {len(direct)} extracted directly, "
                  f"{len(shared)} MERGED by model label (never overwritten).")
            return [m.name for m in members]
        for m in direct:
            tf.extract(m, into)
        added = set()
        for m in shared:
            res = merge_scored(Path(into) / m.name, tf.extractfile(m).read())
            added.update(res["added"])
        print(f"extracted {len(direct)} per-label files; merged {len(shared)} shared scored files "
              f"-- labels added: {sorted(added)}")
    return [m.name for m in members]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("archive")
    p.add_argument("--into", default=".", help="repo root (the archive holds leaves/... paths)")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    extract(Path(args.archive), Path(args.into), args.dry_run)


if __name__ == "__main__":
    main()
