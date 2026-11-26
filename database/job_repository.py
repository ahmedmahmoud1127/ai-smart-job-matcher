"""SQL for saved jobs (Smart Job Matching). Job details live in data/jobs_catalog.py; only the id is stored."""
from database.db import get_connection
from database.session import resolve_user_id
from database.schema import JOBS_SCHEMA

_ready = False


def _ensure_table() -> None:
    """Make sure the table exists even if the app was started before this feature was added."""
    global _ready
    if not _ready:
        with get_connection() as c:
            c.executescript(JOBS_SCHEMA)
        _ready = True


def list_saved(user_id: int | None = None) -> list:
    """Saved jobs, newest first: [{'job_id', 'saved_at'}]."""
    user_id = resolve_user_id(user_id)
    _ensure_table()
    with get_connection() as c:
        return [dict(r) for r in c.execute(
            "SELECT job_id, saved_at FROM saved_jobs WHERE user_id=? ORDER BY saved_at DESC, id DESC", (user_id,))]


def saved_ids(user_id: int | None = None) -> set:
    user_id = resolve_user_id(user_id)
    return {r["job_id"] for r in list_saved(user_id)}


def save_job(job_id: str, user_id: int | None = None) -> None:
    user_id = resolve_user_id(user_id)
    _ensure_table()
    with get_connection() as c:
        c.execute("INSERT OR IGNORE INTO saved_jobs (user_id, job_id) VALUES (?,?)", (user_id, job_id))


def unsave_job(job_id: str, user_id: int | None = None) -> None:
    user_id = resolve_user_id(user_id)
    _ensure_table()
    with get_connection() as c:
        c.execute("DELETE FROM saved_jobs WHERE user_id=? AND job_id=?", (user_id, job_id))


def toggle_saved(job_id: str, user_id: int | None = None) -> bool:
    """Flip the saved state and return the new state (True = now saved)."""
    user_id = resolve_user_id(user_id)
    if job_id in saved_ids(user_id):
        unsave_job(job_id, user_id)
        return False
    save_job(job_id, user_id)
    return True
