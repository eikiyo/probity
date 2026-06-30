"""
Location: projects/AI-PM/Knowledge/probe/normalize.py
Purpose: Canonicalize field values before equality comparison (SP4 mitigation)
Functions: canonical()
Calls: (none)
Imports: unicodedata, re
"""

import unicodedata
import re
from typing import Any, Union


def canonical(value: Any, field_type: str) -> Union[str, float, bool, None]:
    """
    Canonicalize a value for equality comparison.
    Handles: NFKD, whitespace, case folding, number normalization.
    Returns the canonical form or None if unparseable (fail closed).
    """
    if value is None:
        return None

    if field_type == "number":
        return _canonical_number(value)
    elif field_type == "enum":
        return _canonical_enum(value)
    elif field_type == "bool":
        return _canonical_bool(value)
    else:
        return None


def _canonical_number(value: Any) -> Union[float, None]:
    """Normalize number: strip currency, commas, whitespace, parse to float."""
    try:
        if isinstance(value, (int, float)):
            return float(value)

        # String: strip currency, commas, whitespace
        s = str(value).strip()
        s = re.sub(r"[\$,\s]", "", s)  # Remove $, comma, space
        return float(s)
    except (ValueError, AttributeError):
        return None


def _canonical_enum(value: Any) -> Union[str, None]:
    """Normalize enum: NFKD decompose, lowercase, strip whitespace."""
    try:
        s = str(value).strip()
        # NFKD decompose (turn accented chars to base + diacritics, then strip diacritics)
        s = unicodedata.normalize("NFKD", s)
        s = s.encode("ascii", "ignore").decode("ascii")  # Strip diacritics
        s = s.lower()
        return s
    except (ValueError, AttributeError):
        return None


def _canonical_bool(value: Any) -> Union[bool, None]:
    """Normalize bool: parse true/false/yes/no/1/0, case-insensitive."""
    try:
        if isinstance(value, bool):
            return value
        s = str(value).strip().lower()
        if s in ("true", "yes", "1", "y"):
            return True
        elif s in ("false", "no", "0", "n"):
            return False
        else:
            return None
    except (ValueError, AttributeError):
        return None
