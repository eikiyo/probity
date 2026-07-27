"""
Location: tests/test_backfill.py
Purpose: Pin engine/backfill.py. The load-bearing behaviours are: (1) a backfill NEVER becomes a
         sweep -- a cell with zero recorded calls is skipped, not launched; (2) it finds exactly the
         cells that are short against the ORACLE, not against their own data; (3) the label -> client
         mapping is resolved from the single LINEUP definition and fails closed on an unknown label;
         and (4) the closure that builds the client is bound per-label, so a set built for one model
         cannot silently call another.
Functions: TestModelSetForResolvesTheRightClient, TestFindHolesAgainstRealDisk,
           TestFindHolesSkipsUnrunCells, TestHoleArithmetic
Imports: json, sys, pytest, pathlib, backfill
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "engine"))

import backfill  # noqa: E402
import coverage  # noqa: E402


class TestModelSetForResolvesTheRightClient:
    def test_hosted_label_has_no_ollama_unload_model(self):
        """A None ollama_model is what tells run_model to skip `ollama stop`. A hosted label
        carrying its model id here would shell out to unload a model that was never loaded."""
        (label, ollama_model, _factory), = backfill.model_set_for("haiku-4.5-direct")
        assert label == "haiku-4.5-direct"
        assert ollama_model is None

    def test_local_label_carries_its_ollama_model_for_unload(self):
        (_label, ollama_model, _factory), = backfill.model_set_for("gemma3-1b")
        assert ollama_model == "gemma3:1b"

    def test_unknown_label_fails_closed_rather_than_defaulting(self):
        """A backfill that silently picked a default client would re-run a cell on the WRONG
        provider, breaking the parity the whole experiment rests on."""
        with pytest.raises(SystemExit) as e:
            backfill.model_set_for("gpt-9-ultra-or")
        assert "gpt-9-ultra-or" in str(e.value)

    def test_factory_is_bound_per_label_not_to_the_last_loop_iteration(self):
        """The classic late-binding trap: a lambda closing over the loop variable would build the
        LAST model in LINEUP no matter which label was asked for. Pinned by recording what
        build_client is actually called with, for a label that is NOT last in the list."""
        seen = []
        orig = backfill.preflight.build_client
        backfill.preflight.build_client = lambda kind, mid: seen.append((kind, mid))
        try:
            (_l, _o, factory), = backfill.model_set_for("deepseek-v4f")
            factory()
        finally:
            backfill.preflight.build_client = orig
        assert seen == [("deepseek", "deepseek-v4-flash")]
        assert backfill.preflight.LINEUP[-1][0] != "deepseek-v4f", \
            "test is vacuous if the label under test is the last LINEUP entry"


class TestFindHolesSkipsUnrunCells:
    def test_a_cell_with_zero_recorded_calls_is_not_a_hole(self, tmp_path):
        """A never-run cell is a SWEEP's job. If a backfill treated it as a hole it would launch
        the full 9,400-call arm under the name 'filling 357 calls' -- an unbounded spend the
        operator never approved."""
        leaf = tmp_path / "fake_leaf"
        (leaf / "corpus" / "questions").mkdir(parents=True)
        (leaf / "oracle.jsonl").write_text(
            "".join(json.dumps({"id": f"q{i}", "f": "x"}) + "\n" for i in range(3)))
        backfill.built_leaf_dirs = lambda: [leaf]
        try:
            assert backfill.find_holes(["haiku-4.5-direct"], None) == []
        finally:
            import importlib
            importlib.reload(backfill)

    def test_a_partially_recorded_cell_is_a_hole(self, tmp_path):
        leaf = tmp_path / "fake_leaf"
        leaf.mkdir(parents=True)
        (leaf / "oracle.jsonl").write_text(
            "".join(json.dumps({"id": f"q{i}", "f": "x"}) + "\n" for i in range(2)))
        # owes 2 items x 20 runs = 40; record 5
        coverage.checkpoint_path(leaf, "haiku-4.5-direct").write_text(
            "".join(json.dumps({"instance_idx": 0, "run_idx": r}) + "\n" for r in range(5)))
        backfill.built_leaf_dirs = lambda: [leaf]
        try:
            holes = backfill.find_holes(["haiku-4.5-direct"], None)
            assert len(holes) == 1
            assert holes[0]["recorded"] == 5
            assert holes[0]["expected"] == 40
            assert holes[0]["short_by"] == 35
        finally:
            import importlib
            importlib.reload(backfill)


class TestFindHolesAgainstRealDisk:
    """The five cells the flat per-leaf cost cap truncated were BACKFILLED on 2026-07-27 (357
    calls). This class used to assert those five holes existed; reality legitimately advanced, so
    it now asserts the NEW truth -- the arm is whole. The hole-DETECTION capability it used to
    prove is not lost: TestFindHolesSkipsUnrunCells drives it on a synthetic short cell, which
    cannot rot when the real data changes again."""

    def _holes(self):
        labels = [l for l, _, _ in backfill.preflight.LINEUP]
        return {(h["leaf"].name, h["label"]): (h["recorded"], h["expected"])
                for h in backfill.find_holes(labels, None)}

    BACKFILLED = [
        ("pre_vs_post_money", "gemini3-flash-or", 380),
        ("participation_type", "gemini3-flash-or", 360),
        ("safe_cap_vs_discount_applies", "haiku-4.5-direct", 260),
        ("safe_pre_post", "haiku-4.5-direct", 320),
        ("safe_pro_rata_side_letter", "haiku-4.5-direct", 300),
    ]

    def test_the_legacy_arm_has_no_holes_left(self):
        assert self._holes() == {}

    def test_each_formerly_truncated_cell_is_now_exactly_full(self):
        """Named individually so a REGRESSION on any one of them is reported by name, rather than
        hiding inside an aggregate 'no holes' assertion."""
        for leaf, label, expected in self.BACKFILLED:
            cell = coverage.cell_status(ROOT / "leaves" / leaf, label, 20)
            assert cell["recorded"] == expected, f"{leaf}/{label}"
            assert cell["complete"]

    def test_every_lineup_model_now_owes_nothing_across_the_whole_arm(self):
        for label, _k, _m in backfill.preflight.LINEUP:
            total = sum(coverage.cell_status(d, label, 20)["short_by"]
                        for d in backfill.built_leaf_dirs())
            if any(coverage.cell_status(d, label, 20)["recorded"] for d in backfill.built_leaf_dirs()):
                assert total == 0, f"{label} is {total} calls short"


class TestHoleArithmetic:
    def test_short_by_is_expected_minus_recorded(self):
        labels = [l for l, _, _ in backfill.preflight.LINEUP]
        for h in backfill.find_holes(labels, None):
            assert h["short_by"] == h["expected"] - h["recorded"]
            assert h["short_by"] > 0

    # The zero-recorded vs partially-recorded distinction is pinned by
    # TestFindHolesSkipsUnrunCells above, which builds REAL leaf fixtures and drives the real
    # coverage.cell_status. A live-state test used to sit here asserting that "mistral-large-or"
    # had no t01 holes; that was a test of the sweep's progress, not of find_holes -- it passed
    # while mistral was unstarted and went red the hour it began, having found no defect. It was
    # removed rather than re-pointed at another not-yet-started label, which would only reset the
    # same fuse.
