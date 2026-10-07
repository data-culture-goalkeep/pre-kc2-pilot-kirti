#!/usr/bin/env python3
"""Stage E importer entry point with PM-confirmed assessment-code semantics."""
from __future__ import annotations

import import_stage_e_core as core
from stage_e_common import ASSESSMENT_SCORE_MEANINGS

_original_upsert = core.upsert

def _upsert_with_confirmed_score_meaning(cur, table, values, conflict, ret):
    if table == "assessment_score_codes":
        values = dict(values)
        code = values.get("score_code")
        if code in ASSESSMENT_SCORE_MEANINGS:
            values["meaning"] = ASSESSMENT_SCORE_MEANINGS[code]
    return _original_upsert(cur, table, values, conflict, ret)

core.upsert = _upsert_with_confirmed_score_meaning
apply_data = core.apply_data
main = core.main

if __name__ == "__main__":
    main()
