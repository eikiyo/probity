"""
Location: tests/test_lenient_extract.py
Purpose: TDD for harness._lenient_extract() -- a fallback answer-extraction step tried only when
         strict JSON parsing fails. Added 2026-07-03 per Eikiyo: "goal is not to judge JSON, to
         judge reasoning of the financial docs" -- format noise (an invalid backslash escape, a
         wrong-but-unambiguous JSON key, a bare value with no JSON wrapper) should not be scored
         as a reasoning failure when the model's actual answer is unambiguously recoverable. Every
         leaf has exactly ONE scored field (verified repo-wide, all 60), which is what makes a
         "wrong key name" or "no JSON at all" fallback safe: there is only one field it could mean.
         Must still fail closed (return None) on genuinely ambiguous or multi-value raw text --
         this is answer recovery, not guessing.
Run: cd tests && python3 -m unittest test_lenient_extract -v
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

import harness  # noqa: E402

NUMBER_FIELDS = {"dividend_rate_pct": {"type": "number"}}
ENUM_FIELDS = {"safe_pre_post": {"type": "enum", "values": ["pre-money", "post-money"]}}
BOOL_FIELDS = {"pro_rata_rights": {"type": "bool"}}
STRING_FIELDS = {"vesting_schedule": {"type": "string"}}


class TestJsonEscapeRepair(unittest.TestCase):
    def test_repairs_invalid_backslash_underscore_in_key(self):
        raw = '{"safe_cap\\_type": "post-money"}'
        out = harness._lenient_extract(raw, ENUM_FIELDS)
        self.assertEqual(out, {"safe_pre_post": "post-money"})

    def test_repairs_invalid_backslash_underscore_double(self):
        raw = '{"form_d\\_field\\_value": "2366532"}'
        out = harness._lenient_extract(raw, {"form_d_field_value": {"type": "number"}})
        self.assertEqual(out, {"form_d_field_value": "2366532"})

    def test_repairs_bare_unevaluated_division_for_number_field(self):
        # observed gemma3-1b-qat failure on option_pool_shuffle: model answers with an
        # unevaluated division instead of computing the number.
        raw = '{"option_pool_shuffle": 1000000 / 11000000}\n'
        out = harness._lenient_extract(raw, {"option_pool_shuffle": {"type": "number"}})
        self.assertAlmostEqual(float(out["option_pool_shuffle"]), 1000000 / 11000000, places=5)

    def test_division_repair_never_touches_quoted_slash_in_string_value(self):
        raw = '{"vesting_schedule": "4yr/1yr-cliff"}'
        out = harness._lenient_extract(raw, STRING_FIELDS)
        self.assertEqual(out, {"vesting_schedule": "4yr/1yr-cliff"})

    def test_division_repair_fails_closed_on_division_by_zero(self):
        raw = '{"dividend_rate_pct": 5 / 0}'
        out = harness._lenient_extract(raw, NUMBER_FIELDS)
        self.assertIsNone(out)


class TestSingleKeyFallback(unittest.TestCase):
    def test_single_key_dict_with_wrong_name_is_used(self):
        raw = '{"pro_rata\\_rights": "yes"}'
        out = harness._lenient_extract(raw, BOOL_FIELDS)
        self.assertEqual(out, {"pro_rata_rights": "yes"})

    def test_multi_key_dict_with_no_matching_name_fails_closed(self):
        raw = '{"reasoning": "the clause says post-money", "other_field": "post-money"}'
        out = harness._lenient_extract(raw, ENUM_FIELDS)
        self.assertIsNone(out)

    def test_dict_with_matching_field_name_uses_that_key_not_fallback(self):
        raw = '{"other_junk": "wrong", "safe_pre_post": "pre-money"}'
        out = harness._lenient_extract(raw, ENUM_FIELDS)
        self.assertEqual(out, {"safe_pre_post": "pre-money"})


class TestBareValueFallback(unittest.TestCase):
    def test_bare_number_no_json_wrapper(self):
        out = harness._lenient_extract("6\n", NUMBER_FIELDS)
        self.assertEqual(out, {"dividend_rate_pct": "6"})

    def test_bare_number_with_decimal(self):
        out = harness._lenient_extract("8.0\n", NUMBER_FIELDS)
        self.assertEqual(out, {"dividend_rate_pct": "8.0"})

    def test_bare_currency_number(self):
        out = harness._lenient_extract("$2,366,532", {"form_d_field_value": {"type": "number"}})
        self.assertEqual(out, {"form_d_field_value": "$2,366,532"})

    def test_bare_enum_word_matches_allowed_value(self):
        out = harness._lenient_extract("post-money", ENUM_FIELDS)
        self.assertEqual(out, {"safe_pre_post": "post-money"})

    def test_bare_enum_word_case_insensitive(self):
        out = harness._lenient_extract("POST-MONEY", ENUM_FIELDS)
        self.assertEqual(out, {"safe_pre_post": "POST-MONEY"})

    def test_bare_enum_word_not_in_allowed_values_fails_closed(self):
        out = harness._lenient_extract("somewhere-else", ENUM_FIELDS)
        self.assertIsNone(out)

    def test_bare_bool_yes(self):
        out = harness._lenient_extract("yes", BOOL_FIELDS)
        self.assertEqual(out, {"pro_rata_rights": "yes"})

    def test_bare_string_short_answer(self):
        out = harness._lenient_extract("4yr/1yr-cliff", STRING_FIELDS)
        self.assertEqual(out, {"vesting_schedule": "4yr/1yr-cliff"})


class TestFailsClosedOnAmbiguity(unittest.TestCase):
    def test_empty_string_fails_closed(self):
        self.assertIsNone(harness._lenient_extract("", NUMBER_FIELDS))
        self.assertIsNone(harness._lenient_extract(None, NUMBER_FIELDS))

    def test_multi_sentence_prose_fails_closed(self):
        raw = ("Looking at the clause, the dividend rate appears to be 6% based on the "
               "preferred stock terms outlined in section 4.2 of the agreement.")
        out = harness._lenient_extract(raw, NUMBER_FIELDS)
        self.assertIsNone(out)

    def test_prompt_template_echo_fails_closed(self):
        # The real bug that motivated this: gemma3:1b parroting the prompt's pipe-notation
        # example verbatim instead of choosing one value -- must NOT be treated as an answer.
        raw = '{"vesting_schedule": "4yr/1yr-cliff" | "3yr/no-cliff" | ...}'
        out = harness._lenient_extract(raw, STRING_FIELDS)
        self.assertIsNone(out)

    def test_garbled_unparseable_json_fails_closed(self):
        raw = '{"vesting_schedule": "4yr/1yr-cliff}'
        out = harness._lenient_extract(raw, STRING_FIELDS)
        self.assertIsNone(out)

    def test_multiline_bare_text_fails_closed(self):
        raw = "First guess: 6\nActually maybe 8"
        out = harness._lenient_extract(raw, NUMBER_FIELDS)
        self.assertIsNone(out)


if __name__ == "__main__":
    unittest.main()
