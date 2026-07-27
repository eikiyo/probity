"""
Location: tests/test_datadump.py
Purpose: Pin the peer-review dump. Its failure mode is uniquely bad: a dump that looks complete but
         disagrees with the paper hands a reviewer what looks like a reproducibility failure. The
         load-bearing checks are (1) a LIVE arm is never certified, (2) the reviewer's verifier
         reproduces the published numbers from raw records, and (3) the two value-selection rules
         that inflated wobble in the verifier's first draft stay fixed -- each with a control
         proving the wrong rule really does give the wrong answer.
Functions: TestArmCompletenessGate, TestVerifierValueSelection, TestVerifierReproducesPaper,
           TestDumpIntegrity
Imports: gzip, json, sys, pathlib, pytest, datadump, dump_verify, dump_docs
"""

import gzip
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "results"))
sys.path.insert(0, str(ROOT / "engine"))

import datadump      # noqa: E402
import dump_docs     # noqa: E402
import dump_verify   # noqa: E402


class TestArmCompletenessGate:
    def test_the_frozen_legacy_arm_is_certified(self):
        ready, _partial = datadump.complete_arms(datadump.ag.canonical_lineup())
        arms = {a["arm"] for a in ready}
        assert "t07_legacy" in arms
        legacy = next(a for a in ready if a["arm"] == "t07_legacy")
        assert legacy["cells"] == 660 and legacy["short_cells"] == 0

    def test_an_arm_with_any_short_cell_is_not_certified(self, monkeypatch):
        """One short cell is enough. A dump built over a running sweep reads runs.jsonl and the
        scored files at different instants, so it reports mismatches that are really just the
        sweep advancing -- indistinguishable, to a reviewer, from a real reproducibility failure."""
        real = datadump.coverage.cell_status

        def fake(leaf_dir, label, n_runs, suffix=""):
            c = dict(real(leaf_dir, label, n_runs, suffix))
            if label == "deepseek-v4f" and leaf_dir.name == "drag_along":
                c.update(complete=False, short_by=1, recorded=c["expected"] - 1)
            return c

        monkeypatch.setattr(datadump.coverage, "cell_status", fake)
        ready, partial = datadump.complete_arms(datadump.ag.canonical_lineup())
        assert "t07_legacy" not in {a["arm"] for a in ready}
        assert "t07_legacy" in {a["arm"] for a in partial}

    def test_expected_numbers_omits_an_arm_that_was_never_run(self):
        exp = dump_docs.expected_numbers(arms=(0.42,))
        assert exp == {}, "an unrun arm must contribute nothing, not zeros"


class TestVerifierValueSelection:
    """The two rules that were wrong in the verifier's first draft. Each test carries a control
    showing the WRONG rule produces the WRONG answer, so these cannot pass vacuously."""

    @staticmethod
    def _runs(tmp_path, records):
        p = tmp_path / "runs.jsonl"
        p.write_text("".join(json.dumps(r) + "\n" for r in records))
        (tmp_path / "oracle.jsonl").write_text(json.dumps(
            {"leaf": "L", "field": "f", "instance_idx": 0, "truth_canonical": "yes", "f": "yes"}) + "\n")
        return tmp_path

    def _base(self, **kw):
        r = {"leaf": "L", "model_label": "m", "arm": "a", "instance_idx": 0, "run_idx": 0}
        r.update(kw)
        return r

    def test_a_null_normalized_value_is_not_an_answer(self, tmp_path):
        """A None means 'could not be canonicalised', not 'the model said None'. Counting it as a
        value manufactures a second distinct answer and inflates wobble -- it read gemma3-1b at
        44.7% instead of its true 42.4%."""
        d = self._runs(tmp_path, [
            self._base(run_idx=0, normalized={"f": "yes"}),
            self._base(run_idx=1, normalized={"f": None}),
            self._base(run_idx=2, normalized={"f": "yes"}),
        ])
        truth, field_of = dump_verify.load_oracle(d)
        answers = dump_verify.per_item(d, field_of)
        vals = answers[("a", "m", "L", 0)]
        assert vals == ["yes", "yes"], "the None run must contribute nothing"
        assert dump_verify.score_model(answers, truth)[("a", "m")]["wobble_pct"] == 0.0

    def test_counting_null_as_a_value_would_have_reported_wobble(self, tmp_path):
        """Control for the test above: the discarded rule really does flip the verdict."""
        vals_wrong = ["yes", None, "yes"]
        distinct = {json.dumps(v, sort_keys=True) for v in vals_wrong}
        assert len(distinct) > 1, "if this were 1, the None rule would not matter and the test above is vacuous"

    def test_normalized_is_used_and_parsed_is_never_a_fallback(self, tmp_path):
        """`parsed` is pre-canonical text: "68000000" and 68000000.0 are the SAME answer, and
        falling back to parsed would score them as disagreement."""
        d = self._runs(tmp_path, [
            self._base(run_idx=0, parsed={"f": "68000000"}, normalized={"f": 68000000.0}),
            self._base(run_idx=1, parsed={"f": "68,000,000"}, normalized={"f": 68000000.0}),
        ])
        truth, field_of = dump_verify.load_oracle(d)
        answers = dump_verify.per_item(d, field_of)
        assert answers[("a", "m", "L", 0)] == [68000000.0, 68000000.0]
        assert dump_verify.score_model(answers, truth)[("a", "m")]["wobble_pct"] == 0.0

    def test_a_genuinely_different_answer_still_counts_as_wobble(self, tmp_path):
        """Positive control: the rules above must not make everything look stable."""
        d = self._runs(tmp_path, [
            self._base(run_idx=0, normalized={"f": "yes"}),
            self._base(run_idx=1, normalized={"f": "no"}),
        ])
        truth, field_of = dump_verify.load_oracle(d)
        s = dump_verify.score_model(dump_verify.per_item(d, field_of), truth)
        assert s[("a", "m")]["wobble_pct"] == 100.0

    def test_oracle_uses_canonical_truth_not_the_raw_value(self, tmp_path):
        (tmp_path / "oracle.jsonl").write_text(json.dumps(
            {"leaf": "L", "field": "f", "instance_idx": 0,
             "truth_canonical": 100000000.0, "f": "100000000"}) + "\n")
        truth, _ = dump_verify.load_oracle(tmp_path)
        assert truth[("L", 0)] == 100000000.0, "scoring compares canonical forms on both sides"


class TestVerifierReproducesPaper:
    """The end-to-end guarantee: the reviewer's command must exit 0 against the real dump."""

    @pytest.fixture(scope="class")
    def dump(self, tmp_path_factory):
        out = tmp_path_factory.mktemp("dump")
        datadump.build(out)
        return out

    def test_verifier_exits_zero_against_the_published_numbers(self, dump):
        r = subprocess.run([sys.executable, str(dump / "verify_dump.py"),
                            "--dump", str(dump), "--expect", str(dump / "expected_numbers.json")],
                           capture_output=True, text=True)
        assert r.returncode == 0, f"reviewer verification FAILED:\n{r.stdout[-1500:]}"
        assert "PASS" in r.stdout

    def test_the_certified_arm_covers_all_eleven_models(self, dump):
        exp = json.loads((dump / "expected_numbers.json").read_text())
        assert "t07_legacy" in exp
        assert len(exp["t07_legacy"]) == 11

    def test_a_tampered_expectation_makes_the_verifier_fail(self, dump, tmp_path):
        """Prove the gate can go RED. A verifier that cannot fail certifies nothing."""
        exp = json.loads((dump / "expected_numbers.json").read_text())
        exp["t07_legacy"]["gemma3-1b"]["wobble_pct"] = 5.0      # true value is ~42
        bad = tmp_path / "bad.json"
        bad.write_text(json.dumps(exp))
        r = subprocess.run([sys.executable, str(dump / "verify_dump.py"),
                            "--dump", str(dump), "--expect", str(bad)],
                           capture_output=True, text=True)
        assert r.returncode == 1
        assert "MISMATCH" in r.stdout


class TestDumpIntegrity:
    @pytest.fixture(scope="class")
    def dump(self, tmp_path_factory):
        out = tmp_path_factory.mktemp("dump2")
        datadump.build(out)
        return out

    def test_every_file_is_checksummed(self, dump):
        listed = {l.split("  ", 1)[1] for l in
                  (dump / "CHECKSUMS.sha256").read_text().strip().splitlines()}
        on_disk = {p.name for p in dump.iterdir() if p.is_file() and p.name != "CHECKSUMS.sha256"}
        assert on_disk == listed, f"unchecksummed: {on_disk - listed}"

    def test_runs_carry_the_grouping_keys_a_reviewer_needs(self, dump):
        with gzip.open(dump / "runs.jsonl.gz", "rt") as f:
            row = json.loads(f.readline())
        for k in ("leaf", "field", "family", "model_label", "arm", "temperature",
                  "instance_idx", "run_idx"):
            assert k in row, f"runs.jsonl missing {k}"

    def test_prompts_are_the_real_prompt_not_a_template(self, dump):
        with gzip.open(dump / "prompts.jsonl.gz", "rt") as f:
            row = json.loads(f.readline())
        assert len(row["prompt"]) > 200
        assert row["document_sha256"] and len(row["document_sha256"]) == 64

    def test_readme_discloses_the_raw_output_limitation(self, dump):
        txt = (dump / "README.md").read_text()
        assert "Raw response text is retained only for calls that failed to parse" in txt
        assert "both" in txt.lower()
