"""
Location: probity_cli/onboard.py
Purpose: Interactive first-run wizard (OpenClaw-style step order): detect existing config -> pick
         which leaves to fetch real SEC documents for -> pick model(s) (local Ollama / hosted
         DeepSeek+Gemini) -> collect + verify API key(s) -> write ~/.probity/config.json + .env ->
         summary. Every prompt goes through an injectable `io` object so this is testable without
         real stdin (drives the SAME function tests assert on, not a mock of the unit).
Functions: TerminalIO class, run_onboarding(), _pick_leaves(), _pick_models(), _collect_key(),
           _verify_key(), _detect_ollama_models()
Calls: probity_cli.config, probity_cli.materialize, subprocess (ollama list, leaf source.py)
Imports: sys, subprocess, getpass, importlib.util, pathlib, probity_cli.config, probity_cli.materialize
"""

import subprocess
import sys
from pathlib import Path

from probity_cli import config as cfgmod
from probity_cli.materialize import ensure_materialized


class TerminalIO:
    """Real stdin/stdout IO for interactive use. Tests substitute a canned-answer double."""

    def print(self, text=""):
        print(text)

    def ask(self, prompt, default=None):
        suffix = f" [{default}]" if default is not None else ""
        raw = input(f"{prompt}{suffix}: ").strip()
        return raw or (default or "")

    def ask_secret(self, prompt):
        import getpass
        return getpass.getpass(f"{prompt}: ").strip()

    def confirm(self, prompt, default=True):
        suffix = " [Y/n]" if default else " [y/N]"
        raw = input(f"{prompt}{suffix}: ").strip().lower()
        if not raw:
            return default
        return raw.startswith("y")


def _detect_ollama_models():
    """Best-effort `ollama list` -- returns [] on any failure (Ollama not installed/running),
    never raises (this is a nice-to-have detection, not a hard requirement)."""
    try:
        out = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        if out.returncode != 0:
            return []
        lines = out.stdout.strip().splitlines()[1:]  # skip header row
        return [line.split()[0] for line in lines if line.strip()]
    except Exception:
        return []


def _pick_leaves(io, repo_dir):
    leaves_dir = repo_dir / "leaves"
    all_leaves = sorted(p.name for p in leaves_dir.iterdir() if p.is_dir())
    io.print(f"\n[1/4] Documents -- {len(all_leaves)} benchmark leaves are available.")
    io.print("      Fetching pulls REAL SEC filings per leaf (no upper bound on size; a few")
    io.print("      leaves' corpora run several MB each).")
    choice = io.ask("Fetch documents for: 'all', 'none', or a comma-separated leaf list", "none")
    if choice == "none":
        return []
    if choice == "all":
        return all_leaves
    picked = [c.strip() for c in choice.split(",") if c.strip()]
    return [p for p in picked if p in all_leaves]


def _fetch_leaf_corpus(io, repo_dir, leaf_name):
    leaf_dir = repo_dir / "leaves" / leaf_name
    source_py = leaf_dir / "source.py"
    if not source_py.exists():
        io.print(f"      skip {leaf_name}: no source.py")
        return False
    result = subprocess.run([sys.executable, "source.py"], cwd=leaf_dir, capture_output=True, text=True)
    if result.returncode != 0:
        io.print(f"      FAILED {leaf_name}: {result.stderr.strip()[-200:]}")
        return False
    io.print(f"      fetched {leaf_name}")
    return True


def _pick_models(io):
    io.print("\n[2/4] Models -- which model(s) do you want to benchmark with?")
    local = _detect_ollama_models()
    if local:
        io.print(f"      Ollama detected, locally pulled: {', '.join(local)}")
    else:
        io.print("      No local Ollama models detected (Ollama not running, or none pulled).")
    io.print("      Hosted options: deepseek, gemini")
    choice = io.ask(
        "Enter provider(s), comma-separated (e.g. 'deepseek' or an Ollama model name)", "deepseek"
    )
    return [c.strip() for c in choice.split(",") if c.strip()]


def _collect_and_verify_key(io, provider, repo_dir):
    env_var = cfgmod.PROVIDER_ENV_VARS.get(provider)
    if env_var is None:
        return  # a local Ollama model name, not a hosted provider -- no key needed.

    io.print(f"\n[3/4] API key for {provider} ({env_var})")
    existing = cfgmod.resolve_secret(env_var)
    if existing:
        io.print(f"      found existing {env_var} ({cfgmod.mask(existing)})")
        if not io.confirm("      Use it?", default=True):
            existing = None
    if not existing:
        use_ref = io.confirm(
            f"      Reference an existing shell env var instead of storing the raw key?",
            default=False,
        )
        if use_ref:
            ref_name = io.ask("      Env var name to reference", env_var)
            cfgmod.save_secret_ref(env_var, ref_name)
        else:
            raw = io.ask_secret(f"      Paste your {env_var}")
            if not raw:
                io.print(f"      skipped -- {provider} will be unavailable until you run onboard again.")
                return
            cfgmod.save_secret_value(env_var, raw)

    io.print(f"      verifying {env_var}...")
    ok, detail = _verify_key(provider, repo_dir)
    if ok:
        io.print(f"      OK -- {provider} key is valid.")
    else:
        io.print(f"      FAILED -- {detail}. Key stored, but {provider} will error until fixed.")


def _verify_key(provider, repo_dir):
    """Fail closed: make one minimal real call, never assume a stored key works."""
    engine_dir = repo_dir / "engine"
    sys.path.insert(0, str(engine_dir))
    try:
        import importlib
        models_mod = importlib.import_module("models")
        client_cls = {"deepseek": models_mod.DeepSeekClient, "gemini": models_mod.GeminiClient}.get(provider)
        if client_cls is None:
            return False, f"unknown provider '{provider}'"
        client = client_cls()
        client.generate("Reply with the single word: ok", temperature=0.1)
        return True, ""
    except Exception as e:
        return False, str(e)
    finally:
        if str(engine_dir) in sys.path:
            sys.path.remove(str(engine_dir))


def run_onboarding(io=None):
    io = io or TerminalIO()
    existing = cfgmod.load_config()
    if existing:
        io.print("Existing ~/.probity/config.json found.")
        if not io.confirm("Reconfigure from scratch?", default=False):
            io.print("Keeping existing config. Run `probity-bench onboard` again anytime.")
            return existing

    io.print("Probity onboarding -- 4 quick steps.\n")
    repo_dir = ensure_materialized()

    fetched = []
    for leaf in _pick_leaves(io, repo_dir):
        if _fetch_leaf_corpus(io, repo_dir, leaf):
            fetched.append(leaf)

    providers = _pick_models(io)
    for p in providers:
        _collect_and_verify_key(io, p, repo_dir)

    cfg = {
        "models": providers,
        "leaves_with_corpus": fetched,
        "version": 1,
    }
    io.print("\n[4/4] Saving ~/.probity/config.json")
    cfgmod.save_config(cfg)

    io.print("\nDone. Try:")
    io.print("  probity-bench demo       # the wobble replay, zero config")
    io.print("  probity-bench results    # the 2 summary tables")
    io.print("  probity-bench list       # every leaf + corpus status")
    io.print("  probity-bench run <leaf> # benchmark one leaf with your configured models")
    return cfg
