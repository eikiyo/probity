"""
Location: engine/corpus_utils.py
Purpose: Shared utility functions for leaf corpus building (window extraction)
Functions: window_on()
Imports: re
"""
import re


def window_on(text, anchor, before=420, after=900):
    """
    Extract a contextual window around an anchor string in text.
    Returns (window, validating_quote) or (None, None) if anchor not found.
    - window: wider context for the model's input (~420 chars before, ~900 chars after)
    - validating_quote: tighter context for oracle validation (~20 chars before, ~90 chars after)
    """
    i = text.lower().find(anchor.lower())
    if i < 0:
        return None, None
    s = max(0, i - before)
    e = min(len(text), i + len(anchor) + after)
    win = re.sub(r"[ \t]+", " ", text[s:e]).strip()
    qs = max(0, i - 20)
    qe = min(len(text), i + len(anchor) + 90)
    return win, re.sub(r"\s+", " ", text[qs:qe]).strip()
