#!/usr/bin/env python3
"""Stage E importer entry point with PM-confirmed assessment-code semantics."""
from __future__ import annotations

from pathlib import Path
import types

from stage_e_common import ASSESSMENT_SCORE_MEANINGS

_core_path = Path(__file__).with_name("import_stage_e_core.txt")
_core = types.ModuleType("import_stage_e_core")
_core.__file__ = str(_core_path)
_core.__name__ = "import_stage_e_core"
exec(compile(_core_path.read_text(encoding="utf-8"), str(_core_path), "exec"), _core.__dict__)

_original_upsert = _core.upsert

def _upsert_with_confirmed_score_meaning(cur, table, values, conflict, ret):
    if table == "assessment_score_codes":
        values = dict(values)
        code = values.get("score_code")
        if code in ASSESSMENT_SCORE_MEANINGS:
            values["meaning"] = ASSESSMENT_SCORE_MEANINGS[code]
    return _original_upsert(cur, table, values, conflict, ret)

_core.upsert = _upsert_with_confirmed_score_meaning
apply_data = _core.apply_data
main = _core.main

if __name__ == "__main__":
    main()
