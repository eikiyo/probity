#!/usr/bin/env bash
# Location: kaggle-arm/pack.sh
# Purpose: Build the Kaggle dataset payload for track C (local models, off-laptop on a T4).
#          Ships the ENGINE and the 60 leaves' INPUTS only -- corpus, oracle, task.py. Existing
#          results (checkpoints/scored/scorecards) are deliberately EXCLUDED: the kernel must
#          start from a clean slate for its arm, and shipping the 0.7 results into a machine that
#          re-writes leaf files is how a baseline gets silently overwritten.
set -euo pipefail
# Both paths ABSOLUTE before the cd: OUT was relative and `cd "$REPO"` silently
# redirected the tarball into the repo root, where the kernel push would never find it.
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
OUT="$HERE/probity-arm-harness.tgz"
cd "$REPO"
tar czf "$OUT" \
  --exclude='runs_*.jsonl' --exclude='scored*.json' --exclude='*.html' \
  --exclude='manifest_*.json' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='*.lock' \
  engine leaves
echo "wrote $OUT ($(du -h "$OUT" | cut -f1))"
echo "sanity: $(tar tzf "$OUT" | grep -c 'oracle.jsonl') oracle files, $(tar tzf "$OUT" | grep -c 'task.py') task files"
