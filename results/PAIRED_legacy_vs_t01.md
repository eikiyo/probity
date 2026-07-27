# Probity — arm t01 (0.1) results, paired against arm legacy (0.7)

**Wobble** = the share of items where a model gave more than one answer across 20 identical runs. **Accuracy** = the share whose majority answer matched the human-validated truth. They are reported separately and never averaged.

All intervals are 95%. Single rates use **Wilson score** intervals (not the normal approximation, which degenerates near 0 and several models sit at ~3%). Paired deltas use **Tango's score interval** for the difference of paired proportions, because both arms are measured on the same items and are therefore correlated.

## Suite summary @ t01 (0.1)

| Model | Size / routing | Tests | Items | **Wobble** ↓ (95% CI) | Accuracy (95% CI) |
|---|---|---|---|---|---|
| `deepseek-v4-pro` | hosted, direct | 60 | 467 | **0.9% [0.3, 2.2]** | 94.9% [92.5, 96.5] |
| `deepseek-v4-flash` | hosted, direct | 53 | 426 | **0.9% [0.4, 2.4]** | 95.1% [92.6, 96.8] |
| `claude-haiku-4.5` | hosted, direct API | 60 | 466 | **1.1% [0.5, 2.5]** | 93.1% [90.5, 95.1] |
| `mistral-large-2512` | hosted (OR) | 60 | 470 | **1.3% [0.6, 2.8]** | 92.8% [90.1, 94.8] |
| `gemini-3-flash` | hosted (OR) | 60 | 469 | **2.1% [1.2, 3.9]** | 94.9% [92.5, 96.5] |
| `gemma-4-31b-it` | 31B, hosted (OR) | 60 | 469 | **2.6% [1.5, 4.4]** | 94.5% [92.0, 96.2] |
| `llama-3.3-70b` | 70B, hosted (OR) | 60 | 469 | **3.4% [2.1, 5.5]** | 92.3% [89.6, 94.4] |
| `gpt-5-mini` | hosted (OR) | 60 | 470 | **5.5% [3.8, 8.0]** | 94.3% [91.8, 96.0] |
| `gpt-oss-120b` | 120B, hosted (OR) | 60 | 469 | **8.1% [6.0, 10.9]** | 94.7% [92.2, 96.4] |
| `minimax-m2.5` | hosted (OR) | 60 | 469 | **10.7% [8.2, 13.8]** | 94.9% [92.5, 96.5] |
| `gemma3:1b-it-qat` | 1B QAT, local | 60 | 469 | **20.5% [17.1, 24.4]** | 60.3% [55.8, 64.7] |
| `gemma3:1b` | 1B, local | 59 | 464 | **23.1% [19.5, 27.1]** | 58.8% [54.3, 63.2] |

### Statistically indistinguishable groups @ t01 (0.1)

Models whose 95% wobble intervals overlap are **statistically indistinguishable** at this sample size and are not ranked against each other:

1. `deepseek-v4-pro`, `deepseek-v4-flash`, `claude-haiku-4.5`, `mistral-large-2512`, `gemini-3-flash`, `gemma-4-31b-it`, `llama-3.3-70b`
2. `gpt-5-mini`, `gpt-oss-120b`
3. `minimax-m2.5`  *(single model, separated from the rest)*
4. `gemma3:1b-it-qat`, `gemma3:1b`

*Bands are formed by single-linkage chaining on interval overlap: membership means a model overlaps its neighbours in the band, not that every pair in the band mutually overlaps.*

## Paired comparison: legacy (0.7) vs t01 (0.1)

| Model | Pairs | Wobble @ legacy (0.7) | Wobble @ t01 (0.1) | **Δ (legacy (0.7) − t01 (0.1))** 95% CI | Verdict |
|---|---|---|---|---|---|
| `minimax-m2.5` | 469 | 7.5% [5.4, 10.2] | 10.7% [8.2, 13.8] | **-3.2% [-5.7, -1.0]** | lower at legacy (0.7) |
| `gpt-oss-120b` | 469 | 6.2% [4.3, 8.7] | 8.1% [6.0, 10.9] | **-1.9% [-4.1, -0.0]** | lower at legacy (0.7) |
| `llama-3.3-70b` | 469 | 3.2% [1.9, 5.2] | 3.4% [2.1, 5.5] | **-0.2% [-1.6, 1.1]** | no difference established |
| `gpt-5-mini` | 470 | 5.5% [3.8, 8.0] | 5.5% [3.8, 8.0] | **0.0% [-1.6, 1.6]** | no difference established |
| `gemma-4-31b-it` | 469 | 3.0% [1.8, 4.9] | 2.6% [1.5, 4.4] | **+0.4% [-0.6, 1.7]** | no difference established |
| `gemini-3-flash` | 469 | 2.6% [1.5, 4.4] | 2.1% [1.2, 3.9] | **+0.4% [-1.1, 2.0]** | no difference established |
| `claude-haiku-4.5` | 466 | 2.8% [1.6, 4.7] | 1.1% [0.5, 2.5] | **+1.7% [0.9, 3.4]** | lower at t01 (0.1) |
| `mistral-large-2512` | 470 | 3.2% [1.9, 5.2] | 1.3% [0.6, 2.8] | **+1.9% [1.0, 3.6]** | lower at t01 (0.1) |
| `deepseek-v4-pro` | 467 | 4.5% [3.0, 6.8] | 0.9% [0.3, 2.2] | **+3.6% [2.3, 5.8]** | lower at t01 (0.1) |
| `deepseek-v4-flash` | 467 | 5.8% [4.0, 8.3] | 1.1% [0.5, 2.5] | **+4.7% [3.0, 7.1]** | lower at t01 (0.1) |
| `gemma3:1b-it-qat` | 469 | 33.9% [29.8, 38.3] | 20.5% [17.1, 24.4] | **+13.4% [10.4, 16.9]** | lower at t01 (0.1) |
| `gemma3:1b` | 466 | 42.5% [38.1, 47.0] | 23.0% [19.4, 27.0] | **+19.5% [15.7, 23.7]** | lower at t01 (0.1) |

*20 item-pairs excluded because one arm could not measure them (no valid runs). They are excluded from BOTH arms of every pair, never counted as stable in one and dropped from the other.*

## Parse failures and dropped tests

A run that produced nothing a parser could read contributes NO answer. When more than 30% of a test's runs are unparseable for a model, the whole test is dropped from that model's published numbers — which SHRINKS THE DENOMINATOR wobble is a rate over. A model that stops answering its hardest tests can therefore look *more* consistent while actually having answered less. Read this table beside the wobble deltas above, not after them.

The last column is the one that matters: it is the item count each arm's wobble is computed over. A ⚠️ marks a model whose two arms are NOT scored over the same number of items, so its row in the suite tables is not a like-for-like comparison. (The PAIRED table above is unaffected — it is computed over the items BOTH arms measured.) Items can also be lost to transport errors, which is why a model can show zero unparseable runs and still score fewer items.

| Model | Unparseable @ legacy (0.7) | Unparseable @ t01 (0.1) | Tests dropped @ legacy (0.7) | Tests dropped @ t01 (0.1) | Items scored legacy (0.7) → t01 (0.1) |
|---|---|---|---|---|---|
| `deepseek-v4-flash` | 125 | 567 | 0 | 7 | 470 → 426  ⚠️ −44 |
| `gemini-3-flash` | 6 | 354 | 0 | 0 | 469 → 469 |
| `llama-3.3-70b` | 1 | 70 | 0 | 0 | 469 → 469 |
| `gemma-4-31b-it` | 0 | 6 | 0 | 0 | 469 → 469 |
| `deepseek-v4-pro` | 0 | 0 | 0 | 0 | 469 → 467  ⚠️ −2 |
| `mistral-large-2512` | 0 | 0 | 0 | 0 | 470 → 470 |
| `claude-haiku-4.5` | 0 | 0 | 0 | 0 | 468 → 466  ⚠️ −2 |
| `gpt-5-mini` | 18 | 2 | 0 | 0 | 470 → 470 |
| `gpt-oss-120b` | 28 | 5 | 0 | 0 | 469 → 469 |
| `gemma3:1b-it-qat` | 103 | 71 | 0 | 0 | 470 → 469  ⚠️ −1 |
| `gemma3:1b` | 167 | 76 | 0 | 1 | 469 → 464  ⚠️ −5 |
| `minimax-m2.5` | 552 | 166 | 0 | 0 | 470 → 469  ⚠️ −1 |

## By fundraising-document category @ t01 (0.1)

| Category | Tests | **Wobble** ↓ (95% CI) | Accuracy (95% CI) |
|---|---|---|---|
| Priced equity rounds | 16 | **5.0% [4.1, 6.2]** | 86.0% [84.3, 87.6] |
| SAFEs & convertible notes | 12 | **3.7% [2.7, 5.0]** | 95.4% [94.0, 96.5] |
| Cap table math | 7 | **13.0% [10.1, 16.7]** | 81.3% [77.2, 84.9] |
| Investor rights & governance | 7 | **6.7% [5.3, 8.5]** | 88.1% [85.8, 90.0] |
| Founder & employee vesting | 5 | **4.9% [3.4, 7.0]** | 93.3% [90.9, 95.1] |
| Regulatory disclosures | 5 | **14.9% [11.4, 19.2]** | 89.5% [85.7, 92.4] |
| Off-market risk flags | 5 | **6.0% [4.2, 8.5]** | 83.5% [79.9, 86.6] |
| Exit waterfalls | 3 | **32.3% [23.8, 42.2]** | 70.8% [61.1, 79.0] |

## Appendix: requested vs honoured temperature

| Model | Routing | Temp requested | Temp honoured (provider-reported) |
|---|---|---|---|
| `deepseek-v4-flash` | direct | 0.1 | `null` (not reported) |
| `deepseek-v4-pro` | direct | 0.1 | `null` (not reported) |
| `claude-haiku-4-5-20251001` | direct | 0.1 | `null` (not reported) |
| `gemma3:1b` | ollama | 0.1 | `null` (not reported) |
| `gemma3:1b-it-qat` | ollama | 0.1 | `null` (not reported) |
| `google/gemini-3-flash-preview` | openrouter | 0.1 | `null` (not reported) |
| `google/gemma-4-31b-it` | openrouter | 0.1 | `null` (not reported) |
| `openai/gpt-oss-120b` | openrouter | 0.1 | `null` (not reported) |
| `openai/gpt-5-mini` | openrouter | 0.1 | `null` (not reported) |
| `meta-llama/llama-3.3-70b-instruct` | openrouter | 0.1 | `null` (not reported) |
| `minimax/minimax-m2.5` | openrouter | 0.1 | `null` (not reported) |
| `mistralai/mistral-large-2512` | openrouter | 0.1 | `null` (not reported) |

*0 of 12 providers report the sampling temperature back in the response body. Where a provider reports nothing, the value is recorded as `null`: the request carried the temperature, but the provider offers no confirmation that it was applied, and asserting otherwise would be unfounded.*

## Coverage

| Leaf | gemma3-1b | deepseek-v4f | deepseek-v4p | gemma4-31b-or | mistral-large-or | minimax-m2.5-or | llama3.3-70b-or | gemma3-1b-qat | gemini3-flash-or | haiku-4.5-direct | gpt-oss-120b-or | gpt5-mini-or |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| acceleration_trigger | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 |
| antidilution_base | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 |
| antidilution_type | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| auto_conversion_trigger | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| board_seats_investor | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 |
| cliff_present | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 |
| conversion_ratio | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| convert_vs_preference_decision | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 |
| current_ownership_pct | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 |
| dividend_cumulative | 320 | 320 | 320 | 320 | 320 | 320 | 320 | 320 | 320 | 320 | 320 | 320 |
| dividend_rate_pct | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 |
| drag_along | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 |
| employee_pool_pct | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| exercise_window | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| financial_statement_qa | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| flag_full_ratchet | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 |
| flag_internal_inconsistency | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| flag_missing_pro_rata | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 |
| flag_offmarket_liqpref | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 |
| flag_uncapped_participation | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 |
| form_d_fields | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 |
| founder_ownership_pct | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 |
| fully_diluted_basis | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 |
| information_rights | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 |
| investor_ownership_pct | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 |
| liquidation_preference_multiple | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 |
| liquidation_waterfall_payout | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 |
| multi_round_stacked_dilution | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| note_discount | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 |
| note_interest_rate | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 | 120 |
| note_maturity_date | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 |
| note_principal | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 |
| note_qualified_financing_threshold | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 |
| note_valuation_cap | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 |
| option_pool_shuffle | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 |
| option_strike_409a | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 |
| participation_cap | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 | 60 |
| participation_type | 360 | 360 | 360 | 360 | 360 | 360 | 360 | 360 | 360 | 360 | 360 | 360 |
| per_investor_allocation | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| post_money_valuation | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 | 80 |
| pre_vs_post_money | 380 | 380 | 380 | 380 | 380 | 380 | 380 | 380 | 380 | 380 | 380 | 380 |
| preference_seniority | 220 | 220 | 220 | 220 | 220 | 220 | 220 | 220 | 220 | 220 | 220 | 220 |
| preference_stack_payout | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40 |
| price_per_share | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 |
| pro_rata_rights | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 |
| protective_provisions | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 |
| redemption_rights | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 |
| rofr_cosale | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 | 240 |
| round_size | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 |
| s1_risk_factors | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| s1_use_of_proceeds | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| safe_cap_vs_discount_applies | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 | 260 |
| safe_discount_rate | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 |
| safe_mfn_present | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 | 140 |
| safe_pre_post | 320 | 320 | 320 | 320 | 320 | 320 | 320 | 320 | 320 | 320 | 320 | 320 |
| safe_pro_rata_side_letter | 300 | 300 | 300 | 300 | 300 | 300 | 300 | 300 | 300 | 300 | 300 | 300 |
| safe_valuation_cap | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 | 160 |
| securities_exemption | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 |
| vesting_acceleration | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 |
| vesting_schedule | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 | 180 |

**720/720 cells complete · 112800/112800 calls recorded**
