"""Compare CV data with My Profile and apply user-confirmed updates (never automatic)."""
from data.skills_catalog import SKILL_CATEGORY
from database import repository as repo
from services.skills_extractor import canonical_names

CATEGORY_MAP = {"Programming Languages": "Programming Language", "Web Development": "Web Development",
                "Data Science": "Data & AI", "Databases": "Database", "Tools & Technologies": "Tools & DevOps",
                "Soft Skills": "Other"}
CONTACT_FIELDS = {"phone": "Phone Number", "linkedin": "LinkedIn Profile", "github": "GitHub Profile"}


def compare_skills(cv_skill_names: list) -> dict:
    profile_names = set()
    for row in repo.list_rows("skills"):
        profile_names |= canonical_names(row["name"]) or {row["name"]}
    cv = set(cv_skill_names)
    return {"in_both": sorted(cv & profile_names), "cv_only": sorted(cv - profile_names),
            "profile_only": sorted(profile_names - cv)}


def contact_suggestions(cv_contact: dict) -> dict:
    """Only fields that are empty in the profile and present in the CV."""
    user = repo.get_user()
    return {k: v for k, v in cv_contact.items() if k in CONTACT_FIELDS and v and not str(user.get(k, "")).strip()}


def apply_updates(skill_names: list, contact_fields: dict, level: str = "Intermediate") -> dict:
    """Add confirmed skills / fill empty contact fields. Existing data is never overwritten."""
    added = skipped = 0
    for name in skill_names:
        try:
            repo.insert_row("skills", {"name": name, "level": level,
                                       "category": CATEGORY_MAP.get(SKILL_CATEGORY.get(name, ""), "Other")})
            added += 1
        except repo.DuplicateError:
            skipped += 1
    user, fields = repo.get_user(), {}
    for k, v in contact_fields.items():
        if k in CONTACT_FIELDS and not str(user.get(k, "")).strip():
            fields[k] = v
    if fields:
        repo.update_user(fields)
    return {"skills_added": added, "skills_skipped": skipped, "fields_updated": list(fields)}
