"""AI Smart Job Matcher – Main Dashboard. Run: streamlit run app.py"""
import copy

import streamlit as st

from components.career_readiness import render_career_readiness
from components.hero import render_hero
from components.learning_roadmap import render_learning_roadmap
from components.motivation import render_motivation
from components.analytics.page import render_analytics_page
from components.cv.page import render_cv_page
from components.jobs.page import render_jobs_page
from components.roadmap.page import render_roadmap_page
from components.skill_gap.page import render_skill_gap_page
from components.login.page import render_login_page
from components.navbar import go, render_navbar
from components.profile.page import render_profile_page
from components.recommended_jobs import render_recommended_jobs
from components.responsive import inject_responsive
from components.skills_overview import render_skills_overview
from components.statistics import render_statistics
from components.styles import inject_styles
from data.sample_data import ROADMAP
from database.auth_repository import init_auth
from database.db import init_db

st.set_page_config(page_title="AI Smart Job Matcher", page_icon="💼", layout="wide",
                   initial_sidebar_state="collapsed")

def init_state() -> None:
    st.session_state.setdefault("page", "Dashboard")
    st.session_state.setdefault("roadmap", copy.deepcopy(ROADMAP))
    st.session_state.setdefault("saved_jobs", set())
    st.session_state.setdefault("show_all_skills", False)

def dashboard() -> None:
    render_hero()
    render_statistics()
    c1, c2, c3 = st.columns([1, 1.1, 1])
    with c1:
        render_career_readiness()
    with c2:
        render_recommended_jobs()
    with c3:
        render_learning_roadmap()
    s1, s2 = st.columns([1, 1.15])
    with s1:
        render_skills_overview()
    with s2:
        render_motivation()

def coming_soon(page: str) -> None:
    with st.container(key="card_soon"):
        st.markdown(f"### {page}")
        st.write("This page is the next feature on the roadmap. Dashboard, My Profile, CV Analyzer, Jobs, Learning Roadmap, Skill Gap Analysis and Analytics are built so far.")
        st.button("Back to Dashboard", on_click=go, args=("Dashboard",))

@st.cache_resource
def _setup_database() -> bool:
    init_db()
    init_auth()
    return True

_setup_database()
init_state()
inject_styles()
if not st.session_state.get("authenticated"):
    render_login_page()  # the rest of the app is only shown after signing in
    inject_responsive()  # after the login CSS so the phone/tablet rules win
    st.stop()
render_navbar()
if message := st.session_state.pop("welcome_message", None):  # one-time greeting after a sign-up
    st.toast(message, icon="🎉")
page = st.session_state.page
if page == "Dashboard":
    dashboard()
elif page == "My Profile":
    render_profile_page()
elif page == "CV Analyzer":
    render_cv_page()
elif page == "Jobs":
    render_jobs_page()
elif page == "Learning Roadmap":
    render_roadmap_page()
elif page == "Skill Gap Analysis":
    render_skill_gap_page()
elif page == "Analytics":
    render_analytics_page()
else:
    coming_soon(page)
inject_responsive()  # last, so these overrides apply on every page
