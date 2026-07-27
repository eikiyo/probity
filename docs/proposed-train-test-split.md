# Train/Test Split — CORRECTED (orchestrator review, 2026-07-02)

**Superseded the first agent draft.** That draft co-stratified by (class VALUE + difficulty), which at this
sample size produced spurious risk flags on leaves that are actually clean at the class level -- e.g.
`dividend_cumulative` is a textbook 8/8 class split but the difficulty-substratified version produced an
uneven 9/7 split AND a false 'risky' flag. Verified directly against real oracle.jsonl counts before fixing.

**Method now: stratify by class value ONLY** (drop difficulty as a hard bucket), deterministic id-sort within
class, alternate which side gets a stratum's odd leftover item across leaves. Compute/numeric leaves: plain
id-sorted 50/50, unchanged from the original draft.

**Result: risky-leaf count drops from 45 -> 32** (the 14 removed were all difficulty-substratification false
alarms on otherwise-healthy leaves). The 31 remaining (+1 new, `safe_cap_vs_discount_applies`, whose smallest
REAL class has 1 item) are genuine: leaves under 8 total items, where 50/50 unavoidably leaves 1-4 items per
shard. That's real data scarcity (small hand-curated real-filing corpora, same class of constraint already
logged for `round_size`/`dividend_rate_pct`), not a splitting bug -- accepted as-is per the literal
"50/50 for all leaves" instruction. Totals: 470 oracle rows, 233 test / 237 train (near-even; exact 235/235
isn't hit because leaf-level odd-count rounding doesn't perfectly cancel across 60 independent leaves).

## Summary

| Leaf | N | Test | Train | Risk |
|---|---|---|---|---|
| `acceleration_trigger` | 13 | 7 | 6 | — |
| `antidilution_base` | 10 | 6 | 4 | — |
| `antidilution_type` | 5 | 2 | 3 | small N (n=5) |
| `auto_conversion_trigger` | 5 | 3 | 2 | small N (n=5) |
| `board_seats_investor` | 9 | 4 | 5 | — |
| `cliff_present` | 12 | 6 | 6 | — |
| `conversion_ratio` | 5 | 3 | 2 | small N (n=5) |
| `convert_vs_preference_decision` | 2 | 1 | 1 | small N (n=2) |
| `current_ownership_pct` | 9 | 4 | 5 | — |
| `dividend_cumulative` | 16 | 8 | 8 | — |
| `dividend_rate_pct` | 6 | 3 | 3 | small N (n=6) |
| `drag_along` | 12 | 6 | 6 | — |
| `employee_pool_pct` | 1 | 0 | 1 | small N (n=1) |
| `exercise_window` | 5 | 3 | 2 | small N (n=5) |
| `financial_statement_qa` | 5 | 2 | 3 | small N (n=5) |
| `flag_full_ratchet` | 7 | 3 | 4 | small N (n=7) |
| `flag_internal_inconsistency` | 5 | 2 | 3 | small N (n=5) |
| `flag_missing_pro_rata` | 4 | 2 | 2 | small N (n=4) |
| `flag_offmarket_liqpref` | 10 | 5 | 5 | — |
| `flag_uncapped_participation` | 13 | 6 | 7 | — |
| `form_d_fields` | 2 | 1 | 1 | small N (n=2) |
| `founder_ownership_pct` | 3 | 1 | 2 | small N (n=3) |
| `fully_diluted_basis` | 8 | 4 | 4 | — |
| `information_rights` | 12 | 6 | 6 | — |
| `investor_ownership_pct` | 4 | 2 | 2 | small N (n=4) |
| `liquidation_preference_multiple` | 9 | 4 | 5 | — |
| `liquidation_waterfall_payout` | 4 | 2 | 2 | small N (n=4) |
| `multi_round_stacked_dilution` | 5 | 2 | 3 | small N (n=5) |
| `note_discount` | 4 | 2 | 2 | small N (n=4) |
| `note_interest_rate` | 6 | 3 | 3 | small N (n=6) |
| `note_maturity_date` | 4 | 2 | 2 | small N (n=4) |
| `note_principal` | 7 | 3 | 4 | small N (n=7) |
| `note_qualified_financing_threshold` | 2 | 1 | 1 | small N (n=2) |
| `note_valuation_cap` | 4 | 2 | 2 | small N (n=4) |
| `option_pool_shuffle` | 3 | 2 | 1 | small N (n=3) |
| `option_strike_409a` | 7 | 3 | 4 | small N (n=7) |
| `participation_cap` | 3 | 2 | 1 | small N (n=3) |
| `participation_type` | 18 | 8 | 10 | — |
| `per_investor_allocation` | 5 | 3 | 2 | small N (n=5) |
| `post_money_valuation` | 4 | 2 | 2 | small N (n=4) |
| `pre_vs_post_money` | 19 | 10 | 9 | — |
| `preference_seniority` | 11 | 6 | 5 | — |
| `preference_stack_payout` | 2 | 1 | 1 | small N (n=2) |
| `price_per_share` | 8 | 4 | 4 | — |
| `pro_rata_rights` | 12 | 6 | 6 | — |
| `protective_provisions` | 12 | 6 | 6 | — |
| `redemption_rights` | 10 | 5 | 5 | — |
| `rofr_cosale` | 12 | 6 | 6 | — |
| `round_size` | 10 | 5 | 5 | — |
| `s1_risk_factors` | 5 | 2 | 3 | small N (n=5) |
| `s1_use_of_proceeds` | 5 | 3 | 2 | small N (n=5) |
| `safe_cap_vs_discount_applies` | 13 | 6 | 7 | smallest class has only 1 item(s) |
| `safe_discount_rate` | 9 | 5 | 4 | — |
| `safe_mfn_present` | 7 | 4 | 3 | small N (n=7) |
| `safe_pre_post` | 16 | 8 | 8 | — |
| `safe_pro_rata_side_letter` | 15 | 7 | 8 | — |
| `safe_valuation_cap` | 8 | 4 | 4 | — |
| `securities_exemption` | 10 | 5 | 5 | — |
| `vesting_acceleration` | 9 | 4 | 5 | — |
| `vesting_schedule` | 9 | 5 | 4 | — |

## Status
Confirmed by orchestrator review (2026-07-02). Ready to drive the T1/T2 loader implementation:
`docs/proposed-train-test-split.json` is the locked shard assignment (row-hash-equivalent, fully
deterministic and reproducible from oracle.jsonl + this method alone).
