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
    elif field_type == "date":
        return _canonical_date(value)
    elif field_type == "string":
        return _canonical_enum(value)  # same normalization: NFKD + casefold + trim
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


_MONTHS = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
           "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
           "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
           "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12}


def _canonical_date(value: Any) -> Union[str, None]:
    """Normalize a date to ISO YYYY-MM-DD. Handles ISO input and 'Month D, YYYY' / 'D Month YYYY'
    prose forms (the two shapes the model is expected to see/emit); fail closed (None) on anything
    else rather than guess."""
    try:
        s = str(value).strip()
        m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
        if m:
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            return f"{y:04d}-{mo:02d}-{d:02d}"
        m = re.match(r"^([A-Za-z]+)\.?\s+(\d{1,2}),?\s+(\d{4})$", s)
        if m and m.group(1).lower() in _MONTHS:
            mo = _MONTHS[m.group(1).lower()]
            return f"{int(m.group(3)):04d}-{mo:02d}-{int(m.group(2)):02d}"
        m = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\.?,?\s+(\d{4})$", s)
        if m and m.group(2).lower() in _MONTHS:
            mo = _MONTHS[m.group(2).lower()]
            return f"{int(m.group(3)):04d}-{mo:02d}-{int(m.group(1)):02d}"
        return None
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
