"""Section 08 – Career preferences."""
import streamlit as st

from components.profile.widgets import flash, section_title
from database import repository as repo

ROLES = ["Backend Developer", "Frontend Developer", "Full Stack Developer", "Data Analyst",
         "Machine Learning Engineer", "Software Engineer", "Other"]
WORK = ["Remote", "On-site", "Hybrid"]
EMPLOYMENT = ["Full-time", "Part-time", "Internship", "Freelance"]
INDUSTRIES = ["Software Development", "Data Science", "Artificial Intelligence", "Cybersecurity", "Web Development", "Other"]


def _idx(options: list, value: str) -> int:
    return options.index(value) if value in options else 0


def render_preferences() -> None:
    p = repo.get_preferences()
    with st.container(key="card_prof_prefs"):
        section_title("target", "Career Preferences", "Tell us what you are aiming for.")
        with st.form("prefs_form"):
            c1, c2 = st.columns(2)
            role = c1.selectbox("Target Job Role", ROLES, index=_idx(ROLES, p["target_role"]))
            role_other = c2.text_input("If Other, specify role", value=p["target_role_other"])
            work = c1.selectbox("Preferred Work Type", WORK, index=_idx(WORK, p["work_type"]))
            emp = c2.selectbox("Preferred Employment Type", EMPLOYMENT, index=_idx(EMPLOYMENT, p["employment_type"]))
            ind = c1.selectbox("Preferred Industry", INDUSTRIES, index=_idx(INDUSTRIES, p["industry"]))
            ind_other = c2.text_input("If Other, specify industry", value=p["industry_other"])
            saved = st.form_submit_button("Save Preferences", type="primary")
        if not p["target_role"]:
            st.caption("Not saved yet. Choose your options and press Save Preferences.")
        if saved:
            errs = []
            if role == "Other" and not role_other.strip():
                errs.append("Please specify your target role.")
            if ind == "Other" and not ind_other.strip():
                errs.append("Please specify your preferred industry.")
            if errs:
                for e in errs:
                    st.error(e)
            else:
                repo.save_preferences(dict(
                    target_role=role, target_role_other=role_other.strip() if role == "Other" else "",
                    work_type=work, employment_type=emp, industry=ind,
                    industry_other=ind_other.strip() if ind == "Other" else ""))
                flash("Career preferences saved.")
                st.rerun()
