#!/usr/bin/env python3
"""Regression test for the accepted Stage E sanitized-source snapshot."""
import os
import unittest
from pathlib import Path

from stage_e_common import (
    ASSESSMENT_SCORE_MEANINGS,
    ATTENDANCE_MEANINGS,
    calculate_assessment_average,
    expected_counts,
    parse_sources,
)

EXPECTED_COUNTS = {
    "source_files": 11, "academic_years": 4, "grades": 10, "subjects": 8,
    "assessment_periods": 4, "assessment_score_codes": 1, "attendance_status_codes": 5,
    "students": 188, "student_grade_enrollments": 317, "grade_subjects": 64,
    "assessment_competencies": 312, "assessment_activities": 936,
    "student_assessments": 3453, "assessment_scores": 47387,
    "attendance_months": 1882, "attendance_days": 46763, "student_measurements": 1786,
}

class StageESourceSnapshotTest(unittest.TestCase):
    def test_accepted_source_snapshot(self):
        source_dir = os.environ.get("KC2_SOURCE_DIR")
        if not source_dir:
            self.skipTest("KC2_SOURCE_DIR not set")
        manifest = Path(__file__).with_name("source_manifest.json")
        data = parse_sources(Path(source_dir), manifest)
        actual_counts = expected_counts(data)
        self.assertEqual(actual_counts, EXPECTED_COUNTS)
        totals = data.summary["_totals"]
        self.assertEqual(totals["failure_entries_total"], 9346)
        self.assertEqual(totals["assessment_duplicate_groups"], 50)
        self.assertEqual(totals["assessment_duplicate_members"], 100)
        self.assertEqual(totals["attendance_duplicate_groups"], 4)
        self.assertEqual(totals["attendance_duplicate_members"], 8)
        self.assertEqual(sum(1 for row in data.assessments if row["duplicate_candidate"]), 100)
        self.assertEqual(sum(1 for row in data.attendance_months if row["duplicate_candidate"]), 8)
        self.assertEqual(totals["invalid_score_values"], {"77.0": 1, "87.0": 1, "89.0": 1})

        zero_scores = [s for s in data.scores if s["numeric_score"] == 0 and s["score_code"] is None]
        absent_scores = [s for s in data.scores if s["numeric_score"] is None and s["score_code"] == "A"]
        self.assertEqual(len(zero_scores), 1051)
        self.assertEqual(len(absent_scores), 52)
        self.assertTrue(all(s["raw_score_value"] == "0" for s in zero_scores))
        self.assertTrue(all(s["raw_score_value"] == "A" for s in absent_scores))
        self.assertTrue(all(all(k in s for k in ("source_label", "sheet", "row", "column")) for s in zero_scores + absent_scores))
        self.assertIn("A", data.score_codes)
        self.assertEqual(ASSESSMENT_SCORE_MEANINGS["A"], "Absent")
        self.assertEqual(calculate_assessment_average([
            {"numeric_score": 8, "score_code": None},
            {"numeric_score": None, "score_code": "A"},
            {"numeric_score": 7, "score_code": None},
        ]), 5.0)

        self.assertEqual(ATTENDANCE_MEANINGS, {"P": "Present", "A": "Absent", "H": "Holiday", "NA": "Not Applicable"})
        self.assertNotIn("N", ATTENDANCE_MEANINGS)
        self.assertEqual(data.summary["Students & Attendance"]["unresolved_grade_labels"], {})
        mapped_lkg = [e for e in data.enrollments if e["source_grade_label"] == "A. LKG"]
        mapped_ukg = [e for e in data.enrollments if e["source_grade_label"] == "B. UKG"]
        self.assertEqual(len(mapped_lkg), 35)
        self.assertEqual(len(mapped_ukg), 37)
        self.assertTrue(all(e["grade"] == "LKG" and e["source_grade_label"] == "A. LKG" for e in mapped_lkg))
        self.assertTrue(all(e["grade"] == "UKG" and e["source_grade_label"] == "B. UKG" for e in mapped_ukg))
        self.assertEqual(totals["placeholder_activities"], 44)

if __name__ == "__main__":
    unittest.main()
