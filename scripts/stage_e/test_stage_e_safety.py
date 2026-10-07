#!/usr/bin/env python3
"""Focused importer, validator, and migration safety tests."""
import re
import unittest
from pathlib import Path

from import_stage_e import assessment_score_code_values
from stage_e_common import GRADE_LABEL_MAP
from validate_stage_e import CHECK_SQL


ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "supabase" / "migrations" / "20261005150500_apply_pm_phase1_corrections.sql"


class StageESafetyTest(unittest.TestCase):
    def test_importer_directly_writes_a_as_absent(self):
        values = assessment_score_code_values(
            "A",
            {"source_label": "LKG", "sheet": "Dropdown-Range", "row": 13},
            lambda r: {
                "source_file_id": 1,
                "source_sheet_name": r["sheet"],
                "source_row_number": r["row"],
            },
        )
        self.assertEqual(values["score_code"], "A")
        self.assertEqual(values["meaning"], "Absent")

    def test_unknown_assessment_code_is_rejected_by_validator(self):
        sql = CHECK_SQL["assessment_validity"]
        self.assertIn("score_code is not null and score_code<>'A'", sql)

    def test_grade_normalization_map_is_exact(self):
        self.assertEqual(GRADE_LABEL_MAP["A. LKG"], "LKG")
        self.assertEqual(GRADE_LABEL_MAP["B. UKG"], "UKG")

    def test_migration_preserves_source_grade_label(self):
        sql = MIGRATION.read_text(encoding="utf-8")
        self.assertIn("e.source_grade_label = 'A. LKG'", sql)
        self.assertIn("e.source_grade_label = 'B. UKG'", sql)
        self.assertNotRegex(sql.lower(), r"set\s+source_grade_label\s*=")

    def test_migration_is_non_destructive_to_assessment_scores(self):
        sql = MIGRATION.read_text(encoding="utf-8")
        lowered = sql.lower()
        self.assertNotRegex(lowered, r"\bdelete\b")
        self.assertNotRegex(lowered, r"\btruncate\b")
        self.assertNotRegex(lowered, r"\bdrop\b")
        self.assertNotRegex(lowered, r"update\s+public\.assessment_scores\b")

    def test_attendance_update_only_changes_lookup_meanings(self):
        sql = MIGRATION.read_text(encoding="utf-8")
        self.assertIn("update public.attendance_status_codes", sql)
        self.assertIn("when 'P' then 'Present'", sql)
        self.assertIn("when 'A' then 'Absent'", sql)
        self.assertIn("when 'H' then 'Holiday'", sql)
        self.assertIn("when 'NA' then 'Not Applicable'", sql)
        self.assertNotRegex(sql.lower(), r"update\s+public\.attendance_days\b")
        self.assertNotRegex(sql.lower(), r"delete\s+from\s+public\.attendance_days\b")


if __name__ == "__main__":
    unittest.main()
