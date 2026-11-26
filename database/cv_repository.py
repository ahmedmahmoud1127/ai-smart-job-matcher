"""SQL for stored CV analyses."""
import json
from typing import Optional

from database.db import get_connection
from database.session import resolve_user_id


def save_analysis(meta: dict, text: str, result: dict, user_id: int | None = None) -> int:
    user_id = resolve_user_id(user_id)
    with get_connection() as c:
        return c.execute(
            "INSERT INTO cv_analyses (user_id,file_name,file_type,file_size,source_link,extracted_text,target_role,score,skills_json,result_json)"
            " VALUES (?,?,?,?,?,?,?,?,?,?)",
            (user_id, meta["file_name"], meta.get("file_type", ""), meta.get("file_size", 0), meta.get("source_link", ""),
             text, result["role"], result["score"]["total"], json.dumps([s["name"] for s in result["skills"]]),
             json.dumps(result))).lastrowid


def update_analysis(analysis_id: int, result: dict, user_id: int | None = None) -> None:
    user_id = resolve_user_id(user_id)
    with get_connection() as c:
        c.execute("UPDATE cv_analyses SET target_role=?, score=?, skills_json=?, result_json=? WHERE id=? AND user_id=?",
                  (result["role"], result["score"]["total"], json.dumps([s["name"] for s in result["skills"]]),
                   json.dumps(result), analysis_id, user_id))


def get_analysis(analysis_id: int, user_id: int | None = None) -> Optional[dict]:
    user_id = resolve_user_id(user_id)
    with get_connection() as c:
        row = c.execute("SELECT * FROM cv_analyses WHERE id=? AND user_id=?", (analysis_id, user_id)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["result"] = json.loads(d.pop("result_json"))
    d["skills"] = json.loads(d.pop("skills_json"))
    return d


def list_analyses(user_id: int | None = None) -> list:
    user_id = resolve_user_id(user_id)
    with get_connection() as c:
        return [dict(r) for r in c.execute(
            "SELECT id,file_name,file_type,file_size,target_role,score,created_at FROM cv_analyses WHERE user_id=? ORDER BY id DESC",
            (user_id,))]


def delete_analysis(analysis_id: int, user_id: int | None = None) -> None:
    user_id = resolve_user_id(user_id)
    with get_connection() as c:
        c.execute("DELETE FROM cv_analyses WHERE id=? AND user_id=?", (analysis_id, user_id))
