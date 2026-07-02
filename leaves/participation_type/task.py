"""
Location: leaves/participation_type/task.py
Purpose: Leaf 1.3.2 — classify a preferred-stock liquidation provision's participation type.
         Single enum field; prompt gives the standard textbook taxonomy, the model must read the
         real clause and map it. Compatible with engine/harness.run_harness (task-dict API).
Functions: build_prompt(), TASK
Calls: (none -- this file has no imports and no dependency on any other leaf or engine module
       except being IMPORTED BY engine/runner.py, which reads TASK to learn how to run this leaf.)
Imports: (none)

INTERN-LEVEL PRIMER (what "participation type" even means, for anyone new to VC cap tables):
When a company is sold or liquidated, the proceeds get split between preferred stockholders (the
investors) and common stockholders (usually founders/employees) according to whatever the charter
says. "Participation" is the single most consequential lever in that split, because it decides
whether investors get to "double dip":
  - NON-PARTICIPATING: investor picks ONE of two options, whichever is bigger for them --
    (a) take their fixed liquidation preference (e.g. "1x my money back") and walk away, giving
    up any claim on the rest, OR (b) convert their preferred shares into common stock and take
    their pro-rata share of everything, like a common holder. They pick whichever number is
    larger. This is the FOUNDER-FRIENDLIER structure (investors don't get more than the bigger of
    the two numbers).
  - PARTICIPATING: investor gets BOTH -- their fixed preference AND ALSO a pro-rata share of
    whatever is left over afterward (as if their shares had converted to common), stacked on top.
    This is the INVESTOR-FRIENDLIER structure (strictly better for the investor than
    non-participating, in every outcome, hence sometimes called "double-dip preferred").
  - CAPPED (a.k.a. "capped participation"): a middle ground -- the investor DOES get to double-dip
    (preference + pro-rata share) like participating preferred, but only up to some stated
    ceiling (e.g. "total proceeds to preferred capped at 3x the original investment"). Past that
    ceiling, the extra upside flows to common instead.

WHY this leaf's classification is hard in practice (and why "stakes_weight": 5, the max): real
charters draft this in dense, cross-referencing legal prose across multiple lettered subsections
(2(a), 2(b), 2(c)...), and the SAME defined-term NAME can be misleading -- see the "Pfenex Inc."
item in oracle.jsonl for a concrete, verified example: its clause defines a "Maximum Participation
Amount," which SOUNDS like it means "capped participation," but classifying it correctly requires
tracing through a conditional threshold and comparing it against the ACTUAL dollar figures defined
elsewhere in the same document (see the adversarial-audit finding recorded in source.py's
docstring below -- this project's own oracle label for that item is under active dispute as of
2026-07-02, pending Eikiyo's confirmation, precisely because the "obvious" reading and the
"read every cross-referenced subsection and do the arithmetic" reading disagree).
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the preferred-stock liquidation provision below "
    "and classify how the preferred stock participates in liquidation proceeds."
)

_TAXONOMY = (
    "Classify into exactly one of these standard categories:\n"
    "- \"non-participating\": the preferred receives the GREATER OF (a) its liquidation preference "
    "OR (b) the amount it would get by converting to common — one or the other, not both.\n"
    "- \"participating\": the preferred receives its liquidation preference AND THEN ALSO shares "
    "the remaining assets together with the common stock (on an as-converted basis) — it double-dips.\n"
    "- \"capped\": participating, but the preferred's total take is limited to a stated cap "
    "(e.g. a multiple of the original issue price, or a 'Maximum Participation Amount').\n"
)

_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"participation_type": "non-participating" | "participating" | "capped"}\n'
)


def build_prompt(instance: dict) -> str:
    """
    What: assembles the exact text sent to the model for one benchmark item -- concatenates the
          fixed system framing (_SYSTEM), the fixed taxonomy definitions (_TAXONOMY), the fixed
          JSON-only instruction (_INSTRUCTION), and finally THIS item's real document excerpt.
    Why it's split into a "stable prefix + variable tail" shape: every one of the 18 items in
          this leaf gets the EXACT SAME system/taxonomy/instruction text -- only the clause at
          the end changes. Keeping those three pieces as module-level constants (rather than
          re-typing them per item) means (1) there's only ONE place to fix a typo in the
          taxonomy wording, and (2) it's trivially auditable that every item was asked the exact
          same question in the exact same way (no accidental per-item wording drift that could
          bias one item's classification difficulty relative to another).
    Input: instance -- a dict with key "document" holding this item's real clause text (built
           once by source.py's extract_clause() and cached to corpus/questions/<id>.txt).
    Output: a single string -- the full prompt as sent to the model via engine/harness.py's
            client.generate() call.
    Success criteria: the returned prompt must NOT contain the answer itself anywhere in the
            clause text -- i.e. the real document excerpt must describe the MECHANISM (what
            happens to the money) without ever literally stating the word "participating" /
            "non-participating" / "capped" as a self-applied label (verified for this leaf: zero
            of the 18 corpus/questions/*.txt files contain those words -- see the adversarial
            audit's grep check, source.py docstring for detail).
    """
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nLIQUIDATION PROVISION:\n{clause}\n\nJSON:"


# TASK is this leaf's public contract with engine/runner.py (same convention as every other leaf
# in this repo -- see leaves/liquidation_waterfall_payout/task.py for the fullest explanation of
# this contract if you're new to the codebase). "values" here (unlike a "number"-type leaf) gives
# the CLOSED set of valid answers -- this drives engine/results/render.py's per-class accuracy
# breakdown (does the model get "capped" right as often as "non-participating"?) and lets
# engine/scorer.py flag if a model ever emits a 4th, invalid answer (silently would be a parse
# mismatch -- the harness only accepts the model's literal string, it does NOT fuzzy-match against
# "values" for you, so a model answering "Participating" (capitalized) would need
# engine/normalize.py's casefold step to match "participating" -- see normalize._canonical_enum()).
TASK = {
    "name": "participation_type",
    "description": "Classify preferred-stock liquidation participation (1.3.2).",
    "fields": {
        "participation_type": {
            "type": "enum",
            "values": ["participating", "non-participating", "capped"],
            "description": "How the preferred participates in liquidation proceeds.",
        }
    },
    "stakes_weight": 5,  # max on this project's 1-5 scale: this is the ORIGINAL flagship leaf (Round 1).
    "build_prompt": build_prompt,
}
