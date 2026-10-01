#!/usr/bin/env python3
"""Regression test for the accepted Stage E sanitized-source snapshot."""
import os
import unittest
from pathlib import Path

from stage_e_common import expected_counts, parse_sources

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
        self.assertEqual(expected_counts(data), EXPECTED_COUNTS)
        totals = data.summary["_totals"]
        self.assertEqual(totals["failure_entries_total"], 9346)
        self.assertEqual(totals["assessment_duplicate_groups"], 50)
        self.assertEqual(totals["assessment_duplicate_members"], 100)
        self.assertEqual(totals["attendance_duplicate_groups"], 4)
        self.assertEqual(totals["attendance_duplicate_members"], 8)
        self.assertEqual(totals["invalid_score_values"], {"77.0": 1, "87.0": 1, "89.0": 1})
        self.assertEqual(totals["placeholder_activities"], 44)

if __name__ == "__main__":
    unittest.main()
