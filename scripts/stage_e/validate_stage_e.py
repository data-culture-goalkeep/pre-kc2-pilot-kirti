#!/usr/bin/env python3
"""Read-only Stage E validator entry point for the PM-confirmed rule set."""
from __future__ import annotations

import validate_stage_e_core as core

core.CHECK_SQL["assessment_validity"] = core.CHECK_SQL["assessment_validity"].replace("\\n", "\n")

CHECK_SQL = core.CHECK_SQL
main = core.main

if __name__ == "__main__":
    main()
