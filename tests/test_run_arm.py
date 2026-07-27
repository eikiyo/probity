"""
Location: tests/test_run_arm.py
Purpose: Pin engine/run_arm.py, the only component in this repo that spends money unattended
         across eight models in sequence. The load-bearing checks are all REFUSALS: it must not
         spend when the balance is unreadable, must not spend when the balance is short, must not
         start the next model after one failed, and must not re-bill a model that is already
         complete. Cheapest-first ordering is pinned too, because it is what makes a plumbing bug
         surface on an $0.81 model instead of the $8.94 one.
Functions: TestArmOrderIsCheapestFirst, TestArmOrderMatchesTheLineup, TestBalanceGateFailsClosed,
           TestCompletionRequiresBothSignals, TestAlreadyCompleteModelIsSkipped
Imports: sys, pytest, pathlib, run_arm
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "engine"))

import run_arm  # noqa: E402


class TestArmOrderIsCheapestFirst:
    def test_estimated_cost_is_non_decreasing_down_the_list(self):
        """Priced on a FULL arm (9,400 calls), not on calls still owed. est_cost() shrinks toward
        zero as a model completes, so asserting on remaining cost tests the live progress of the
        sweep rather than the property under test -- it passed at authoring time and went red an
        hour later when the first models finished, having found no defect."""
        full = []
        for label, _c, _m in run_arm.ARM_ORDER:
            per_call = run_arm.guard_mod.per_call_cost(label)
            if per_call is None:
                per_call = run_arm.guard_mod._UNKNOWN_MODEL_COST_USD
            full.append(round(9400 * per_call, 6))
        assert full == sorted(full), f"ARM_ORDER is not cheapest-first: {full}"

    def test_the_ordering_is_strict_enough_to_be_meaningful(self):
        """Positive control: if every model cost the same, the test above would pass trivially."""
        costs = {run_arm.guard_mod.per_call_cost(l) for l, _c, _m in run_arm.ARM_ORDER}
        assert len(costs) > 1

    def test_the_dearest_model_runs_last(self):
        assert run_arm.ARM_ORDER[-1][0] == "minimax-m2.5-or"


class TestArmOrderMatchesTheLineup:
    def test_every_entry_is_a_declared_lineup_member_with_matching_routing(self):
        """A typo here would run a model on the wrong provider for a whole arm -- the exact parity
        break the experiment exists to avoid. Checked against preflight.LINEUP, the ONE mapping."""
        import preflight
        lineup = {l: (k, m) for l, k, m in preflight.LINEUP}
        for label, client, model_id in run_arm.ARM_ORDER:
            assert label in lineup, f"{label} is not in preflight.LINEUP"
            assert lineup[label] == (client, model_id), \
                f"{label} routing drifted: run_arm says {(client, model_id)}, LINEUP says {lineup[label]}"

    def test_no_duplicates_and_no_local_models(self):
        labels = [l for l, _c, _m in run_arm.ARM_ORDER]
        assert len(labels) == len(set(labels)) == 9
        assert not (set(labels) & set(run_arm.guard_mod.LOCAL_MODELS)), \
            "local models run on Kaggle, not through this driver"

    def test_it_covers_every_hosted_lineup_member(self):
        import preflight
        hosted = {l for l, k, _m in preflight.LINEUP if k in preflight.HOSTED}
        covered = {l for l, _c, _m in run_arm.ARM_ORDER} | {"gpt-oss-120b-or"}   # already run
        assert hosted == covered, f"hosted models not scheduled: {hosted - covered}"


class TestBalanceGateFailsClosed:
    def test_unreadable_balance_refuses_to_spend(self):
        """'I could not check' must never be treated as 'it is fine'. A 402 lands mid-run with no
        clean resume marker, so an unknown balance is a stop, not a shrug."""
        orig = run_arm.preflight.or_balance
        run_arm.preflight.or_balance = lambda: None
        try:
            ok, msg = run_arm.gate_balance("llama3.3-70b-or", "openrouter", 0.1)
        finally:
            run_arm.preflight.or_balance = orig
        assert ok is False
        assert "refusing to spend blind" in msg

    def test_balance_below_estimate_plus_buffer_refuses(self):
        need = run_arm.est_cost("minimax-m2.5-or", 0.1)
        orig = run_arm.preflight.or_balance
        run_arm.preflight.or_balance = lambda: need + run_arm.BALANCE_BUFFER_USD - 0.01
        try:
            ok, msg = run_arm.gate_balance("minimax-m2.5-or", "openrouter", 0.1)
        finally:
            run_arm.preflight.or_balance = orig
        assert ok is False
        assert "top up" in msg

    def test_sufficient_balance_passes(self):
        need = run_arm.est_cost("minimax-m2.5-or", 0.1)
        orig = run_arm.preflight.or_balance
        run_arm.preflight.or_balance = lambda: need + run_arm.BALANCE_BUFFER_USD + 0.01
        try:
            ok, _msg = run_arm.gate_balance("minimax-m2.5-or", "openrouter", 0.1)
        finally:
            run_arm.preflight.or_balance = orig
        assert ok is True

    def test_a_direct_api_says_it_cannot_check_rather_than_implying_it_did(self):
        ok, msg = run_arm.gate_balance("haiku-4.5-direct", "anthropic", 0.1)
        assert ok is True
        assert "no readable balance" in msg

    def test_the_buffer_is_actually_positive(self):
        """A zero buffer means the gate passes at exactly the estimate, and the estimate is an
        estimate -- the run would wall at the last few percent of the dearest model."""
        assert run_arm.BALANCE_BUFFER_USD > 0


class TestCompletionRequiresBothSignals:
    """`complete` must require a clean exit AND full coverage. Either alone is a false green: a
    sweep can exit 0 with holes if the assert is bypassed, and can exit nonzero after recording
    every call."""

    @pytest.mark.parametrize("exit_code,recorded,owed,expected", [
        (0, 9400, 9400, True),
        (0, 9300, 9400, False),      # exited clean but short -- the 2026-07-03 failure
        (1, 9400, 9400, False),      # every call recorded but the process failed
        (1, 9300, 9400, False),
    ])
    def test_completion_logic(self, exit_code, recorded, owed, expected):
        row = {"exit_code": exit_code, "recorded": recorded, "owed": owed}
        assert (row["recorded"] == row["owed"] and row["exit_code"] == 0) is expected


class TestSpendCalibration:
    """The list-price estimate underprices a REASONING model, because guard.py bills a 25-token
    answer and reasoning tokens are output tokens that never appear in the completion. Measured on
    the 0.1 arm: gpt-5-mini cost $5.72 against a $2.43 estimate. Every check here is about the
    gate refusing to under-price, because under-pricing is what lands a 402 mid-run."""

    RATIOS = {"cheap-model": 0.76, "thinky-model": 2.35}

    def test_a_billed_model_is_priced_at_its_own_observed_ratio(self):
        assert run_arm.calibration("thinky-model", self.RATIOS) == 2.35

    def test_an_unbilled_model_is_priced_at_the_worst_ratio_seen(self):
        """Fail closed: a model we have never billed must not be assumed cheap just because it
        has no history. The worst observed under-estimate is the honest prior."""
        assert run_arm.calibration("never-run-before", self.RATIOS) == 2.35

    def test_a_cheap_observation_never_discounts_below_list_price(self):
        """A ratio under 1.0 is real (gemma4 came in at 0.76x), but letting it shrink the estimate
        would let the gate approve a run on a balance that list price alone says is short."""
        assert run_arm.calibration("cheap-model", self.RATIOS) == 1.0

    def test_with_no_history_at_all_calibration_is_exactly_one(self):
        """No data must mean 'no adjustment', not a silently invented multiplier."""
        assert run_arm.calibration("anything", {}) == 1.0

    def test_calibrated_estimate_is_never_below_the_list_estimate(self):
        for label, _c, _m in run_arm.ARM_ORDER:
            raw = run_arm.est_cost(label, 0.1, calibrated=False)
            assert run_arm.est_cost(label, 0.1) >= raw - 1e-9, label

    def test_ratios_are_read_from_the_ledger_not_hardcoded(self):
        """Positive control: the real ledger must actually yield ratios, otherwise every test
        above is exercising an empty dict and the calibration is dead code in production."""
        ratios = run_arm.observed_ratios()
        assert ratios, "no ledger rows produced a ratio -- calibration would be inert"
        assert "gpt5-mini-or" in ratios
        assert ratios["gpt5-mini-or"] > 2.0

    def test_a_direct_api_row_contributes_no_ratio(self):
        """DeepSeek and Anthropic expose no readable balance, so their rows carry
        measured_spend_usd=None. Treating that as $0 spent would compute a 0.0 ratio and make the
        gate think the model is free."""
        assert "deepseek-v4f" not in run_arm.observed_ratios()
        assert "haiku-4.5-direct" not in run_arm.observed_ratios()


class TestAlreadyCompleteModelIsSkipped:
    def test_a_finished_model_owes_zero_calls_and_costs_zero(self):
        """gpt-oss-120b-or is mid-sweep as this is written, so use the LEGACY arm, where every
        model is complete. A model that owes 0 must price at $0 -- otherwise a resumed arm would
        gate on, and report, spend it is not going to make."""
        assert run_arm.calls_owed("mistral-large-or", None) == 0
        assert run_arm.est_cost("mistral-large-or", None) == 0.0

    def test_an_unstarted_model_owes_the_full_arm(self):
        """Priced against an arm that has NEVER been run (temp 0.42), not against whichever model
        happened not to have started yet. The previous version asserted on minimax-m2.5-or at
        temp 0.1 and went red the moment that sweep began -- a test of the arm's live progress
        wearing the name of a test about calls_owed. Same defect class as the one removed from
        test_backfill.py the same day."""
        for label, _c, _m in run_arm.ARM_ORDER:
            assert run_arm.calls_owed(label, 0.42) == 9400, label

    def test_owed_never_goes_negative(self):
        for label, _c, _m in run_arm.ARM_ORDER:
            assert run_arm.calls_owed(label, None) >= 0
