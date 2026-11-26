"""CV Analyzer page."""
import streamlit as st

from components.cv.results import render_results
from components.cv.styles import inject_cv_styles
from components.cv.upload import render_history, render_upload_card
from components.icons import icon
from components.profile.styles import inject_profile_styles
from components.profile.widgets import show_flash
from database import cv_repository as cv_repo


def _init_state() -> None:
    st.session_state.setdefault("cv_uploader_key", 0)
    st.session_state.setdefault("cv_show_all", False)
    if "cv_current_id" not in st.session_state:  # reopen the latest saved analysis after a refresh
        rows = cv_repo.list_analyses()
        st.session_state.cv_current_id = rows[0]["id"] if rows else None


def render_cv_page() -> None:
    _init_state()
    inject_profile_styles()  # shared card/list/chip styles
    inject_cv_styles()
    show_flash()
    st.markdown('<div class="page-title">CV Analyzer</div><div class="page-sub">Upload your CV and let AI analyze it for you. '
                'Discover your skills, strengths, and get personalized insights.</div>', unsafe_allow_html=True)
    left, right = st.columns([1, 1.75])
    with left:
        render_upload_card()
        render_history()
    with right:
        row = cv_repo.get_analysis(st.session_state.cv_current_id) if st.session_state.cv_current_id else None
        if st.session_state.cv_current_id and row is None:
            st.session_state.cv_current_id = None
        if row:
            render_results(row)
        else:
            with st.container(key="card_cv_empty"):
                st.markdown(f'<div class="empty-big"><div class="ico">{icon("chart", 34)}</div><h3>No analysis yet</h3>'
                            '<div>Upload your CV and press <b>Analyze CV</b> to see your score, skills, strengths and recommendations.</div></div>',
                            unsafe_allow_html=True)
