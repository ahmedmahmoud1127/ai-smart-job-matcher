"""Learning Roadmap page: build the roadmap, then follow and track it."""
import streamlit as st

from components.cv.styles import inject_cv_styles
from components.profile.styles import inject_profile_styles
from components.profile.widgets import show_flash
from components.roadmap.form import init_form_state, render_form
from components.roadmap.styles import inject_roadmap_styles
from components.roadmap.view import render_progress_card, render_skill_cards, render_stages, render_stats
from database import roadmap_repository as roadmap_repo
from services.roadmap_generator import progress_summary


def render_roadmap_page() -> None:
    inject_profile_styles()  # shared card / tile / chip styles
    inject_cv_styles()       # shared badges, mini stats, tips
    inject_roadmap_styles()
    show_flash()
    st.markdown('<div class="page-title">Learning Roadmap</div><div class="page-sub">A personalised study plan that shows what to learn, '
                'in which order, for how long and from which resources.</div>', unsafe_allow_html=True)

    latest = roadmap_repo.get_latest()
    init_form_state(latest)
    render_form(has_roadmap=latest is not None)
    if latest is None:
        with st.container(key="card_rm_empty"):
            st.markdown('<div class="empty-big"><div class="ico">🗺️</div><h3>No roadmap yet</h3>'
                        '<div>Pick a career, add your current skills and press <b>Generate Roadmap</b>.</div></div>', unsafe_allow_html=True)
        return

    rid, plan = latest["id"], latest["plan"]
    completed = roadmap_repo.completed_skills(rid)
    prog = progress_summary(plan, completed)
    render_stats(plan, prog)
    left, right = st.columns([1, 1.45])
    with left:
        render_progress_card(rid, plan, prog)
    with right:
        render_skill_cards(plan, completed)
    render_stages(rid, plan, prog, completed)
