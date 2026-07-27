"""
Location: tests/test_run_log.py
Purpose: Pin results/run_log.py. This file reports SPEND and COVERAGE, so its failure mode is a
         confident wrong number in the paper's audit trail. The load-bearing checks: a duplicate
         checkpoint record is counted once toward coverage but still disclosed; a shortfall is
         reported in bold rather than smoothed away; an UNMEASURABLE direct-API spend is excluded
         from the total instead of silently added as zero; and the log states what it does not
         measure rather than printing a zero that reads as "nothing happened".
Functions: TestCallStatsAgainstRealDisk, TestDuplicateRecordsAreCountedOnceAndDisclosed,
           TestLedgerSemantics, TestUnmeasurableSpendIsNotZero, TestHonestyOfTheLog
Imports: json, sys, pytest, pathlib, run_log
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "results"))
sys.path.insert(0, str(ROOT / "engine"))

import run_log  # noqa: E402


class TestCallStatsAgainstRealDisk:
    def test_a_complete_legacy_model_owes_nothing(self):
        s = run_log.call_stats("mistral-large-or", None)
        assert s["expected"] == 9400
        assert s["distinct"] == 9400
        assert s["short_by"] == 0

    def test_the_backfilled_model_now_reports_no_shortfall(self):
        """haiku had lost 283 calls to the flat cost cap; the backfill (2026-07-27) recovered
        them. The ability to REPORT a shortfall is pinned on synthetic data in
        TestDuplicateRecordsAreCountedOnceAndDisclosed and by the bold-a-shortfall test below."""
        s = run_log.call_stats("haiku-4.5-direct", None)
        assert s["expected"] == 9400
        assert s["distinct"] == 9400
        assert s["short_by"] == 0

    def test_expected_comes_from_the_oracle_not_from_the_records(self):
        """Every model owes the same 9,400 regardless of what it recorded -- that is what makes
        the shortfall visible. If `expected` were derived from the data it would always match."""
        for label in ("mistral-large-or", "haiku-4.5-direct", "gemini3-flash-or"):
            assert run_log.call_stats(label, None)["expected"] == 9400

    def test_an_unrun_model_reports_zero_recorded_not_a_crash(self):
        s = run_log.call_stats("minimax-m2.5-or", 0.42)
        assert s["distinct"] == 0
        assert s["short_by"] == 9400


class TestDuplicateRecordsAreCountedOnceAndDisclosed:
    def test_a_resumed_cell_counts_once_toward_coverage_but_is_still_reported(self, tmp_path,
                                                                              monkeypatch):
        """A resume-safe WRITER does not make a resume-safe READER. The same (instance, run) key
        appended twice must not inflate coverage -- and must not vanish from the report either."""
        leaf = tmp_path / "fake"
        leaf.mkdir()
        (leaf / "oracle.jsonl").write_text(json.dumps({"id": "q0", "f": "x"}) + "\n")
        recs = [{"instance_idx": 0, "run_idx": r} for r in range(20)]
        recs.append({"instance_idx": 0, "run_idx": 0})          # the re-appended retry
        (leaf / "runs_lbl.jsonl").write_text(
            "".join(json.dumps(r) + "\n" for r in recs))
        monkeypatch.setattr(run_log.ag, "built_leaves", lambda: [{"leaf": "fake"}])
        monkeypatch.setattr(run_log, "ROOT", tmp_path)
        s = run_log.call_stats("lbl", None)
        assert s["records"] == 21
        assert s["distinct"] == 20      # coverage is NOT inflated by the duplicate
        assert s["duplicates"] == 1     # but the resume is disclosed
        assert s["short_by"] == 0


class TestLedgerSemantics:
    def _ledger(self, tmp_path, monkeypatch, rows):
        p = tmp_path / "run_ledger.jsonl"
        p.write_text("".join(json.dumps(r) + "\n" for r in rows))
        monkeypatch.setattr(run_log, "LEDGER", p)

    def test_rows_from_another_arm_are_ignored(self, tmp_path, monkeypatch):
        self._ledger(tmp_path, monkeypatch, [
            {"label": "a", "client": "openrouter", "temperature": 0.7, "exit_code": 0,
             "seconds": 10, "measured_spend_usd": 1.0},
            {"label": "b", "client": "openrouter", "temperature": 0.1, "exit_code": 0,
             "seconds": 20, "measured_spend_usd": 2.0},
        ])
        assert [r["label"] for r in run_log.ledger_for(0.1)] == ["b"]

    def test_a_rerun_accumulates_spend_and_time_but_not_coverage(self, tmp_path, monkeypatch):
        """A model re-run to fill holes really did spend twice. Coverage is the LATEST state;
        cost and wall-clock are the SUM. Reporting the latest spend would understate the bill."""
        self._ledger(tmp_path, monkeypatch, [
            {"label": "a", "client": "openrouter", "temperature": 0.1, "exit_code": 1,
             "seconds": 100, "recorded": 9000, "owed": 9400, "measured_spend_usd": 3.0},
            {"label": "a", "client": "openrouter", "temperature": 0.1, "exit_code": 0,
             "seconds": 50, "recorded": 9400, "owed": 9400, "measured_spend_usd": 0.5},
        ])
        row, = run_log.ledger_for(0.1)
        assert row["total_spend_usd"] == 3.5
        assert row["total_seconds"] == 150.0
        assert row["recorded"] == 9400       # latest, not summed
        assert row["exit_code"] == 0
        assert row["runs"] == 2

    def test_a_missing_ledger_is_empty_not_an_error(self, tmp_path, monkeypatch):
        monkeypatch.setattr(run_log, "LEDGER", tmp_path / "nope.jsonl")
        assert run_log.ledger_for(0.1) == []


class TestUnmeasurableSpendIsNotZero:
    def test_direct_api_spend_is_excluded_from_the_total_not_added_as_zero(self, tmp_path,
                                                                           monkeypatch):
        """Anthropic exposes no balance endpoint here. Treating None as 0.0 would print a total
        that looks complete while silently omitting a model's entire cost."""
        p = tmp_path / "run_ledger.jsonl"
        p.write_text("".join(json.dumps(r) + "\n" for r in [
            {"label": "or-model", "client": "openrouter", "temperature": 0.1, "exit_code": 0,
             "seconds": 60, "measured_spend_usd": 1.25},
            {"label": "haiku-4.5-direct", "client": "anthropic", "temperature": 0.1,
             "exit_code": 0, "seconds": 60, "measured_spend_usd": None},
        ]))
        monkeypatch.setattr(run_log, "LEDGER", p)
        table = run_log.spend_table(0.1)
        assert "**$1.25**" in table
        assert "no readable balance" in table
        assert "haiku-4.5-direct" in table
        assert "$0.00" not in table


class TestHonestyOfTheLog:
    def test_the_log_names_what_it_does_not_measure(self):
        text = run_log.build_log(None)
        assert "What is NOT measured here" in text
        assert "retries" in text.lower()

    def test_an_arm_with_no_ledger_says_so_rather_than_showing_a_zero_total(self):
        text = run_log.build_log(None)
        assert "No ledger rows for this arm" in text
        assert "TOTAL (measured)" not in text

    def test_a_complete_arm_shows_a_dash_not_a_fake_shortfall(self):
        """The total is derived, not typed: 60 leaves x 20 runs x the oracle's item count, summed
        over the lineup. Hardcoding 103400 meant this went red on the day a 12th model legitimately
        joined -- a red that reports nothing except that the literal is stale."""
        import sys as _sys
        _sys.path.insert(0, str(ROOT / "results"))
        import aggregate as ag
        calls = run_log.ag.model_counts(None) and 9400 * len(ag.canonical_lineup())
        text = run_log.build_log(None)
        assert f"| **TOTAL** | **{calls}** | **{calls}** | **—** |" in text

    def test_a_shortfall_would_be_bolded_if_one_existed(self, monkeypatch):
        """Positive control. The legacy arm is now whole, so the real data can no longer exercise
        the bold-a-shortfall path -- and a formatter that never fires is indistinguishable from a
        broken one. Drive it with an injected short cell instead."""
        monkeypatch.setattr(run_log, "call_stats",
                            lambda label, temp: {"expected": 9400, "distinct": 9117,
                                                  "short_by": 283, "duplicates": 0,
                                                  "errors": 0, "unparsed": 0})
        text = run_log.stats_table(None, ["haiku-4.5-direct"])
        assert "**283**" in text


class TestReconstructedSpendIsLabelled:
    def test_an_operator_supplied_balance_is_daggered_and_footnoted(self, tmp_path, monkeypatch):
        """A reconstructed figure must be visibly distinguishable from a sampled one. If both
        render identically the table quietly claims a measurement it did not make."""
        p = tmp_path / "run_ledger.jsonl"
        p.write_text("".join(json.dumps(r) + "\n" for r in [
            {"label": "sampled-or", "client": "openrouter", "temperature": 0.1, "exit_code": 0,
             "seconds": 60, "measured_spend_usd": 1.00},
            {"label": "gpt-oss-120b-or", "client": "openrouter", "temperature": 0.1,
             "exit_code": 0, "seconds": 60, "measured_spend_usd": 0.50,
             "provenance": "reconstructed"},
        ]))
        monkeypatch.setattr(run_log, "LEDGER", p)
        table = run_log.spend_table(0.1)
        assert "$0.5000 †" in table
        assert "$1.0000 †" not in table, "a sampled row must NOT be daggered"
        assert "recorded by the operator rather than sampled" in table
        assert "**$1.50**" in table, "a reconstructed row still counts toward the total"

    def test_no_dagger_and_no_footnote_when_every_row_is_sampled(self, tmp_path, monkeypatch):
        p = tmp_path / "run_ledger.jsonl"
        p.write_text(json.dumps({"label": "a", "client": "openrouter", "temperature": 0.1,
                                  "exit_code": 0, "seconds": 60,
                                  "measured_spend_usd": 1.0}) + "\n")
        monkeypatch.setattr(run_log, "LEDGER", p)
        table = run_log.spend_table(0.1)
        assert "†" not in table
