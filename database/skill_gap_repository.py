"""SQL for Skill Gap Analysis: the user's target career, level, study hours, skill edits and the last generated result."""
import json
from datetime import datetime
from typing import Optional

from database.db import get_connection
from database.session import resolve_user_id
from database.schema import SKILL_GAP_SCHEMA

_ready = False


def _ensure_table() -> None:
    """Create the table even if the app was started before this feature existed."""
    global _ready
    if not _ready:
        with get_connection() as c:
            c.executescript(SKILL_GAP_SCHEMA)
        _ready = True


def get_state(user_id: int | None = None) -> Optional[dict]:
    user_id = resolve_user_id(user_id)
    _ensure_table()
    with get_connection() as c:
        r = c.execute("SELECT * FROM skill_gap_state WHERE user_id=?", (user_id,)).fetchone()
    if not r:
        return None
    return {"career": r["career"], "level": r["level"], "hours_per_day": r["hours_per_day"], "focus": r["focus"],
            "added": json.loads(r["added_json"]), "removed": json.loads(r["removed_json"]),
            "result": json.loads(r["result_json"]) if r["result_json"] else None, "generated_at": r["generated_at"]}


def save_state(career: str, level: str, hours_per_day: float, focus: str, added: dict, removed: list,
               user_id: int | None = None) -> None:
    user_id = resolve_user_id(user_id)
    _ensure_table()
    with get_connection() as c:
        c.execute("INSERT INTO skill_gap_state (user_id,career,level,hours_per_day,focus,added_json,removed_json,updated_at) "
                  "VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET career=excluded.career, level=excluded.level, "
                  "hours_per_day=excluded.hours_per_day, focus=excluded.focus, added_json=excluded.added_json, "
                  "removed_json=excluded.removed_json, updated_at=excluded.updated_at",
                  (user_id, career, level, hours_per_day, focus, json.dumps(added), json.dumps(sorted(removed)),
                   datetime.now().isoformat(timespec="seconds")))


def save_result(result: dict, user_id: int | None = None) -> str:
    """Store the last generated analysis/roadmap (needs an existing state row). Returns the timestamp."""
    user_id = resolve_user_id(user_id)
    _ensure_table()
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as c:
        c.execute("UPDATE skill_gap_state SET result_json=?, generated_at=? WHERE user_id=?", (json.dumps(result), now, user_id))
    return now
