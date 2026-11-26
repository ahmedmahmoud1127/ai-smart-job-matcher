"""Read-only access layer for future AI features (CV Analyzer, Job Matching, Skill Gap,
Learning Roadmap, Recommendations). Import from here instead of touching SQL."""
import pandas as pd

from database import repository as repo
from database.session import resolve_user_id


def get_full_profile(user_id: int | None = None) -> dict:
    """Whole profile as one plain dict (JSON-serialisable)."""
    user_id = resolve_user_id(user_id)
    prefs = repo.get_preferences(user_id)
    prefs["effective_role"] = (prefs.get("target_role_other") if prefs.get("target_role") == "Other"
                               else prefs.get("target_role")) or ""
    prefs["effective_industry"] = (prefs.get("industry_other") if prefs.get("industry") == "Other"
                                   else prefs.get("industry")) or ""
    return {"user": repo.get_user(user_id), "education": repo.list_rows("education", user_id),
            "skills": repo.list_rows("skills", user_id), "experience": repo.list_rows("work_experience", user_id),
            "projects": repo.list_rows("projects", user_id), "languages": repo.list_rows("languages", user_id),
            "preferences": prefs}


def get_skills_df(user_id: int | None = None) -> pd.DataFrame:
    user_id = resolve_user_id(user_id)
    return pd.DataFrame(repo.list_rows("skills", user_id), columns=["id", "user_id", "name", "category", "level"])


def get_skill_names(user_id: int | None = None) -> list:
    user_id = resolve_user_id(user_id)
    return [s["name"] for s in repo.list_rows("skills", user_id)]
