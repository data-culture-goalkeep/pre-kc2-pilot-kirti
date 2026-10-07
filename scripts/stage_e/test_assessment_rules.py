#!/usr/bin/env python3
"""Focused tests for PM-approved assessment and attendance rules."""
import unittest

from stage_e_common import (
    ASSESSMENT_SCORE_MEANINGS,
    ATTENDANCE_MEANINGS,
    assessment_effective_score,
    calculate_assessment_average,
    parse_assessment_score,
)


class AssessmentRuleTest(unittest.TestCase):
    def test_numeric_zero_is_valid_and_preserved(self):
        self.assertEqual(parse_assessment_score("0"), (0, None))

    def test_numeric_ten_is_valid(self):
        self.assertEqual(parse_assessment_score("10"), (10, None))

    def test_absent_code_is_valid_and_preserved(self):
        self.assertEqual(parse_assessment_score("A"), (None, "A"))
        self.assertEqual(ASSESSMENT_SCORE_MEANINGS["A"], "Absent")
        self.assertEqual(assessment_effective_score(None, "A"), 0)

    def test_known_invalid_numeric_values_are_rejected(self):
        for raw in ("77", "87", "89"):
            with self.subTest(raw=raw):
                self.assertIsNone(parse_assessment_score(raw))

    def test_unknown_non_numeric_value_is_rejected(self):
        self.assertIsNone(parse_assessment_score("UNKNOWN"))

    def test_mixed_average_includes_absent_as_zero(self):
        rows = [
            {"numeric_score": 8, "score_code": None},
            {"numeric_score": None, "score_code": "A"},
            {"numeric_score": 7, "score_code": None},
        ]
        self.assertEqual(calculate_assessment_average(rows), 5.0)

    def test_all_absent_average_is_zero(self):
        rows = [{"numeric_score": None, "score_code": "A"} for _ in range(3)]
        self.assertEqual(calculate_assessment_average(rows), 0)

    def test_numeric_zero_remains_in_denominator(self):
        rows = [
            {"numeric_score": 0, "score_code": None},
            {"numeric_score": 5, "score_code": None},
            {"numeric_score": 10, "score_code": None},
        ]
        self.assertEqual(calculate_assessment_average(rows), 5.0)

    def test_unsupported_representation_is_not_assumed(self):
        with self.assertRaises(ValueError):
            assessment_effective_score(None, "X")
        with self.assertRaises(ValueError):
            assessment_effective_score(None, None)
        with self.assertRaises(ValueError):
            assessment_effective_score(5, "A")

    def test_blank_average_has_no_invented_rule(self):
        with self.assertRaises(ValueError):
            calculate_assessment_average([])

    def test_attendance_meanings_and_unresolved_n(self):
        self.assertEqual(
            ATTENDANCE_MEANINGS,
            {"P": "Present", "A": "Absent", "H": "Holiday", "NA": "Not Applicable"},
        )
        self.assertNotIn("N", ATTENDANCE_MEANINGS)


if __name__ == "__main__":
    unittest.main()
