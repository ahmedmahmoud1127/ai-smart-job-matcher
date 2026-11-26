"""SQL for Learning Roadmap: the latest generated roadmap per user and the skills marked as completed."""
import json
from typing import Optional

from database.db import get_connection
from database.session import resolve_user_id
from database.schema import ROADMAP_SCHEMA

_ready = False


def _ensure_tables() -> None:
    """Create the tables even if the app was started before this feature existed."""
    global _ready
    if not _ready:
        with get_connection() as c:
            c.executescript(ROADMAP_SCHEMA)
        _ready = True


def replace_roadmap(plan: dict, selected_skills: list, include_bonus: bool, user_id: int | None = None) -> int:
    """Store a new roadmap and remove the previous one (its progress is deleted by ON DELETE CASCADE)."""
    user_id = resolve_user_id(user_id)
    _ensure_tables()
    with get_connection() as c:
        c.execute("DELETE FROM learning_roadmaps WHERE user_id=?", (user_id,))
        return c.execute(
            "INSERT INTO learning_roadmaps (user_id, career, level, hours_per_day, include_bonus, selected_skills, plan_json)"
            " VALUES (?,?,?,?,?,?,?)",
            (user_id, plan["career"], plan["level"], plan["hours_per_day"], int(include_bonus),
             json.dumps(selected_skills), json.dumps(plan))).lastrowid


def get_latest(user_id: int | None = None) -> Optional[dict]:
    """The user's current roadmap: {'id', 'created_at', 'include_bonus', 'selected_skills', 'plan'} or None."""
    user_id = resolve_user_id(user_id)
    _ensure_tables()
    with get_connection() as c:
        row = c.execute("SELECT * FROM learning_roadmaps WHERE user_id=? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
    if not row:
        return None
    return {"id": row["id"], "created_at": row["created_at"], "include_bonus": bool(row["include_bonus"]),
            "selected_skills": json.loads(row["selected_skills"]), "plan": json.loads(row["plan_json"])}


def completed_skills(roadmap_id: int) -> set:
    _ensure_tables()
    with get_connection() as c:
        return {r["skill"] for r in c.execute("SELECT skill FROM roadmap_progress WHERE roadmap_id=?", (roadmap_id,))}


def set_completed(roadmap_id: int, skill: str, done: bool) -> None:
    _ensure_tables()
    with get_connection() as c:
        if done:
            c.execute("INSERT OR IGNORE INTO roadmap_progress (roadmap_id, skill) VALUES (?,?)", (roadmap_id, skill))
        else:
            c.execute("DELETE FROM roadmap_progress WHERE roadmap_id=? AND skill=?", (roadmap_id, skill))


def set_many_completed(roadmap_id: int, skills: list, done: bool) -> None:
    for s in skills:
        set_completed(roadmap_id, s, done)


def delete_roadmap(user_id: int | None = None) -> None:
    user_id = resolve_user_id(user_id)
    _ensure_tables()
    with get_connection() as c:
        c.execute("DELETE FROM learning_roadmaps WHERE user_id=?", (user_id,))
