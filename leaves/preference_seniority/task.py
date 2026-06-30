"""
Location: leaves/preference_seniority/task.py
Purpose: Leaf 1.3.4 — classify the inter-series liquidation seniority of a multi-series preferred
         charter as pari-passu (all series rank equally) or stacked (a seniority order). The model
         reads the real liquidation clause and maps whether one series is paid before another.
Functions: build_prompt(), TASK
"""

_SYSTEM = (
    "You are a venture-financing lawyer. A company has MORE THAN ONE series of preferred stock. Read "
    "the liquidation provision below and classify how the preferred SERIES rank against EACH OTHER on "
    "a liquidation: PARI-PASSU or STACKED."
)
_TAXONOMY = (
    "Classify into exactly one of these categories:\n"
    "- \"pari-passu\": the preferred series rank EQUALLY with each other. On a liquidation they share "
    "the available proceeds together, ratably / in proportion to their preferences — no series is paid "
    "before another. Tell-tale: 'rank pari passu', 'on a parity', the proceeds 'distributed/shared "
    "ratably among the holders of the Preferred Stock' (all series together), 'distributed among them "
    "pro rata'.\n"
    "- \"stacked\": the preferred series rank in a SENIORITY ORDER. A senior series is paid its full "
    "liquidation preference FIRST, before any junior series receives anything. Tell-tale: 'the Series X "
    "ranks senior to the Series Y', 'in the following order of priority', 'junior to the Series Z', "
    "one series' preference paid 'prior to' another series receiving any distribution.\n"
)
_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"preference_seniority": "pari-passu" | "stacked"}\n'
)


def build_prompt(instance: dict) -> str:
    clause = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nLIQUIDATION PROVISION:\n{clause}\n\nJSON:"


TASK = {
    "name": "preference_seniority",
    "description": "Classify multi-series preferred liquidation seniority as pari-passu or stacked (1.3.4).",
    "fields": {"preference_seniority": {"type": "enum", "values": ["pari-passu", "stacked"],
               "description": "Whether preferred series rank equally (pari-passu) or in a seniority order (stacked)."}},
    "stakes_weight": 5,
    "build_prompt": build_prompt,
}
