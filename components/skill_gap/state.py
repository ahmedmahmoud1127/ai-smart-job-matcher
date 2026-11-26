"""Skill Gap state, calculations and button callbacks (all persistence goes through database/skill_gap_repository)."""
import streamlit as st

from components.navbar import go
from components.profile.widgets import flash
from data.roadmaps import LEVELS
from database import roadmap_repository as roadmap_repo
from database import skill_gap_repository as repo
from services import profile_data, skill_gap
from services.roadmap_generator import generate_roadmap

MAX_NAME = 40


def ensure_state() -> dict:
    state = repo.get_state()
    if state is None:
        target = profile_data.get_full_profile()["preferences"].get("effective_role")
        career = target if target in skill_gap.careers() else "Backend Developer"
        repo.save_state(career, "Intermediate", 2.0, "Balanced", {}, [])
        state = repo.get_state()
    if state["career"] not in skill_gap.careers():  # a career that no longer exists
        repo.save_state("Backend Developer", state["level"], state["hours_per_day"], state["focus"], state["added"], state["removed"])
        state = repo.get_state()
    return state


def compute(state: dict) -> tuple:
    """(skills used, analysis result) for the saved state - recalculated on every run, never hardcoded."""
    skills = skill_gap.effective_skills(skill_gap.collect_project_skills(), state["added"], state["removed"])
    return skills, skill_gap.analyze(state["career"], skills, state["level"], float(state["hours_per_day"]), state["focus"])


def _save(state: dict, **changes) -> None:
    new = {**state, **changes}
    repo.save_state(new["career"], new["level"], float(new["hours_per_day"]), new["focus"], new["added"], new["removed"])


# ------------------------------------------------------------------------------------------ callbacks
def add_skill() -> None:
    ss, state = st.session_state, ensure_state()
    raw = " ".join((ss.get("sg_new_name") or "").split())
    if not raw:
        flash("Type a skill name first.", "warning")
        return
    if len(raw) > MAX_NAME or not all(ch.isalnum() or ch in " +#.&/-_" for ch in raw):
        flash("Use a short skill name (letters, numbers and + # . & / - only).", "warning")
        return
    name, level = skill_gap.clean_skill_name(raw), ss.get("sg_new_level", state["level"])
    added = {k: v for k, v in state["added"].items() if k.lower() != name.lower()}
    added[name] = level
    _save(state, added=added, removed=[r for r in state["removed"] if r.lower() != name.lower()])
    flash(f"Added “{name}” ({level}). Your skill match was recalculated.")


def remove_skills(widget_key: str) -> None:
    picked, state = st.session_state.get(widget_key) or [], ensure_state()
    if not picked:
        return
    added = {k: v for k, v in state["added"].items() if k not in picked}
    removed = sorted(set(state["removed"]) | {p for p in picked if p not in state["added"]})
    _save(state, added=added, removed=removed)
    flash(f"Removed {len(picked)} skill(s) from this analysis. My Profile was not changed.")


def reset_skills() -> None:
    _save(ensure_state(), added={}, removed=[])
    flash("Skills reset to what My Profile and your CV contain.")


def save_focus() -> None:
    _save(ensure_state(), focus=st.session_state.sg_focus_pick)


def toggle_all_missing() -> None:
    st.session_state.sg_show_all = not st.session_state.get("sg_show_all", False)


def regenerate() -> None:
    """Recompute from the latest My Profile / CV data and store a snapshot of the roadmap in SQLite."""
    state = ensure_state()
    _, result = compute(state)
    repo.save_result(skill_gap.summary(result))
    flash(f"Roadmap regenerated: {result['match_pct']}% match, {result['need']} skill(s) to learn, about {result['total_duration']}.")


def start_learning_plan() -> None:
    """Hand the plan to the existing Learning Roadmap page without destroying a roadmap the user is already following."""
    state = ensure_state()
    skills, result = compute(state)
    repo.save_result(skill_gap.summary(result))
    catalog = skill_gap.catalog_skill_names(skills)
    prefill = {"rm_career": state["career"], "rm_level": state["level"], "rm_hours": float(state["hours_per_day"]),
               "rm_skills": catalog, "rm_bonus": True, "rm_extra": ""}
    latest = roadmap_repo.get_latest()
    if latest is None:
        plan = generate_roadmap(state["career"], state["level"], float(state["hours_per_day"]), catalog, include_bonus=True)
        roadmap_repo.replace_roadmap(plan, catalog, True)
        st.session_state.update(prefill)
        flash(f"Your {state['career']} learning plan is ready: {plan['missing_count']} skill(s), {plan['total_duration']}.")
    elif latest["plan"]["career"] == state["career"]:
        flash("Opening your current roadmap for this career. Your progress was kept.")
    else:
        st.session_state.update(prefill)
        flash(f"The roadmap form was filled for {state['career']}. Press “Regenerate Roadmap” to replace your current roadmap.", "warning")
    go("Learning Roadmap")
