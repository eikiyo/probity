"""
Location: results/render.py
Purpose: Render RESULTS.md (full per-leaf detail, all 60+ tables) + the README landing-page
         summary (2 aggregate tables, color-coded via shields.io badges) from EVERY leaf that has
         a scored.json. WOBBLE (run-to-run inconsistency) is the headline -- the core thesis --
         with accuracy beside it, never averaged in. Multi-leaf: FIELD + CLASSES come from each
         leaf's own task.TASK (single source of truth); per-leaf display config lives in LEAVES.
         README REDESIGN (2026-07-02, Eikiyo-directed): the README previously injected all 60
         individual per-leaf tables inline -- a wall of tables that buried the actual finding.
         Replaced with 2 aggregate tables (suite_summary_table(): wobble/accuracy weighted by
         item count, one row per model size -- THE headline result; family_summary_table(): same,
         one row per registry family/category) computed by aggregate_by_model()/
         aggregate_by_family() directly from every leaf's scored.json. The full 60-table
         per-leaf breakdown stays in results/RESULTS.md, linked from the README, not duplicated.
Functions: load_leaf(), wobble_pct(), per_class(), definitions(), render_leaf(), readme_block_for(),
           auto_findings(), aggregate_by_model(), aggregate_by_family(), badge(),
           suite_summary_table(), family_summary_table(), main()
Imports: json, re, importlib.util, pathlib
"""

import json
import re
import importlib.util
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Per-leaf DISPLAY config only — field + class enum are read from the leaf's task.TASK.
LEAVES = [
    {"slug": "participation_type",
     "title": "Test 1.3.2 — Preferred-stock liquidation participation",
     "corpus_desc": "real SEC-filed charter clauses",
     "labels": {"non-participating": "non-part", "participating": "part", "capped": "capped"}},
    {"slug": "safe_pre_post",
     "title": "Test 2.1.4 — SAFE valuation cap: pre-money vs post-money",
     "corpus_desc": "real SEC-filed YC SAFE provisions",
     "labels": {"post-money": "post", "pre-money": "pre"}},
    {"slug": "dividend_cumulative",
     "title": "Test 1.4.2 — Preferred dividends: cumulative vs non-cumulative",
     "corpus_desc": "real SEC-filed preferred-stock charter dividend clauses",
     "labels": {"cumulative": "cumulative", "non-cumulative": "non-cum"}},
    {"slug": "acceleration_trigger",
     "title": "Test 6.3 — Equity vesting acceleration: single-trigger vs double-trigger",
     "corpus_desc": "real SEC-filed equity-award / employment agreements",
     "labels": {"single-trigger": "single", "double-trigger": "double"}},
    {"slug": "preference_seniority",
     "title": "Test 1.3.4 — Multi-series preference seniority: pari-passu vs stacked",
     "corpus_desc": "real SEC-filed multi-series preferred charters",
     "labels": {"pari-passu": "pari-passu", "stacked": "stacked"}},
    {"slug": "flag_offmarket_liqpref",
     "title": "Test 8.1 — Risk flag: off-market liquidation preference (>1x)",
     "corpus_desc": "real SEC-filed preferred-stock liquidation clauses",
     "labels": {"yes": "off-market(>1x)", "no": "standard(1x)"}},
    {"slug": "redemption_rights",
     "title": "Test 1.7 — Redemption rights: redeemable vs non-redeemable",
     "corpus_desc": "real SEC-filed preferred-stock charter redemption clauses",
     "labels": {"yes": "redeemable", "no": "non-redeem"}},
    {"slug": "drag_along",
     "title": "Test 5.6 — Transfer agreements: drag-along (obligation) vs co-sale (right)",
     "corpus_desc": "real SEC-filed stockholder/transfer agreements",
     "labels": {"yes": "drag(obligated)", "no": "co-sale(right)"}},
    {"slug": "rofr_cosale",
     "title": "Test 5.5 — Right of First Refusal & Co-Sale: investor transfer right present vs absent",
     "corpus_desc": "real SEC-filed stockholder/transfer documents",
     "labels": {"yes": "rofr/cosale", "no": "absent/other-right"}},
    {"slug": "pro_rata_rights",
     "title": "Test 5.4 — Pro-rata right on future financings: granted vs not",
     "corpus_desc": "real SEC-filed SAFEs, side letters and investors' rights agreements",
     "labels": {"yes": "pro-rata", "no": "absent/waived"}},
    {"slug": "cliff_present",
     "title": "Test 6.2 — Vesting schedule: cliff present vs absent",
     "corpus_desc": "real SEC-filed equity-award agreements and disclosures",
     "labels": {"yes": "cliff", "no": "no-cliff"}},
    {"slug": "protective_provisions",
     "title": "Test 5.2 — Protective provisions: investor class-veto right present vs absent",
     "corpus_desc": "real SEC-filed charters and governance documents",
     "labels": {"yes": "veto-right", "no": "absent"}},
    {"slug": "information_rights",
     "title": "Test 5.3 — Information rights: live financial-reporting obligation vs absent",
     "corpus_desc": "real SEC-filed investors' rights agreements and equity-award docs",
     "labels": {"yes": "info-rights", "no": "absent/waived"}},
    {"slug": "vesting_acceleration",
     "title": "Test 5.7 — Vesting acceleration: granted on trigger vs absent",
     "corpus_desc": "real SEC-filed equity-award agreements and proxy disclosures",
     "labels": {"yes": "accelerates", "no": "no-acceleration"}},
    {"slug": "liquidation_preference_multiple",
     "title": "Test 1.3.1 — Liquidation preference multiple: 1x vs 2x vs 3x vs other",
     "corpus_desc": "real SEC-filed preferred-stock liquidation preference clauses",
     "labels": {"non-participating": "non-part", "1x": "1x", "2x": "2x", "3x": "3x", "other": "other"}},
    {"slug": "board_seats_investor",
     "title": "Test 5.1 — Board seats: number an investor has the right to designate",
     "corpus_desc": "real SEC-filed voting/shareholders'/designation agreements",
     "labels": {}},
    {"slug": "safe_pro_rata_side_letter",
     "title": "Test 2.1.6 — SAFE pro-rata side letter: granted vs absent",
     "corpus_desc": "real SEC-filed SAFEs and pro-rata side letters",
     "labels": {"yes": "pro-rata", "no": "absent"}},
    {"slug": "pre_vs_post_money",
     "title": "Test 1.1.2 — Priced round basis: pre-money vs post-money",
     "corpus_desc": "real SEC-filed priced-round financing documents",
     "labels": {"pre-money": "pre", "post-money": "post"}},
    {"slug": "flag_full_ratchet",
     "title": "Test 8.2 — Risk flag: full-ratchet anti-dilution present vs absent",
     "corpus_desc": "real SEC-filed preferred-stock anti-dilution clauses",
     "labels": {"yes": "full-ratchet", "no": "absent"}},
    {"slug": "post_money_valuation",
     "title": "Test 1.1.1 — Post-money valuation extraction",
     "corpus_desc": "real SEC-filed priced-round financing documents",
     "labels": {}},
    {"slug": "antidilution_type",
     "title": "Test 1.5.1 — Anti-dilution mechanism: full-ratchet vs weighted-average vs none",
     "corpus_desc": "real SEC-filed preferred-stock anti-dilution clauses",
     "labels": {"full-ratchet": "full-ratchet", "weighted-average": "weighted-avg",
                "broad-based": "broad-based", "narrow-based": "narrow-based", "none": "none"}},
    {"slug": "flag_uncapped_participation",
     "title": "Test 8.3 — Risk flag: uncapped participating-preferred present vs absent",
     "corpus_desc": "real SEC-filed preferred-stock liquidation/participation clauses",
     "labels": {"yes": "uncapped", "no": "capped/none"}},
    {"slug": "safe_mfn_present",
     "title": "Test 2.1.5 — SAFE Most-Favored-Nation clause: present vs absent",
     "corpus_desc": "real SEC-filed SAFE agreements",
     "labels": {"yes": "MFN", "no": "absent"}},
    {"slug": "participation_cap",
     "title": "Test 1.3.3 — Participation cap multiple extraction",
     "corpus_desc": "real SEC-filed capped-participating-preferred liquidation clauses",
     "labels": {}},
    {"slug": "option_strike_409a",
     "title": "Test 6.4 — Stock option exercise (strike) price extraction",
     "corpus_desc": "real SEC-filed stock option grant agreements",
     "labels": {}},
    {"slug": "safe_valuation_cap",
     "title": "Test 2.1.1 — SAFE valuation cap extraction",
     "corpus_desc": "real SEC-filed SAFE agreements",
     "labels": {}},
    {"slug": "note_principal",
     "title": "Test 2.2.1 — Convertible note principal amount extraction",
     "corpus_desc": "real SEC-filed convertible promissory notes",
     "labels": {}},
    {"slug": "safe_discount_rate",
     "title": "Test 2.1.2 — SAFE discount rate extraction",
     "corpus_desc": "real SEC-filed SAFE agreements",
     "labels": {}},
    {"slug": "note_valuation_cap",
     "title": "Test 2.2.4 — Convertible note valuation cap extraction",
     "corpus_desc": "real SEC-filed convertible promissory notes",
     "labels": {}},
    {"slug": "conversion_ratio",
     "title": "Test 1.6.1 — Preferred-stock conversion ratio extraction",
     "corpus_desc": "real SEC-filed preferred-stock charters",
     "labels": {}},
    {"slug": "antidilution_base",
     "title": "Test 1.5.2 — Anti-dilution weighted-average base: broad-based vs narrow-based vs n/a",
     "corpus_desc": "real SEC-filed preferred-stock charter anti-dilution clauses",
     "labels": {"broad-based": "broad", "narrow-based": "narrow", "n/a": "n/a"}},
    {"slug": "auto_conversion_trigger",
     "title": "Test 1.6.2 — Automatic conversion (QPO) proceeds threshold extraction",
     "corpus_desc": "real SEC-filed preferred-stock charter automatic-conversion clauses",
     "labels": {}},
    {"slug": "note_interest_rate",
     "title": "Test 2.2.2 — Convertible note interest rate extraction",
     "corpus_desc": "real SEC-filed convertible promissory notes",
     "labels": {}},
    {"slug": "safe_cap_vs_discount_applies",
     "title": "Test 2.1.3 — SAFE conversion mechanic: cap-only vs discount-only vs both (MFN)",
     "corpus_desc": "real SEC-filed SAFE (Simple Agreement for Future Equity) instruments",
     "labels": {"cap": "cap", "discount": "discount", "both-mfn": "both-mfn"}},
    {"slug": "price_per_share",
     "title": "Test 1.1.3 — Priced-round price-per-share extraction",
     "corpus_desc": "real SEC-filed stock purchase agreements / charters / offerings",
     "labels": {}},
    {"slug": "note_maturity_date",
     "title": "Test 2.2.3 — Convertible note maturity date extraction",
     "corpus_desc": "real SEC-filed convertible promissory notes",
     "labels": {}},
    {"slug": "note_discount",
     "title": "Test 2.2.5 — Convertible note conversion-discount rate extraction",
     "corpus_desc": "real SEC-filed convertible promissory notes",
     "labels": {}},
    {"slug": "note_qualified_financing_threshold",
     "title": "Test 2.2.6 — Convertible note Qualified Financing proceeds threshold extraction",
     "corpus_desc": "real SEC-filed convertible promissory notes",
     "labels": {}},
    {"slug": "vesting_schedule",
     "title": "Test 6.1 — Equity vesting schedule extraction + normalization",
     "corpus_desc": "real SEC-filed equity-award / employment agreements",
     "labels": {}},
    {"slug": "current_ownership_pct",
     "title": "Test 3.1 — Cap-table current ownership percentage (compute)",
     "corpus_desc": "real SEC-filed S-1 Security Ownership tables (single-class stock only)",
     "labels": {}},
    {"slug": "founder_ownership_pct",
     "title": "Test 3.2.1 — Named founder's ownership percentage (compute)",
     "corpus_desc": "real SEC-filed S-1 Security Ownership tables (single-class stock only)",
     "labels": {}},
    {"slug": "investor_ownership_pct",
     "title": "Test 3.2.2 — Named institutional investor's ownership percentage (compute)",
     "corpus_desc": "real SEC-filed S-1 Security Ownership tables (single-class stock only)",
     "labels": {}},
    {"slug": "employee_pool_pct",
     "title": "Test 3.2.3 — Employee option pool size as % of total shares (compute)",
     "corpus_desc": "real SEC-filed S-1 capitalization narrative",
     "labels": {}},
    {"slug": "securities_exemption",
     "title": "Test 7.1 — Securities Act exemption classification",
     "corpus_desc": "real SEC Form D filings (structured federalExemptionsExclusions field)",
     "labels": {"506b": "506(b)", "506c": "506(c)", "504": "504", "reg-a": "Reg A", "other": "other"}},
    {"slug": "form_d_fields",
     "title": "Test 7.2 — Form D field extraction (Total Amount Sold)",
     "corpus_desc": "real SEC Form D filings",
     "labels": {}},
    {"slug": "round_size",
     "title": "Test 1.2.1 — Total financing round size extraction",
     "corpus_desc": "real SEC Form D filings (structured totalAmountSold field, operating companies only)",
     "labels": {}},
    {"slug": "dividend_rate_pct",
     "title": "Test 1.4.1 — Annual dividend rate percentage extraction",
     "corpus_desc": "real venture-financing preferred-stock charters",
     "labels": {}},
    {"slug": "multi_round_stacked_dilution",
     "title": "Test 3.6 — Per-share dilution to new investors (compute)",
     "corpus_desc": "real IPO prospectus Dilution-section tables",
     "labels": {}},
    {"slug": "fully_diluted_basis",
     "title": "Test 3.4 — Fully-diluted vs issued-outstanding basis classification",
     "corpus_desc": "real venture financing exhibits + S-1 capitalization tables",
     "labels": {"fully-diluted": "Fully-diluted", "issued-outstanding": "Issued-outstanding"}},
    {"slug": "financial_statement_qa",
     "title": "Test 7.5 — Named-period revenue figure extraction",
     "corpus_desc": "real S-1 Selected/Summary Financial Data tables",
     "labels": {}},
    {"slug": "flag_internal_inconsistency",
     "title": "Test 8.6 — Cross-citation share-count consistency flag",
     "corpus_desc": "real S-1/424B4 filings, paired share-count citations",
     "labels": {}},
    {"slug": "exercise_window",
     "title": "Test 6.5 — Post-termination option exercise window extraction",
     "corpus_desc": "real SEC-filed option grant agreement exhibits",
     "labels": {}},
    {"slug": "s1_risk_factors",
     "title": "Test 7.4 — S-1 risk-factor heading extraction",
     "corpus_desc": "real S-1/424B4 Risk Factors sections",
     "labels": {}},
    {"slug": "flag_missing_pro_rata",
     "title": "Test 8.5 — Explicit pro-rata waiver vs grant flag",
     "corpus_desc": "real SEC-filed investor rights agreements + waivers",
     "labels": {}},
    {"slug": "s1_use_of_proceeds",
     "title": "Test 7.3 — Primary use of IPO proceeds extraction",
     "corpus_desc": "real S-1/424B4 Use of Proceeds sections",
     "labels": {}},
    {"slug": "per_investor_allocation",
     "title": "Test 1.2.2 — Named investor's individual dollar allocation extraction",
     "corpus_desc": "real SEC Schedule 13D/13D-A filings (investor-side)",
     "labels": {}},
    {"slug": "option_pool_shuffle",
     "title": "Test 3.3 — Pre-money option pool price-per-share compute",
     "corpus_desc": "real SEC-filed Agreement for Future Equity worked examples (Form C exhibit)",
     "labels": {}},
    {"slug": "convert_vs_preference_decision",
     "title": "Test 4.4 — Convert-vs-take-preference decision (compute)",
     "corpus_desc": "real SEC-filed Agreement for Future Equity worked examples (Form C exhibit)",
     "labels": {"convert": "Convert", "take-preference": "Take preference"}},
    {"slug": "liquidation_waterfall_payout",
     "title": "Test 4.1 — Per-share value to common after preferred waterfall (compute)",
     "corpus_desc": "real SC 13E-3 going-private fairness opinion",
     "labels": {}},
    {"slug": "preference_stack_payout",
     "title": "Test 4.3 — Named preferred series' total waterfall payout (compute)",
     "corpus_desc": "real SC 13E-3 going-private fairness opinion",
     "labels": {}},
]

SIZE = {"gemma3-1b": "1B", "qwen3.5-27b": "27B", "deepseek-v4f": "hosted",
        "gemma": "12B", "deepseek": "hosted"}
ORDER = ["gemma3-1b", "qwen3.5-27b", "deepseek-v4f", "gemma", "deepseek"]


def load_leaf(slug):
    """Return (field, classes, scored, oracle) for a leaf, deriving field+classes from its task.TASK.
    classes is None for NUMBER-type fields (no enum buckets to break out by class)."""
    leaf = ROOT / "leaves" / slug
    spec = importlib.util.spec_from_file_location(f"task_{slug}", leaf / "task.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    field = list(mod.TASK["fields"])[0]
    classes = mod.TASK["fields"][field].get("values")
    scored = json.loads((leaf / "scored.json").read_text())
    oracle = [json.loads(l) for l in open(leaf / "oracle.jsonl") if l.strip()]
    return field, classes, scored, oracle


def wobble_pct(res, field):
    """% of items whose answer flipped at least once across the runs (the core metric)."""
    return res["reliability"]["field_flips"].get(field, 0.0) * 100


def response_rate_str(res):
    """
    What: formats the model's raw response rate as "<parsed>/<attempted> (<pct>%)".
    Why: engine/scorer.py computes valid_run_count and parse_failure_count for every leaf, but
         until this fix that data never reached the public README/RESULTS.md tables -- a model
         that silently failed to return ANY parseable answer on a meaningful share of its runs
         (e.g. a transient API 503, or a genuine malformed-JSON output) was invisible: wobble and
         accuracy are computed ONLY over the runs that DID parse, so a low response rate could
         hide behind an apparently-clean "100% accuracy" figure. Found on adversarial audit,
         2026-07-02: liquidation_waterfall_payout's deepseek-v4f run had a 22.5% parse-failure
         rate (94% of those were raw API 503s, not model failures) with zero visibility in the
         previously-shipped README. See root CLAUDE.md §0.7 "every failure is observable."
    Output: a string like "62/80 (78%)" -- attempted = valid_run_count + parse_failure_count.
    Success criteria: attempted should equal len(instances) * N_RUNS for a fully-run leaf; a
         response rate under 100% is a genuine signal worth a reader's attention, not noise.
    """
    r = res["reliability"]
    valid = r.get("valid_run_count", 0)
    attempted = valid + r.get("parse_failure_count", 0)
    pct = (valid / attempted * 100) if attempted else 0.0
    return f"{valid}/{attempted} ({pct:.0f}%)"


def per_class(per_instance, oracle, field, classes):
    out = {c: [0, 0] for c in classes}
    for row, o in zip(per_instance, oracle):
        if row["n_valid"] == 0:
            continue
        out[o[field]][1] += 1
        out[o[field]][0] += int(row["majority_correct"])
    return out


def _models(scored):
    return [k for k in ORDER if k in scored] + [k for k in scored if k not in ORDER]


def _runs_each(scored):
    n = max((r["reliability"]["valid_run_count"] for r in scored.values()), default=0)
    per = max((len(r["accuracy"]["per_instance"]) for r in scored.values()), default=1)
    return n // per if per else 0


def definitions(labels, generic=False, has_classes=True):
    lines = [
        "**What the columns mean:**\n",
        "- **Wobble** (headline, lower is better) — the share of items where the model gave **more "
        "than one answer** across its 20 identical runs. A model that wobbles can't be trusted in a "
        "money workflow even when it's often right.",
        "- **Consistency** — the *average* agreement **within** each item's runs (how often they "
        "matched that item's most common answer). Wobble counts *whether* an item flipped; "
        "Consistency measures *how much*.",
        "- **Accuracy** — the share of items whose majority answer matched the human-validated truth.",
        "- **Response rate** — the share of the model's attempted runs that returned a parseable "
        "answer at all (parsed / attempted). A run can fail to parse for two different reasons: the "
        "model emitted malformed/non-JSON output, or the API call itself errored (rate limit, "
        "timeout, 5xx). Wobble and Accuracy are computed *only* over the runs that DID parse, so a "
        "low response rate is a distinct reliability signal, not folded into either headline number — "
        "a model can look perfectly consistent and accurate while silently failing to answer a "
        "meaningful share of the time.",
    ]
    if has_classes:
        cols = "the right-hand class columns" if generic else " · ".join(labels.values())
        lines.append(f"- **{cols}** — accuracy **within** each true class (correct / total), so a model can't "
                     "score well by always guessing the most common class.")
    return "\n".join(lines)


def _wobble_table(scored, field):
    L = ["| Model | Size | **Wobble** ↓ | Consistency | Accuracy (majority) | Measurable | Response rate |",
         "|---|---|---|---|---|---|---|"]
    for k in _models(scored):
        res = scored[k]; a = res["accuracy"]; r = res["reliability"]
        L.append(f"| `{res['model']}` | {SIZE.get(k,'?')} | **{wobble_pct(res,field):.0f}%** | "
                 f"{r['consistency_pct']:.0f}% | {a['accuracy_majority']*100:.0f}% | "
                 f"{a['n_measurable']}/{a['n_instances']} | {response_rate_str(res)} |")
    return L


def _class_table(scored, oracle, field, classes, labels):
    L = ["| Model | " + " | ".join(labels[c] for c in classes) + " |",
         "|---|" + "---|" * len(classes)]
    for k in _models(scored):
        pc = per_class(scored[k]["accuracy"]["per_instance"], oracle, field, classes)
        L.append(f"| `{scored[k]['model']}` | " +
                 " | ".join(f"{pc[c][0]}/{pc[c][1]}" if pc[c][1] else "—" for c in classes) + " |")
    return L


def auto_findings(scored, oracle, field, classes):
    """Data-driven summary when a leaf has no hand-written findings: cliff + best model."""
    rows = [(SIZE.get(k, k), wobble_pct(scored[k], field),
             scored[k]["accuracy"]["accuracy_majority"] * 100) for k in _models(scored)]
    best = min(rows, key=lambda x: (x[1], -x[2]))
    hi = max(r[1] for r in rows); lo = min(r[1] for r in rows)
    L = ["## What this shows\n"]
    L.append(f"- **Wobble spread: {lo:.0f}%–{hi:.0f}% across the ladder.** "
             f"Lowest-wobble model: **{best[0]}** ({best[1]:.0f}% wobble, {best[2]:.0f}% accuracy).")
    if hi - lo >= 30:
        L.append("- **Wobble is a cliff, not a slope** — small models flip on a large share of items "
                 "while larger models collapse to near-zero; the usable boundary is a jump, not a gradient.")
    return "\n".join(L)


PART_FINDINGS = """## What this shows

- **Participating preferred is the universal blind spot.** Even the best models get only 1-2 of 5
  participating clauses right; the small models get 0. The "preference AND THEN also share with the
  common" structure is systematically misread as capped or non-participating.
- **Small models can't classify the hard classes at all** (1B: 0/5 participating, 0/5 capped) -
  they collapse everything to non-participating."""

SAFE_FINDINGS = """## What this shows

- **Accuracy does not imply trustworthiness — the cleanest case yet.** deepseek-v4-flash answers
  every one of the 16 SAFEs correctly (100% accuracy) yet still **wobbles on 19% of them** across 20
  identical runs. A model you would call "100% accurate" from a single pass changes its answer on
  ~1 in 5 items when you actually repeat the question. Wobble catches what an accuracy score hides.
- **Low wobble can mask low accuracy.** gemma3:1b looks stable (6% wobble) but is only 62% accurate -
  it confidently and *repeatably* gives the wrong pre/post classification. Consistency without
  accuracy is its own trap; this is why the two numbers are never averaged."""

FINDINGS = {"participation_type": PART_FINDINGS, "safe_pre_post": SAFE_FINDINGS}


def render_leaf(cfg):
    field, classes, scored, oracle = load_leaf(cfg["slug"])
    labels = cfg["labels"]; total = len(oracle)
    if classes:
        counts = {c: sum(o[field] == c for o in oracle) for c in classes}
        bal = " / ".join(f"{counts[c]} {labels[c]}" for c in classes)
    else:
        vals = [o[field] for o in oracle]
        bal = f"values range {min(vals)}-{max(vals)}" if vals else "n/a"
    L = [f"## {cfg['title']}\n"]
    L.append(f"**Corpus:** {total} {cfg['corpus_desc']}, human-validated answers ({bal}). "
             f"Each model run **{_runs_each(scored)}×/item at temp 0.7**.\n")
    L.append("### Headline — WOBBLE (the core metric)\n")
    L.append("*Wobble = % of items where the model gave more than one answer across its runs. "
             "A model that wobbles cannot be trusted in a money workflow even when it is often right.*\n")
    L += _wobble_table(scored, field)
    L.append("\n" + definitions(labels, has_classes=bool(classes)) + "\n")
    if classes:
        L.append("\n### Accuracy by class (majority vote)\n")
        L += _class_table(scored, oracle, field, classes, labels)
    L.append("\n### Which items make models wobble\n")
    L.append("| Item | True | Difficulty | Models that wobbled |")
    L.append("|---|---|---|---|")
    for i, o in enumerate(oracle):
        wob = [SIZE.get(k, k) for k in _models(scored)
               if scored[k]["accuracy"]["per_instance"][i]["fields"].get(field, {}).get("consistency", 1.0) < 1.0]
        if wob:
            L.append(f"| {o['company'][:22]} | {o[field]} | {o.get('difficulty','?')} | {', '.join(wob)} |")
    L.append("\n" + FINDINGS.get(cfg["slug"]) if cfg["slug"] in FINDINGS
             else "\n" + auto_findings(scored, oracle, field, classes))
    return "\n".join(L)


def readme_block_for(cfg):
    field, classes, scored, oracle = load_leaf(cfg["slug"])
    labels = cfg["labels"]; total = len(oracle)
    if classes:
        counts = {c: sum(o[field] == c for o in oracle) for c in classes}
        bal = " / ".join(f"{counts[c]} {labels[c]}" for c in classes)
    else:
        vals = [o[field] for o in oracle]
        bal = f"values range {min(vals)}-{max(vals)}" if vals else "n/a"
    L = [f"**{cfg['title']}** — {total} clauses ({bal}), each model run {_runs_each(scored)}×/item:", ""]
    class_header = " | " + " | ".join(labels[c] for c in classes) if classes else ""
    L.append("| Model | Size | **Wobble** ↓ | Consistency | Accuracy | Response rate" + class_header + " |")
    L.append("|---|---|---|---|---|---|" + ("---|" * len(classes) if classes else ""))
    for k in _models(scored):
        res = scored[k]; a = res["accuracy"]; r = res["reliability"]
        if classes:
            pc = per_class(a["per_instance"], oracle, field, classes)
            cells = " | " + " | ".join(f"{pc[c][0]}/{pc[c][1]}" if pc[c][1] else "-" for c in classes)
        else:
            cells = ""
        L.append(f"| `{res['model']}` | {SIZE.get(k,'?')} | **{wobble_pct(res,field):.0f}%** | "
                 f"{r['consistency_pct']:.0f}% | {a['accuracy_majority']*100:.0f}% | {response_rate_str(res)}{cells} |")
    return "\n".join(L)


def _present_leaves():
    return [c for c in LEAVES if (ROOT / "leaves" / c["slug"] / "scored.json").exists()]



FAMILY_DISPLAY = {
    "priced_equity": "Priced equity rounds",
    "convertibles": "SAFEs & convertible notes",
    "cap_table": "Cap table math",
    "exit_waterfall": "Exit waterfalls",
    "rights_governance": "Investor rights & governance",
    "founder_equity": "Founder & employee vesting",
    "regulatory": "Regulatory disclosures",
    "risk_flag": "Off-market risk flags",
}

MODEL_DISPLAY = {
    "gemma3-1b": ("gemma3:1b", "1B, local"),
    "gemma3-1b-qat": ("gemma3:1b-it-qat", "1B QAT, local"),
    "qwen3.5-27b": ("qwen3.5:27b", "27B, local"),
    "deepseek-v4f": ("deepseek-v4-flash", "hosted"),
    # OpenRouter lineup added 2026-07-02 -- hosted, no local heat/time limit (Eikiyo: "not
    # limited by laptop anymore"). Label is the guard/checkpoint label from
    # engine/runner.openrouter_model_set(), not the raw OpenRouter model id.
    "gemma4-31b-or": ("gemma-4-31b-it", "31B, hosted (OR)"),
    "mistral-large-or": ("mistral-large-2512", "hosted (OR)"),
    "minimax-m2.5-or": ("minimax-m2.5", "hosted (OR)"),
    "llama3.3-70b-or": ("llama-3.3-70b", "70B, hosted (OR)"),
    "gemini3-flash-or": ("gemini-3-flash", "hosted (OR)"),
    "gpt-oss-120b-or": ("gpt-oss-120b", "120B, hosted (OR)"),
    "gpt5-mini-or": ("gpt-5-mini", "hosted (OR)"),
    "haiku-4.5-direct": ("claude-haiku-4.5", "direct API"),
}


def badge(pct, lower_is_better):
    """A colored shields.io pill for a percentage -- green/yellow/red by threshold."""
    if pct is None:
        return "—"
    if lower_is_better:
        color = "brightgreen" if pct < 10 else "yellow" if pct < 30 else "red"
    else:
        color = "brightgreen" if pct > 85 else "yellow" if pct > 60 else "red"
    label = f"{pct:.0f}%25"
    return f"![{pct:.0f}%](https://img.shields.io/badge/-{label}-{color})"


def aggregate_by_model():
    """N-weighted wobble + accuracy per model, across every built leaf that has a scored.json."""
    reg = json.loads((ROOT / "engine" / "registry.json").read_text())
    built = [l for l in reg["leaves"] if l.get("tier") == "built" and "leaf" in l]
    wobble_num, wobble_den = {}, {}
    acc_num, acc_den = {}, {}
    leaf_count = {}
    for l in built:
        sp = ROOT / l["leaf"] / "scored.json"
        if not sp.exists():
            continue
        scored = json.loads(sp.read_text())
        field = l["field"]
        for model, res in scored.items():
            rel, acc = res.get("reliability", {}), res.get("accuracy", {})
            n_inst = acc.get("n_instances", 0)
            n_meas = acc.get("n_measurable", 0)
            flip = rel.get("field_flips", {}).get(field)
            if flip is None or not rel.get("measurable", True) or not n_inst:
                continue
            wobble_num[model] = wobble_num.get(model, 0) + flip * n_inst
            wobble_den[model] = wobble_den.get(model, 0) + n_inst
            if n_meas:
                acc_num[model] = acc_num.get(model, 0) + acc.get("accuracy_majority", 0) * n_meas
                acc_den[model] = acc_den.get(model, 0) + n_meas
            leaf_count[model] = leaf_count.get(model, 0) + 1
    # A model with a handful of leaves is a one-off smoke test, not a suite measurement --
    # excluded so a stray spot-check never pollutes the headline table.
    MIN_LEAVES_FOR_SUITE_TABLE = 10
    out = []
    for model in sorted(wobble_den, key=lambda m: -leaf_count[m]):
        if leaf_count[model] < MIN_LEAVES_FOR_SUITE_TABLE:
            continue
        w = 100 * wobble_num[model] / wobble_den[model] if wobble_den[model] else None
        a = 100 * acc_num[model] / acc_den[model] if acc_den.get(model) else None
        out.append({"model": model, "leaves": leaf_count[model], "wobble": w, "accuracy": a,
                    "n_items": int(wobble_den[model])})
    return out


def aggregate_by_family():
    """N-weighted wobble + accuracy per registry family, averaged ACROSS EVERY MODEL in the
    current lineup -- not pinned to one model. Was pinned to deepseek-v4f until 2026-07-03
    because it was the only model with full 60/60 coverage at the time; now all 11 models in
    MODEL_DISPLAY hit full coverage, so picking one model would hide how every other model
    performs per category (Eikiyo: "why cant this be average of all models?"). "leaves" counts
    DISTINCT test leaves that contributed at least one model's measurable result, not
    leaf*model combinations -- so the Tests column still reads as "how many of the 60 tests are
    in this category," unchanged in meaning from the single-model version."""
    reg = json.loads((ROOT / "engine" / "registry.json").read_text())
    built = [l for l in reg["leaves"] if l.get("tier") == "built" and "leaf" in l]
    wobble_num, wobble_den = {}, {}
    acc_num, acc_den = {}, {}
    leaf_ids = {}
    for l in built:
        sp = ROOT / l["leaf"] / "scored.json"
        if not sp.exists():
            continue
        scored = json.loads(sp.read_text())
        field, fam = l["field"], l["family"]
        counted = False
        for model_label, res in scored.items():
            rel, acc = res.get("reliability", {}), res.get("accuracy", {})
            n_inst = acc.get("n_instances", 0)
            n_meas = acc.get("n_measurable", 0)
            flip = rel.get("field_flips", {}).get(field)
            if flip is None or not rel.get("measurable", True) or not n_inst:
                continue
            wobble_num[fam] = wobble_num.get(fam, 0) + flip * n_inst
            wobble_den[fam] = wobble_den.get(fam, 0) + n_inst
            if n_meas:
                acc_num[fam] = acc_num.get(fam, 0) + acc.get("accuracy_majority", 0) * n_meas
                acc_den[fam] = acc_den.get(fam, 0) + n_meas
            counted = True
        if counted:
            leaf_ids.setdefault(fam, set()).add(l["leaf"])
    out = []
    for fam in sorted(wobble_den, key=lambda f: -len(leaf_ids[f])):
        w = 100 * wobble_num[fam] / wobble_den[fam] if wobble_den[fam] else None
        a = 100 * acc_num[fam] / acc_den[fam] if acc_den.get(fam) else None
        out.append({"family": fam, "leaves": len(leaf_ids[fam]), "wobble": w, "accuracy": a})
    return out


def suite_summary_table():
    """THE headline table: does wobble fall as model capability rises?"""
    rows = aggregate_by_model()
    lines = ["| Model | Size | Tests covered | **Wobble** ↓ | Accuracy |",
             "|---|---|---|---|---|"]
    for r in rows:
        name, size = MODEL_DISPLAY.get(r["model"], (r["model"], "?"))
        lines.append(f"| `{name}` | {size} | {r['leaves']} | {badge(r['wobble'], True)} | "
                      f"{badge(r['accuracy'], False)} |")
    return "\n".join(lines)


def family_summary_table():
    """One row per fundraising-document category, N-weighted average ACROSS EVERY MODEL in the
    lineup (see aggregate_by_family() docstring for why this isn't pinned to one model)."""
    rows = aggregate_by_family()
    lines = ["| Category | Tests | **Wobble** ↓ (all models) | Accuracy (all models) |",
             "|---|---|---|---|"]
    for r in rows:
        label = FAMILY_DISPLAY.get(r["family"], r["family"])
        lines.append(f"| {label} | {r['leaves']} | {badge(r['wobble'], True)} | "
                      f"{badge(r['accuracy'], False)} |")
    return "\n".join(lines)


def main():
    present = _present_leaves()
    header = ("# Probity — Benchmark Results\n\n"
              "**Wobble** = run-to-run inconsistency (the core metric): ask the same question 20× at "
              "temperature 0.7 and count how often the answer changes. **Accuracy** = % correct vs a "
              "human-validated answer extracted from the source document. They are reported separately "
              "and never averaged — a model can be perfectly consistent and consistently wrong.\n\n"
              "Models span a size ladder (1B → 12B local + a hosted model) to test whether wobble "
              "falls as capability rises. Local via Ollama (zero egress); hosted = deepseek-v4-flash.\n\n---\n\n")
    body = "\n\n---\n\n".join(render_leaf(c) for c in present)
    (ROOT / "results" / "RESULTS.md").write_text(header + body + REPRO + "\n", encoding="utf-8")
    print(f"wrote results/RESULTS.md ({len(present)} leaves)")

    cap = (f"*{len(present)} tests, each item run 20x/item at temp 0.7 across a model size ladder. "
           "**Wobble** (lower = better) is the run-to-run inconsistency rate, weighted by item "
           "count across every test that model ran. Full per-test breakdown (all "
           f"{len(present)} tables): [`results/RESULTS.md`](results/RESULTS.md).*\n")
    block = ("<!-- BENCHMARK:START -->\n" + cap +
             "\n### Does reliability improve with model size?\n\n" + suite_summary_table() +
             "\n\n### By fundraising-document category\n\n" + family_summary_table() +
             "\n\n<!-- BENCHMARK:END -->")
    readme = ROOT / "README.md"
    txt = re.sub(r"<!-- BENCHMARK:START.*?-->.*?<!-- BENCHMARK:END -->", lambda m: block,
                 readme.read_text(), flags=re.S)
    readme.write_text(txt, encoding="utf-8")
    print(f"injected 2 summary tables (suite + by-category) into README.md")


REPRO = """

---

## Models and scope

Per leaf during the build-out, Probity runs the **fast set** (1B/3B/12B local via Ollama, zero
egress, plus deepseek-v4-flash) so a leaf costs minutes. The **heavy comprehensive run**
(qwen3.5:27b and hosted frontier models - Gemini, Haiku, etc. - at N=20+) is deferred to a single
sweep across all leaves once the full benchmark exists.

## Reproduce

```bash
cd leaves/<test_name>
python3 source.py          # fetch the real SEC documents
python3 run.py             # run the model ladder, N=20
python3 ../../results/render.py
```

Answers are human-validated from each document's own legal text (`leaves/<test>/oracle.jsonl`, with
the validating quote + difficulty per item). Genuinely ambiguous clauses are excluded, not guessed.
"""

if __name__ == "__main__":
    main()
