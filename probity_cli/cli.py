"""
Location: probity_cli/cli.py
Purpose: `probity-bench` console-script entry point. Subcommands: onboard, demo, results, list, run.
Functions: main(), cmd_demo(), cmd_results(), cmd_list(), cmd_run()
Calls: probity_cli.onboard, probity_cli.materialize, probity_cli.config, subprocess
Imports: argparse, sys, subprocess, importlib.util, pathlib, probity_cli.*
"""

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

from probity_cli import __version__
from probity_cli.config import load_config, resolve_secret, PROVIDER_ENV_VARS
from probity_cli.materialize import ensure_materialized
from probity_cli.onboard import run_onboarding


def _load_render_module(repo_dir):
    spec = importlib.util.spec_from_file_location("probity_render", repo_dir / "results" / "render.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cmd_onboard(args):
    run_onboarding()


def cmd_demo(args):
    repo_dir = ensure_materialized()
    demo_py = repo_dir / "demo" / "wobble_demo.py"
    subprocess.run([sys.executable, str(demo_py)])


def cmd_results(args):
    repo_dir = ensure_materialized()
    render = _load_render_module(repo_dir)
    print(render.suite_summary_table())
    print()
    print(render.family_summary_table())


def cmd_list(args):
    repo_dir = ensure_materialized()
    cfg = load_config()
    fetched = set(cfg.get("leaves_with_corpus", []))
    leaves_dir = repo_dir / "leaves"
    for leaf in sorted(p.name for p in leaves_dir.iterdir() if p.is_dir()):
        has_corpus = (leaves_dir / leaf / "corpus").is_dir()
        mark = "x" if has_corpus or leaf in fetched else " "
        print(f"[{mark}] {leaf}")


def cmd_run(args):
    repo_dir = ensure_materialized()
    leaf_dir = repo_dir / "leaves" / args.leaf
    if not leaf_dir.is_dir():
        print(f"error: no such leaf '{args.leaf}' (see `probity-bench list`)", file=sys.stderr)
        sys.exit(1)

    import os
    env = os.environ.copy()
    for provider, var in PROVIDER_ENV_VARS.items():
        value = resolve_secret(var)
        if value:
            env[var] = value

    if not (leaf_dir / "corpus").is_dir():
        print(f"no local corpus for '{args.leaf}' yet -- fetching via source.py...")
        subprocess.run([sys.executable, "source.py"], cwd=leaf_dir, env=env, check=True)

    subprocess.run([sys.executable, "run.py"], cwd=leaf_dir, env=env, check=True)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="probity-bench", description="Probity: an LLM reliability benchmark for real fundraising documents.")
    parser.add_argument("--version", action="version", version=f"probity-bench {__version__}")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("onboard", help="interactive setup: documents, models, API keys").set_defaults(func=cmd_onboard)
    sub.add_parser("demo", help="zero-config wobble replay (real recorded model runs)").set_defaults(func=cmd_demo)
    sub.add_parser("results", help="print the 2 summary tables (by model, by category)").set_defaults(func=cmd_results)
    sub.add_parser("list", help="list every leaf + local corpus status").set_defaults(func=cmd_list)
    run_p = sub.add_parser("run", help="benchmark one leaf with your configured models")
    run_p.add_argument("leaf")
    run_p.set_defaults(func=cmd_run)

    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 1
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
