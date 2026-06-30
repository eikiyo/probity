"""
Location: leaves/protective_provisions/task.py
Purpose: Leaf 5.2 -- classify whether a document grants preferred stockholders/investors PROTECTIVE
         PROVISIONS -- specified corporate actions (e.g. amending the charter, authorizing senior
         stock, a merger, increasing the option pool) require the separate consent/affirmative vote of
         a majority/supermajority of a class of investors/preferred -- or does NOT.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. Read the document excerpt below and classify whether it "
    "grants investors/preferred stockholders PROTECTIVE PROVISIONS -- a veto right requiring their "
    "separate class consent for specified corporate actions -- or does NOT."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"yes\": the excerpt grants investors/a class of preferred (or unit) holders the right that "
    "specified corporate actions require THEIR separate affirmative vote or written consent "
    "('Protective Provisions', 'shall not, without the consent of the holders of at least [X%]', "
    "'voting as a separate class/series').\n"
    "- \"no\": the excerpt does NOT grant this -- no such veto mechanism is shown. This includes "
    "plain corporate documents with no class-consent requirement at all (e.g. a Letter of Intent, a "
    "post-IPO charter where preferred has converted/been eliminated, generic Articles of "
    "Incorporation with only default majority-of-all-stock voting).\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"protective_provisions": "yes" | "no"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nDOCUMENT EXCERPT:\n{clause}\n\nJSON:"


TASK = {
    "name": "protective_provisions",
    "description": "Classify whether a document grants investors protective-provisions class-veto rights (5.2).",
    "fields": {"protective_provisions": {"type": "enum", "values": ["yes", "no"],
               "description": "yes if investors hold a class-consent veto right, else no."}},
    "stakes_weight": 4,
    "build_prompt": build_prompt,
}
