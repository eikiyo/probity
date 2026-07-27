"""
Location: tests/test_aggregate.py
Purpose: Pin results/aggregate.py against the committed 0.7 arm, which is ground truth we did not
         author. The load-bearing checks are: (1) the reduction reproduces the PUBLISHED accuracy
         numbers, (2) the canonical lineup is declared rather than inferred (the leaf-count
         heuristic it replaces now admits 43 fine-tune labels), (3) an arm paired against ITSELF
         has exactly zero discordance, and (4) an unmeasurable item is carried as None rather than
         silently counted as stable.
Functions: TestLineup, TestReproducesPublishedNumbers, TestPerItemFlipsTriState,
           TestSelfPairingInvariant, TestArmIsolation
Imports: json, sys, pytest, pathlib, aggregate
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "results"))
sys.path.insert(0, str(ROOT / "engine"))

import aggregate as ag  # noqa: E402


class TestLineup:
    # Models in the lineup that have NOT yet been measured in the legacy 0.7 arm. deepseek-v4p
    # was added 2026-07-27 and is being swept now. Listing it explicitly is the point: a lineup
    # member with no data must be a DECLARED exception, never something a test quietly tolerates.
    NOT_YET_MEASURED_IN_LEGACY = {"deepseek-v4p"}

    def test_lineup_is_declared_and_has_no_duplicates(self):
        lineup = ag.canonical_lineup()
        assert len(lineup) == 12
        assert len(set(lineup)) == len(lineup)

    def test_lineup_excludes_finetune_lab_labels(self):
        """The fine-tune lab wrote 43 extra labels into the same scored.json files, several of
        which clear the old '>= 10 leaves' heuristic. None may appear in the published lineup."""
        lineup = set(ag.canonical_lineup())
        scored = json.loads((ROOT / "leaves" / "drag_along" / "scored.json").read_text())
        intruders = [k for k in scored
                     if k not in lineup and (k.startswith(("v5-", "tuned-", "mlx-", "q06-"))
                                              or "iter" in k)]
        assert intruders, "expected fine-tune labels to exist in the fixture"
        assert not (lineup & set(intruders))

    def test_every_measured_lineup_label_covers_all_sixty_leaves(self):
        """A lineup naming a model that never ran would silently shrink the published table. A
        model that HAS run must have run everywhere -- a partial model is worse than an absent
        one, because it still appears in the table carrying a denominator nobody checked."""
        counts = ag.model_counts(None)
        assert set(counts) == set(ag.canonical_lineup()) - self.NOT_YET_MEASURED_IN_LEGACY
        for label, c in counts.items():
            assert c["leaves"] == 60, f"{label} covers {c['leaves']} leaves, expected 60"

    def test_the_pending_list_is_kept_honest(self):
        """If a pending model HAS been measured, the exception must be deleted, not left to rot
        into a permanent excuse that hides a future real gap."""
        stale = self.NOT_YET_MEASURED_IN_LEGACY & set(ag.model_counts(None))
        assert not stale, f"measured now -- remove from NOT_YET_MEASURED_IN_LEGACY: {stale}"


class TestReproducesPublishedNumbers:
    """Ground truth: the accuracy column shipped in README.md for the 0.7 arm."""

    PUBLISHED_ACCURACY = {
        "gemma3-1b": 58, "deepseek-v4f": 95, "gemma4-31b-or": 94, "mistral-large-or": 93,
        "minimax-m2.5-or": 94, "llama3.3-70b-or": 93, "gemma3-1b-qat": 61,
        "gemini3-flash-or": 94, "haiku-4.5-direct": 93, "gpt-oss-120b-or": 94,
        "gpt5-mini-or": 94,
    }

    def test_accuracy_matches_the_published_table(self):
        counts = ag.model_counts(None)
        for label, published in self.PUBLISHED_ACCURACY.items():
            c = counts[label]
            got = round(100 * c["correct"] / c["measurable"])
            assert got == published, f"{label}: recomputed {got}%, README says {published}%"

    def test_measured_item_count_never_exceeds_the_oracle_total(self):
        for label, c in ag.model_counts(None).items():
            assert c["measured"] <= 470, f"{label} measured {c['measured']} of 470 items"
            assert c["flipped"] <= c["measured"]

    # Post-backfill (2026-07-27) every cell recorded all 9,400 calls. A handful of ITEMS are
    # still unmeasurable -- not because calls are missing, but because all 20 runs for that item
    # returned output no parser could read. These are two DIFFERENT dimensions and the suite
    # keeps them apart: coverage is about calls MADE, measurability about answers OBTAINED.
    MEASURED_ITEMS = {
        "gemma3-1b": 469, "deepseek-v4f": 470, "gemma4-31b-or": 469, "mistral-large-or": 470,
        "minimax-m2.5-or": 470, "llama3.3-70b-or": 469, "gemma3-1b-qat": 470,
        "gemini3-flash-or": 469, "haiku-4.5-direct": 468, "gpt-oss-120b-or": 469,
        "gpt5-mini-or": 470,
    }

    def test_measured_item_counts_match_disk(self):
        """haiku had lost 16 items and gemini 4 to the guard TRUNCATION; the backfill recovered
        those. What remains is a much smaller residue of all-20-runs-unparseable items, which the
        tri-state reduction correctly refuses to count as stable."""
        counts = ag.model_counts(None)
        for label, expected in self.MEASURED_ITEMS.items():
            assert counts[label]["measured"] == expected, label

    def test_no_model_loses_more_than_a_handful_of_items_to_parse_failure(self):
        """A guard rail on the residue: if this ever jumps, a model has started failing to answer
        at scale and the wobble denominator is quietly shrinking again."""
        for label, c in ag.model_counts(None).items():
            assert 470 - c["measured"] <= 2, f"{label} lost {470 - c['measured']} items"


class TestPerItemFlipsTriState:
    def test_zero_run_item_is_none_not_false(self):
        res = {"accuracy": {"per_instance": [
            {"n_valid": 0, "fields": {"f": {"consistency": 0.0}}},
            {"n_valid": 20, "fields": {"f": {"consistency": 1.0}}},
            {"n_valid": 20, "fields": {"f": {"consistency": 0.6}}},
        ]}}
        assert ag.per_item_flips(res, "f") == [None, False, True]

    def test_a_zero_run_item_is_not_counted_as_a_flip(self):
        """scorer's two paths disagree on this item: score_runs skips it, score_accuracy records
        consistency 0.0 which a naive `< 1.0` test reads as a flip. Neither answer may leak in."""
        res = {"accuracy": {"per_instance": [{"n_valid": 0,
                                               "fields": {"f": {"consistency": 0.0}}}]}}
        flags = ag.per_item_flips(res, "f")
        assert flags == [None]
        assert sum(1 for f in flags if f is True) == 0
        assert sum(1 for f in flags if f is not None) == 0

    def test_missing_field_detail_is_none(self):
        res = {"accuracy": {"per_instance": [{"n_valid": 20, "fields": {}}]}}
        assert ag.per_item_flips(res, "f") == [None]


class TestSelfPairingInvariant:
    """An arm paired against ITSELF must be perfectly concordant. Any nonzero discordance means
    the pairing is misaligning items, which would silently fabricate a temperature effect."""

    @pytest.mark.parametrize("label", ["haiku-4.5-direct", "gemma3-1b", "minimax-m2.5-or"])
    def test_zero_discordance_against_itself(self, label):
        p = ag.paired_counts(label, None, None)
        assert p["only_a"] == 0 and p["only_b"] == 0
        assert p["n_pairs"] > 0
        assert p["both"] + p["neither"] == p["n_pairs"]

    def test_dropped_pairs_are_reported_not_hidden(self):
        """Post-backfill the 16 truncated haiku items are back; the 2 that remain dropped are
        items whose every run was unparseable. They must still be COUNTED and disclosed, never
        silently absorbed into a shrinking denominator."""
        p = ag.paired_counts("haiku-4.5-direct", None, None)
        assert p["dropped"] == 2        # the all-runs-unparseable residue, explicitly accounted
        assert p["n_pairs"] == 468


class TestArmIsolation:
    def test_an_unrun_arm_yields_no_counts_rather_than_zeros(self):
        """A model with no data for an arm must be ABSENT, not present with 0% wobble -- a
        confident zero from no data is the failure mode this whole exercise exists to kill."""
        counts = ag.model_counts(0.42)      # an arm that was never run
        assert counts == {}

    def test_paired_counts_empty_when_one_arm_missing(self):
        p = ag.paired_counts("haiku-4.5-direct", None, 0.42)
        assert p["n_pairs"] == 0
