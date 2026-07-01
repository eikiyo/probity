"""
Location: leaves/securities_exemption/task.py
Purpose: Leaf 7.1 — classify which Securities Act exemption a Form D filing claimed.
         Single enum field; the model reads the real exemption information from a Form D
         and classifies into the standard taxonomy.
Functions: build_prompt(), TASK
Calls: (none)
Imports: (none)
"""

_SYSTEM = (
    "You are a securities lawyer. Read the federal exemption information from a Form D filing below "
    "and classify which Securities Act exemption was claimed for this offering."
)

_TAXONOMY = (
    "Classify into exactly one of these standard categories:\n"
    "- \"506b\": Regulation D, Rule 506(b) — accredited investors + up to 35 non-accredited.\n"
    "- \"506c\": Regulation D, Rule 506(c) — accredited investors only, with general solicitation.\n"
    "- \"504\": Regulation D, Rule 504 — small offerings up to $5M.\n"
    "- \"reg-a\": Regulation A — small public offering (Tier 1 or Tier 2).\n"
    "- \"other\": Section 4(a)(2), Section 4(a)(6), or other exemption.\n"
)

_INSTRUCTION = (
    'Respond with ONLY this JSON object, nothing else:\n'
    '{"securities_exemption": "506b" | "506c" | "504" | "reg-a" | "other"}\n'
)


def build_prompt(instance: dict) -> str:
    """Stable prefix then the exemption information excerpt."""
    exemption_text = instance.get("document", "")
    return f"{_SYSTEM}\n\n{_TAXONOMY}\n{_INSTRUCTION}\nFORM D EXEMPTION INFORMATION:\n{exemption_text}\n\nJSON:"


TASK = {
    "name": "securities_exemption",
    "description": "Classify which Securities Act exemption a Form D filing claimed (7.1).",
    "fields": {
        "securities_exemption": {
            "type": "enum",
            "values": ["506b", "506c", "504", "reg-a", "other"],
            "description": "The federal exemption claimed in the Form D filing.",
        }
    },
    "stakes_weight": 3,
    "build_prompt": build_prompt,
}
