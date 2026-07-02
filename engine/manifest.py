"""
Location: engine/manifest.py
Purpose: Reproducibility manifest (DESIGN T8) -- records data_version, model id, seed
         (n_runs/temperature), and a timestamp alongside a leaf's run, so anyone can re-run from
         it and get the identical score. Honest scope: this system samples a live model at
         temperature>0 with no seed param exposed by any provider client (engine/models.py), so
         "reproducible" here means what is ACTUALLY guaranteed -- engine/scorer.py is a pure
         function of the recorded run data, so the SAME run records always re-score to the
         IDENTICAL result. verify_manifest() checks that guarantee: it fingerprints the run
         records the manifest was built from and fails closed if that data has drifted.
Functions: content_hash(), build_manifest(), verify_manifest()
Calls: none (pure)
Imports: hashlib, json, datetime
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def content_hash(obj: Any) -> str:
    """Deterministic sha256 over a canonical (sorted-key) JSON dump. Any change to the
    underlying data -- a value, a key, ordering -- changes this hash."""
    canonical = json.dumps(obj, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_manifest(
    leaf_name: str,
    model_label: str,
    run_records: List[Dict[str, Any]],
    task_name: str,
    n_runs: int,
    temperature: float,
    timestamp: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a manifest dict for one leaf+model run. `timestamp` may be injected (tests, CI
    replay) or left None to stamp the real current UTC time."""
    ts = timestamp if timestamp is not None else datetime.now(timezone.utc).isoformat()
    manifest = {
        "leaf": leaf_name,
        "model": model_label,
        "task_name": task_name,
        "data_version": content_hash(run_records),
        "n_runs": n_runs,
        "temperature": temperature,
        "timestamp": ts,
    }
    if extra:
        manifest["extra"] = extra
    return manifest


def verify_manifest(manifest: Dict[str, Any], run_records: List[Dict[str, Any]]) -> bool:
    """Fail-closed reproducibility check: True only if run_records hash to EXACTLY the
    data_version recorded in the manifest. Any drift (a changed value, a dropped/added record)
    returns False -- never silently True."""
    if "data_version" not in manifest:
        return False
    return content_hash(run_records) == manifest["data_version"]
