"""Analytics Dashboard page: career progress, skills, learning activity, roadmap, job matching, CV and insights."""
import streamlit as st

from components.analytics import sections
from components.analytics.styles import inject_analytics_styles
from components.cv.styles import inject_cv_styles
from components.profile.styles import inject_profile_styles
from components.profile.widgets import show_flash
from services import analytics
from services.analytics import DEFAULT_WINDOW


def render_analytics_page() -> None:
    inject_profile_styles()  # shared page title, empty states, chips
    inject_cv_styles()       # shared badges and mini stats
    inject_analytics_styles()
    show_flash()
    st.session_state.setdefault("an_window", DEFAULT_WINDOW)
    st.session_state.setdefault("an_skill_view", "All")

    raw = analytics.load_raw()                       # reads the database and stores today's snapshot
    window = sections.render_header(raw["first_name"])
    data = analytics.build_dashboard(raw, window)    # pure calculation for the selected date range

    sections.render_cards(data)
    left, right = st.columns([1, 1.45])
    with left:
        sections.render_career(data)
        sections.render_recent(data)
    with right:
        sections.render_skills(data)
    sections.render_learning(data)
    left, right = st.columns(2)
    with left:
        sections.render_roadmap(data)
    with right:
        sections.render_cv(data)
    sections.render_jobs(data)
    sections.render_insights(data)
