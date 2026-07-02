"""
Location: probity_cli/materialize.py
Purpose: Copy the bundled benchmark code (engine/, leaves/*, results/, demo/ -- code + labels +
         prior run outputs, NEVER corpus/ raw documents) into a writable ~/.probity/repo/ so the
         existing run.py/source.py scripts (which write files relative to themselves) work exactly
         as they do from a git clone. Re-copies on a version bump; otherwise a no-op.
Functions: source_root(), ensure_materialized(), repo_dir()
Calls: (stdlib only)
Imports: shutil, pathlib, probity_cli.config, probity_cli
"""

import shutil
from pathlib import Path

from probity_cli import __version__
from probity_cli.config import HOME_DIR

PACKAGE_DIR = Path(__file__).parent
BUNDLED_DATA = PACKAGE_DIR / "data"
DEV_REPO_ROOT = PACKAGE_DIR.parent  # when run from a git clone, engine/ is a sibling of probity_cli/

REPO_DIR = HOME_DIR / "repo"
VERSION_STAMP = REPO_DIR / ".materialized_version"

# What gets materialized -- same list whether copying from the wheel's bundled data/ or a dev checkout.
_DIRS = ["engine", "leaves", "results", "demo"]


def source_root():
    """Where the real files live right now: the wheel's bundled data/ if installed, else the dev
    checkout's repo root (this file's grandparent) if that looks like a real Probity checkout."""
    if (BUNDLED_DATA / "engine").is_dir():
        return BUNDLED_DATA
    if (DEV_REPO_ROOT / "engine").is_dir():
        return DEV_REPO_ROOT
    raise RuntimeError(
        "Could not find Probity's engine/ code (checked the installed package data and the dev "
        "checkout). This install looks broken -- try `pip install --force-reinstall probity-bench`."
    )


def repo_dir():
    return REPO_DIR


def ensure_materialized(force=False):
    """Copy source_root()'s {engine,leaves,results,demo} into ~/.probity/repo/ if missing or stale.
    Returns the materialized repo dir. force=True always re-copies (used by `onboard --reset`)."""
    stamp = VERSION_STAMP.read_text(encoding="utf-8").strip() if VERSION_STAMP.exists() else None
    if not force and stamp == __version__ and REPO_DIR.is_dir():
        return REPO_DIR

    root = source_root()
    REPO_DIR.mkdir(parents=True, exist_ok=True)
    for name in _DIRS:
        src = root / name
        if not src.is_dir():
            continue  # demo/ or results/ may legitimately be thin; never fail the whole copy for it.
        dst = REPO_DIR / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(
            src, dst,
            ignore=shutil.ignore_patterns("corpus", "_archive_*", "__pycache__", "*.pyc"),
        )
    VERSION_STAMP.write_text(__version__ + "\n", encoding="utf-8")
    return REPO_DIR
