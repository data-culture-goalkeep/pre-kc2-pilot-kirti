# Import execution checkpoint — 2026-10-21

This is a partial staging import, not a production cutover.

Verified staging counts: 148 student profiles, 502 BMI monthly entries, 162 raw assessment score entries (18 I STD students), and 456 March 2026 daily attendance entries.

The I STD assessment data uses source workbook School Grade sheet 2025-2026, tab I STD, score columns B:J and source row coordinates. These scores are kept as raw text with resolution_status pending. Term and subject headings require complete cross-column validation before promotion.

March 2026 attendance source: first section of consolidated 2025-2026 workbook, with 120 matching student rows and 3720 candidate day status cells (P, A, H). Only 456 of these cells are staged at this checkpoint because the importer reached a tool execution limit. Do not reinsert completed source cells without a unique source-coordinate guard.

Existing 17 public tables and 188 original students are unchanged. Backup skipped at user request, but no destructive migration has occurred.

Before destructive cutover: finish attendance and all nine grade tabs, resolve missing staging names, reconcile source conflicts, and verify final counts and app query compatibility.
