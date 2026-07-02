"""
Location: probity_cli/config.py
Purpose: Local config + secret storage under ~/.probity/ -- config.json (non-secret settings) and
         .env (chmod 600, actual key values IF the user chose to store one; a "ref" entry instead
         stores only an env-var NAME, never a value -- see save_secret_ref()).
Functions: load_config(), save_config(), load_env_file(), save_secret_value(), save_secret_ref(),
           resolve_secret(), mask()
Calls: (stdlib only)
Imports: json, os, stat, pathlib
"""

import json
import os
import stat
from pathlib import Path

HOME_DIR = Path.home() / ".probity"
CONFIG_PATH = HOME_DIR / "config.json"
ENV_PATH = HOME_DIR / ".env"

# Providers the onboarding wizard knows how to ask for, keyed by the env var engine/models.py
# actually reads (grounded in models.py -- never invent a provider that isn't wired up).
PROVIDER_ENV_VARS = {
    "deepseek": "DEEPSEEK_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


def load_config():
    """Read ~/.probity/config.json. Missing file -> {} (never raises for absence)."""
    if not CONFIG_PATH.exists():
        return {}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def save_config(cfg):
    """Write ~/.probity/config.json, creating the dir if needed."""
    HOME_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def load_env_file():
    """Parse ~/.probity/.env (simple KEY=VALUE lines) into a dict. Missing file -> {}."""
    if not ENV_PATH.exists():
        return {}
    out = {}
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _write_env_file(env):
    HOME_DIR.mkdir(parents=True, exist_ok=True)
    lines = [f"{k}={v}" for k, v in sorted(env.items())]
    ENV_PATH.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    os.chmod(ENV_PATH, stat.S_IRUSR | stat.S_IWUSR)  # chmod 600 -- this file can hold raw keys.


def save_secret_value(var_name, raw_value):
    """Store the RAW key value under ~/.probity/.env (chmod 600). Never printed back by caller."""
    env = load_env_file()
    env[var_name] = raw_value
    _write_env_file(env)


def save_secret_ref(var_name, ref_env_var):
    """Store a REFERENCE (an existing env var NAME, not a value) -- the secret-ref pattern: the
    real key stays wherever the user already keeps it (their shell profile), we only remember
    which var name to read at run time."""
    env = load_env_file()
    env[var_name] = f"$REF:{ref_env_var}"
    _write_env_file(env)


def resolve_secret(var_name):
    """Resolve a provider's key at run time: process env wins (matches OpenClaw's precedence),
    then ~/.probity/.env (following a $REF pointer if that's what's stored), else None."""
    if os.environ.get(var_name):
        return os.environ[var_name]
    stored = load_env_file().get(var_name)
    if stored is None:
        return None
    if stored.startswith("$REF:"):
        return os.environ.get(stored[len("$REF:"):])
    return stored


def mask(value):
    """sk-...ab12 style masking for display -- never show a full secret."""
    if not value:
        return "(not set)"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:3]}...{value[-4:]}"
