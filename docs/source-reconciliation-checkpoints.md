# Final-source reconciliation checkpoints

Status: analysis only. No database modifications.

Student Profile Sheet: 148 non-empty unique student IDs, all 148 present in the existing 188-student database. Forty existing IDs are absent from the new profile: SCH-26-0001 to SCH-26-0040.

Historical record impact of those forty IDs: 51 grade enrolments; 182 assessments; 1,515 individual assessment scores; 114 attendance months; 2,453 attendance days; 89 measurements.

BMI 2026 tab, column D: 98 populated student-ID rows, 95 distinct IDs, 3 repeated occurrences. Every populated ID is part of the final 148-ID cohort. Repeated IDs must be inspected before they are classified as duplicates or valid multiple measurements.

Grade sheet first-column scan: LKG 24 student-ID occurrences (21 unique), UKG 6, I STD 18, II STD 13, III STD 15, IV STD 14, V STD 14, VI STD 0, VII STD 15. The VI STD result does not prove absence of students; their IDs could be in another column. Exact row and term layout must be verified for every tab.

Attendance: separate January, February, March and consolidated workbooks overlap in reporting dates. Some separate workbook rows have blank IDs. Do not map by name alone or treat blank days as absences.

Remaining steps: inspect each grade tab's actual ID column and term blocks, reconcile BMI repeats and missing IDs, map attendance periods and collisions, and prepare source-to-target validation counts. Verify recoverable backup before any deletion.

The existing database and current frontend remain unchanged.
