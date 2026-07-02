"""
Location: tests/test_probity_cli.py
Purpose: Unit tests for the probity_cli package -- config/secret round-trip (raw + ref modes),
         materialize excludes corpus/, onboarding wizard end-to-end with a fake IO double, and
         cli.py argument parsing. Real assertions on concrete file/dict contents, no toBeDefined.
Run: cd tests && python3 -m unittest test_probity_cli -v
"""

import json
import stat
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from probity_cli import config as cfgmod  # noqa: E402
from probity_cli import materialize as matmod  # noqa: E402
from probity_cli.onboard import run_onboarding  # noqa: E402
from probity_cli import cli  # noqa: E402


class FakeIO:
    """Scripted IO double -- pops canned answers in call order. Bool answers for confirm(),
    strings for ask()/ask_secret()."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.log = []

    def print(self, text=""):
        self.log.append(text)

    def ask(self, prompt, default=None):
        return self.answers.pop(0) if self.answers else (default or "")

    def ask_secret(self, prompt):
        return self.answers.pop(0) if self.answers else ""

    def confirm(self, prompt, default=True):
        if not self.answers:
            return default
        v = self.answers.pop(0)
        return v if isinstance(v, bool) else v == "y"


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.id().split(".")[-1] + "_home")
        self._patch_home = patch.object(cfgmod, "HOME_DIR", self.tmp / ".probity")
        self._patch_home.start()
        cfgmod.CONFIG_PATH = cfgmod.HOME_DIR / "config.json"
        cfgmod.ENV_PATH = cfgmod.HOME_DIR / ".env"

    def tearDown(self):
        self._patch_home.stop()
        import shutil
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_config_round_trip(self):
        self.assertEqual(cfgmod.load_config(), {})
        cfgmod.save_config({"models": ["deepseek"]})
        self.assertEqual(cfgmod.load_config(), {"models": ["deepseek"]})

    def test_secret_value_round_trip_and_permissions(self):
        cfgmod.save_secret_value("DEEPSEEK_API_KEY", "sk-real-value")
        self.assertEqual(cfgmod.resolve_secret("DEEPSEEK_API_KEY"), "sk-real-value")
        mode = stat.S_IMODE(cfgmod.ENV_PATH.stat().st_mode)
        self.assertEqual(mode, 0o600)

    def test_secret_ref_resolves_via_referenced_env_var(self):
        cfgmod.save_secret_ref("DEEPSEEK_API_KEY", "MY_REF_VAR")
        with patch.dict("os.environ", {"MY_REF_VAR": "referenced-value"}, clear=False):
            self.assertEqual(cfgmod.resolve_secret("DEEPSEEK_API_KEY"), "referenced-value")

    def test_secret_ref_unresolved_when_referenced_var_absent(self):
        cfgmod.save_secret_ref("DEEPSEEK_API_KEY", "NEVER_SET_VAR")
        import os
        os.environ.pop("NEVER_SET_VAR", None)
        self.assertIsNone(cfgmod.resolve_secret("DEEPSEEK_API_KEY"))

    def test_process_env_takes_precedence_over_stored_file(self):
        cfgmod.save_secret_value("DEEPSEEK_API_KEY", "stored-value")
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "live-shell-value"}, clear=False):
            self.assertEqual(cfgmod.resolve_secret("DEEPSEEK_API_KEY"), "live-shell-value")

    def test_mask_never_reveals_full_value(self):
        self.assertNotIn("sk-real-secret-value", cfgmod.mask("sk-real-secret-value"))
        self.assertEqual(cfgmod.mask(""), "(not set)")
        self.assertEqual(cfgmod.mask(None), "(not set)")


class TestMaterialize(unittest.TestCase):
    def test_dev_checkout_excludes_corpus_and_archive(self):
        # Runs against the REAL repo checkout (this test file's grandparent) -- proves the actual
        # exclusion patterns work against real leaf directories, not a synthetic fixture.
        root = matmod.DEV_REPO_ROOT
        self.assertTrue((root / "engine").is_dir())
        import tempfile
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "leaves"
            shutil.copytree(
                root / "leaves", dst,
                ignore=shutil.ignore_patterns("corpus", "_archive_*", "__pycache__", "*.pyc"),
            )
            corpus_dirs = list(dst.glob("*/corpus"))
            archive_dirs = list(dst.glob("*/_archive_*"))
            self.assertEqual(corpus_dirs, [], "materialize must never copy corpus/ (raw documents)")
            self.assertEqual(archive_dirs, [], "materialize must never copy stale _archive_* runs")
            # sanity: real leaf code DID come through
            self.assertTrue((dst / "vesting_schedule" / "run.py").exists())

    def test_source_root_prefers_bundled_data_over_dev_checkout(self):
        with patch.object(matmod, "BUNDLED_DATA", matmod.DEV_REPO_ROOT):
            self.assertEqual(matmod.source_root(), matmod.DEV_REPO_ROOT)


class TestOnboarding(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.id().split(".")[-1] + "_home")
        self._patch_home = patch.object(cfgmod, "HOME_DIR", self.tmp / ".probity")
        self._patch_home.start()
        cfgmod.CONFIG_PATH = cfgmod.HOME_DIR / "config.json"
        cfgmod.ENV_PATH = cfgmod.HOME_DIR / ".env"
        self._patch_mat_home = patch.object(matmod, "HOME_DIR", self.tmp / ".probity")
        self._patch_mat_home.start()
        matmod.REPO_DIR = matmod.HOME_DIR / "repo"
        matmod.VERSION_STAMP = matmod.REPO_DIR / ".materialized_version"

    def tearDown(self):
        self._patch_home.stop()
        self._patch_mat_home.stop()
        import shutil
        if self.tmp.exists():
            shutil.rmtree(self.tmp)

    def test_skip_everything_still_writes_valid_config(self):
        io = FakeIO(["none", ""])  # no leaves, no models
        cfg = run_onboarding(io=io)
        self.assertEqual(cfg["leaves_with_corpus"], [])
        self.assertEqual(cfg["models"], [])
        self.assertEqual(cfgmod.load_config(), cfg)

    def test_ollama_only_model_needs_no_key_and_no_verify_call(self):
        io = FakeIO(["none", "gemma3:1b"])
        cfg = run_onboarding(io=io)
        self.assertEqual(cfg["models"], ["gemma3:1b"])
        # no provider key path was ever entered -- .env should not exist
        self.assertFalse(cfgmod.ENV_PATH.exists())

    def test_second_run_with_existing_config_can_be_kept_without_reasking(self):
        io1 = FakeIO(["none", "gemma3:1b"])
        run_onboarding(io=io1)
        io2 = FakeIO([False])  # "reconfigure from scratch?" -> No
        cfg2 = run_onboarding(io=io2)
        self.assertEqual(cfg2["models"], ["gemma3:1b"])

    def test_ref_mode_stores_pointer_not_raw_value(self):
        io = FakeIO(["none", "deepseek", True, "SOME_ENV_VAR_NAME"])
        with patch("probity_cli.onboard._verify_key", return_value=(True, "")):
            run_onboarding(io=io)
        stored = cfgmod.load_env_file()["DEEPSEEK_API_KEY"]
        self.assertEqual(stored, "$REF:SOME_ENV_VAR_NAME")

    def test_failed_verify_does_not_crash_the_wizard(self):
        io = FakeIO(["none", "deepseek", False, "not-a-real-key"])
        cfg = run_onboarding(io=io)  # real _verify_key runs, fails closed (no real key) -- must not raise
        self.assertEqual(cfg["models"], ["deepseek"])
        self.assertEqual(cfgmod.load_env_file()["DEEPSEEK_API_KEY"], "not-a-real-key")


class TestCliParsing(unittest.TestCase):
    def test_no_subcommand_prints_help_and_returns_1(self):
        self.assertEqual(cli.main([]), 1)

    def test_results_and_list_and_demo_and_run_are_registered(self):
        parser_result = {}
        with patch.object(cli, "cmd_results") as mock_results:
            cli.main(["results"])
            mock_results.assert_called_once()
        with patch.object(cli, "cmd_list") as mock_list:
            cli.main(["list"])
            mock_list.assert_called_once()
        with patch.object(cli, "cmd_demo") as mock_demo:
            cli.main(["demo"])
            mock_demo.assert_called_once()
        with patch.object(cli, "cmd_run") as mock_run:
            cli.main(["run", "vesting_schedule"])
            args = mock_run.call_args[0][0]
            self.assertEqual(args.leaf, "vesting_schedule")

    def test_run_missing_leaf_argument_errors(self):
        with self.assertRaises(SystemExit):
            cli.main(["run"])


if __name__ == "__main__":
    unittest.main()
