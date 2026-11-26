"""Profile completion score (weights from the product spec)."""
from database import repository as repo
from database.session import resolve_user_id

WEIGHTS = {"personal": 20, "education": 20, "skills": 20, "experience": 8, "projects": 7,
           "languages": 10, "preferences": 15}


def compute_completion(user_id: int | None = None) -> dict:
    user_id = resolve_user_id(user_id)
    user, prefs = repo.get_user(user_id), repo.get_preferences(user_id)
    n = {t: len(repo.list_rows(t, user_id)) for t in ("education", "skills", "work_experience", "projects", "languages")}
    personal_filled = sum(1 for f in repo.USER_FIELDS if str(user.get(f, "")).strip())
    pref_filled = sum(1 for k in ("target_role", "work_type", "employment_type", "industry") if prefs.get(k))
    earned = {
        "personal": WEIGHTS["personal"] * personal_filled / len(repo.USER_FIELDS),
        "education": WEIGHTS["education"] if n["education"] else 0,
        "skills": WEIGHTS["skills"] * min(n["skills"], 5) / 5,
        "experience": WEIGHTS["experience"] if n["work_experience"] else 0,
        "projects": WEIGHTS["projects"] if n["projects"] else 0,
        "languages": WEIGHTS["languages"] if n["languages"] else 0,
        "preferences": WEIGHTS["preferences"] * pref_filled / 4,
    }
    hints = {
        "personal": "Complete your personal information (phone, links, location).",
        "education": "Add your education.",
        "skills": "Add at least 5 technical skills.",
        "experience": "Add work, internship or volunteering experience.",
        "projects": "Add a project with a GitHub link.",
        "languages": "Add the languages you speak.",
        "preferences": "Set your career preferences.",
    }
    labels = {"personal": "Personal Information", "education": "Education", "skills": "Technical Skills",
              "experience": "Work Experience", "projects": "Projects", "languages": "Languages",
              "preferences": "Career Preferences"}
    sections = [{"key": k, "label": labels[k], "weight": WEIGHTS[k], "earned": round(earned[k], 1),
                 "complete": earned[k] >= WEIGHTS[k] - 0.01, "hint": hints[k]} for k in WEIGHTS]
    return {"total": round(sum(earned.values())), "sections": sections,
            "missing": [s for s in sections if not s["complete"]]}
