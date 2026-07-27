#!/usr/bin/env bash
# Location: kaggle-arm/push_instances.sh
# Purpose: Generate and push ONE Kaggle kernel PER MODEL so both run as concurrent GPU sessions.
#          Kaggle kernels take no env vars at push time, so MODEL_INDEX is baked into each copy by
#          rewriting the single constant line -- the rest of the script is byte-identical between
#          instances, so the two runs cannot drift apart.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
NAMES=("1b" "1b-qat")
for i in 0 1; do
  DIR="$HERE/inst-${NAMES[$i]}"
  rm -rf "$DIR"; mkdir -p "$DIR"
  sed "s|^MODEL_INDEX = .*|MODEL_INDEX = $i   # baked by push_instances.sh|" arm_kernel.py > "$DIR/arm_kernel.py"
  python3 -c "import ast,sys; ast.parse(open('$DIR/arm_kernel.py').read())" || { echo "generated kernel $i has a syntax error"; exit 1; }
  grep -q "^MODEL_INDEX = $i " "$DIR/arm_kernel.py" || { echo "MODEL_INDEX $i was NOT baked in"; exit 1; }
  sed "s|probity-arm-local|probity-arm-${NAMES[$i]}|g" kernel-metadata.json > "$DIR/kernel-metadata.json"
  echo "=== pushing probity-arm-${NAMES[$i]} (MODEL_INDEX=$i) ==="
  kaggle kernels push -p "$DIR"
done
