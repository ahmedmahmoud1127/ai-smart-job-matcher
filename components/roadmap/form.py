"""'Build Your Roadmap' form: career, experience level, study hours and current skills, plus the Generate action."""
import streamlit as st

from components.profile.widgets import flash, section_title
from data.roadmaps import LEVEL_HELP, LEVELS, STUDY_DAYS_PER_WEEK
from data.skills_catalog import SKILL_CATEGORY
from database import roadmap_repository as roadmap_repo
from services import profile_data
from services.job_matching import build_candidate
from services.roadmap_generator import careers, generate_roadmap, normalize_skills

SKILL_OPTIONS = sorted(SKILL_CATEGORY)


def _profile_skill_names() -> list:
    """Skills found in My Profile and the latest CV analysis (same source Smart Job Matching uses)."""
    return sorted(n for n in build_candidate()["skills"] if n in SKILL_CATEGORY)


def init_form_state(latest: dict) -> None:
    """Give every widget key a value. Streamlit drops widget state when the page is left, so this runs on every visit:
    the form comes back with the inputs of the saved roadmap, or with sensible defaults on the first visit."""
    ss = st.session_state
    if latest:
        plan = latest["plan"]
        defaults = {"rm_career": plan["career"], "rm_level": plan["level"], "rm_hours": float(plan["hours_per_day"]),
                    "rm_skills": [s for s in latest["selected_skills"] if s in SKILL_CATEGORY], "rm_bonus": latest["include_bonus"]}
    else:
        target = profile_data.get_full_profile()["preferences"].get("effective_role")
        defaults = {"rm_career": target if target in careers() else careers()[0], "rm_level": LEVELS[0], "rm_hours": 2.0,
                    "rm_skills": _profile_skill_names() if "rm_skills" not in ss else [], "rm_bonus": True}
    defaults.update({"rm_extra": "", "rm_carry": True})
    for key, value in defaults.items():
        ss.setdefault(key, value)


def _import_skills() -> None:
    names = _profile_skill_names()
    if not names:
        flash("No skills found yet. Add skills in My Profile or analyze your CV first.", "warning")
        return
    st.session_state.rm_skills = sorted(set(st.session_state.rm_skills) | set(names))
    flash(f"Imported {len(names)} skill(s) from My Profile and your CV analysis.")


def _generate() -> None:
    ss = st.session_state
    known, unknown = normalize_skills(ss.rm_skills, ss.rm_extra)
    latest = roadmap_repo.get_latest()
    carried = roadmap_repo.completed_skills(latest["id"]) if latest and ss.rm_carry else set()
    plan = generate_roadmap(ss.rm_career, ss.rm_level, float(ss.rm_hours), sorted(known), include_bonus=ss.rm_bonus,
                            extra_known=carried)
    selected = sorted(known | carried)
    roadmap_repo.replace_roadmap(plan, selected, ss.rm_bonus)
    ss.rm_skills, ss.rm_extra = selected, ""  # typed words are now part of the selection
    if plan["missing_count"]:
        flash(f"Roadmap ready for {plan['career']}: {plan['missing_count']} skill(s) to learn, {plan['total_duration']}.")
    else:
        flash(f"You already know every skill in this {plan['career']} roadmap. Try another career or turn on bonus skills.")
    if carried:
        flash(f"{len(carried)} skill(s) you completed earlier were counted as known.")
    if unknown:
        flash("Not recognised and ignored: " + ", ".join(unknown), "warning")


def render_form(has_roadmap: bool) -> None:
    with st.container(key="card_rm_form"):
        section_title("map", "Build Your Roadmap", "Choose a career, tell us what you know, and get a step-by-step study plan.")
        left, right = st.columns([1, 1.35], gap="large")
        with left:
            st.selectbox("Target career", careers(), key="rm_career")
            st.radio("Experience level", LEVELS, key="rm_level", horizontal=True)
            st.markdown(f'<div class="rm-hint">{LEVEL_HELP[st.session_state.rm_level]}</div>', unsafe_allow_html=True)
            st.slider("Study hours per day", 0.5, 10.0, step=0.5, key="rm_hours",
                      help=f"Time estimates assume {STUDY_DAYS_PER_WEEK} study days per week.")
            st.checkbox("Include bonus skills (nice to have)", key="rm_bonus")
        with right:
            st.multiselect("Skills you already know", SKILL_OPTIONS, key="rm_skills", placeholder="Search and pick your skills")
            st.text_input("Other skills (comma separated)", key="rm_extra", placeholder="e.g. js, reactjs, Git & GitHub")
            if has_roadmap:
                st.checkbox("Count skills I completed in my current roadmap as known", key="rm_carry")
            st.button("Import from My Profile & CV", icon=":material/download:", key="rm_import", on_click=_import_skills)
        st.button("Regenerate Roadmap" if has_roadmap else "Generate Roadmap", icon=":material/auto_awesome:", key="rm_generate",
                  type="primary", on_click=_generate)
        st.markdown('<div class="disclaimer">The roadmap is built with Python rules from predefined career roadmaps: it compares '
                    'your skills with the career\'s required skills and estimates time from standard study hours. '
                    'No AI model or external service is used.</div>', unsafe_allow_html=True)
