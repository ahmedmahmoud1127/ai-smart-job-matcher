"""Skill Gap Analysis page."""
import streamlit as st

from components.cv.styles import inject_cv_styles
from components.profile.styles import inject_profile_styles
from components.profile.widgets import show_flash
from components.skill_gap import sections
from components.skill_gap.state import compute, ensure_state
from components.skill_gap.styles import inject_skill_gap_styles


def render_skill_gap_page() -> None:
    inject_profile_styles()  # shared cards, chips, lists
    inject_cv_styles()       # shared mini stats, badges
    inject_skill_gap_styles()
    show_flash()
    state = ensure_state()
    skills, result = compute(state)
    sections.render_header()
    left, right = st.columns([1.45, 1])
    with left:
        sections.render_target_card(state, skills)
    with right:
        sections.render_overview(result)
    c1, c2, c3 = st.columns([1, 1.7, 1.05])
    with c1:
        sections.render_missing(result)
    with c2:
        sections.render_roadmap(result, state)
    with c3:
        sections.render_recommendations(result)
