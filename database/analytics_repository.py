"""SQL for the Analytics Dashboard. Everything except `analytics_snapshots` is read-only access to existing tables."""
from typing import Optional

from database.db import get_connection
from database.session import resolve_user_id
from database.schema import ANALYTICS_SCHEMA

_ready = False
SNAPSHOT_FIELDS = ["readiness", "avg_match", "best_match", "strong_matches", "top5_avg", "jobs_analyzed",
                   "skills_count", "cv_score", "roadmap_pct"]


def _ensure_table() -> None:
    """Create the table even if the app was started before this feature existed."""
    global _ready
    if not _ready:
        with get_connection() as c:
            c.executescript(ANALYTICS_SCHEMA)
        _ready = True


def completed_events(roadmap_id: int) -> list:
    """Skills ticked off in a roadmap, oldest first: [{'skill', 'completed_at'}] (timestamps are UTC)."""
    with get_connection() as c:
        return [dict(r) for r in c.execute(
            "SELECT skill, completed_at FROM roadmap_progress WHERE roadmap_id=? ORDER BY completed_at, id", (roadmap_id,))]


def list_snapshots(user_id: int | None = None) -> list:
    """One row per day the dashboard was opened, oldest first."""
    user_id = resolve_user_id(user_id)
    _ensure_table()
    with get_connection() as c:
        return [dict(r) for r in c.execute(
            "SELECT snap_date, " + ", ".join(SNAPSHOT_FIELDS) + " FROM analytics_snapshots WHERE user_id=? ORDER BY snap_date",
            (user_id,))]


def save_snapshot(snap_date: str, values: dict, user_id: int | None = None) -> None:
    """Insert or update today's snapshot (a later visit on the same day replaces the earlier one)."""
    user_id = resolve_user_id(user_id)
    _ensure_table()
    cols = ", ".join(SNAPSHOT_FIELDS)
    marks = ", ".join("?" for _ in SNAPSHOT_FIELDS)
    updates = ", ".join(f"{f}=excluded.{f}" for f in SNAPSHOT_FIELDS)
    with get_connection() as c:
        c.execute(f"INSERT INTO analytics_snapshots (user_id, snap_date, {cols}) VALUES (?, ?, {marks}) "
                  f"ON CONFLICT(user_id, snap_date) DO UPDATE SET {updates}",
                  [user_id, snap_date] + [values.get(f) for f in SNAPSHOT_FIELDS])
