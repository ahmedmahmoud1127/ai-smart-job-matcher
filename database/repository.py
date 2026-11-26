"""All SQL lives here. UI code never writes SQL directly."""
import sqlite3
from typing import Any, Optional

from database.db import get_connection
from database.session import resolve_user_id

USER_FIELDS = ["full_name", "email", "phone", "country", "city", "linkedin", "github", "portfolio"]
TABLES = {  # whitelist: table -> (editable columns, ORDER BY)
    "education": (["university", "faculty", "major", "degree", "academic_year", "graduation_year", "gpa"],
                  "graduation_year DESC, id DESC"),
    "skills": (["name", "category", "level"], "id DESC"),
    "work_experience": (["job_title", "company", "employment_type", "start_date", "end_date", "description"],
                        "start_date DESC, id DESC"),
    "projects": (["name", "description", "technologies", "github_url", "demo_url"], "id DESC"),
    "languages": (["name", "level"], "id DESC"),
}
PREF_FIELDS = ["target_role", "target_role_other", "work_type", "employment_type", "industry", "industry_other"]


class DuplicateError(Exception):
    pass


def get_user(user_id: int | None = None) -> dict:
    user_id = resolve_user_id(user_id)
    with get_connection() as c:
        row = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else {}


def update_user(data: dict, user_id: int | None = None) -> None:
    user_id = resolve_user_id(user_id)
    cols = [f for f in USER_FIELDS if f in data]
    with get_connection() as c:
        c.execute(f"UPDATE users SET {', '.join(f'{k}=?' for k in cols)} WHERE id=?",
                  [data[k] for k in cols] + [user_id])


def list_rows(table: str, user_id: int | None = None) -> list:
    user_id = resolve_user_id(user_id)
    _, order = TABLES[table]
    with get_connection() as c:
        return [dict(r) for r in c.execute(f"SELECT * FROM {table} WHERE user_id=? ORDER BY {order}", (user_id,))]


def insert_row(table: str, data: dict, user_id: int | None = None) -> None:
    user_id = resolve_user_id(user_id)
    cols = TABLES[table][0]
    try:
        with get_connection() as c:
            c.execute(f"INSERT INTO {table} (user_id,{','.join(cols)}) VALUES (?{',?' * len(cols)})",
                      [user_id] + [data.get(k) for k in cols])
    except sqlite3.IntegrityError as e:
        raise DuplicateError(str(e)) from e


def update_row(table: str, row_id: int, data: dict, user_id: int | None = None) -> None:
    user_id = resolve_user_id(user_id)
    cols = [k for k in TABLES[table][0] if k in data]
    try:
        with get_connection() as c:
            c.execute(f"UPDATE {table} SET {', '.join(f'{k}=?' for k in cols)} WHERE id=? AND user_id=?",
                      [data[k] for k in cols] + [row_id, user_id])
    except sqlite3.IntegrityError as e:
        raise DuplicateError(str(e)) from e


def delete_row(table: str, row_id: int, user_id: int | None = None) -> None:
    user_id = resolve_user_id(user_id)
    assert table in TABLES
    with get_connection() as c:
        c.execute(f"DELETE FROM {table} WHERE id=? AND user_id=?", (row_id, user_id))


def get_preferences(user_id: int | None = None) -> dict:
    user_id = resolve_user_id(user_id)
    with get_connection() as c:
        row = c.execute("SELECT * FROM career_preferences WHERE user_id=?", (user_id,)).fetchone()
    return dict(row) if row else {k: "" for k in PREF_FIELDS}


def save_preferences(data: dict, user_id: int | None = None) -> None:
    user_id = resolve_user_id(user_id)
    vals = [data.get(k, "") for k in PREF_FIELDS]
    with get_connection() as c:
        c.execute(f"INSERT INTO career_preferences (user_id,{','.join(PREF_FIELDS)}) VALUES (?{',?' * len(PREF_FIELDS)}) "
                  f"ON CONFLICT(user_id) DO UPDATE SET {', '.join(f'{k}=excluded.{k}' for k in PREF_FIELDS)}",
                  [user_id] + vals)
