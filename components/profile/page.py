"""My Profile page: assembles all sections."""
import streamlit as st

from components.profile.overview import render_overview
from components.profile.personal_info import render_personal_info
from components.profile.preferences import render_preferences
from components.profile.sections import (render_education, render_experience, render_languages,
                                         render_projects, render_skills)
from components.profile.styles import inject_profile_styles
from components.profile.widgets import show_flash


def render_profile_page() -> None:
    inject_profile_styles()
    show_flash()
    st.markdown('<div class="page-title">My Profile</div>'
                '<div class="page-sub">Manage your personal information, skills, and career preferences.</div>',
                unsafe_allow_html=True)
    render_overview()
    render_personal_info()
    render_education()
    render_skills()
    render_experience()
    render_projects()
    left, right = st.columns([1, 1.4])
    with left:
        render_languages()
    with right:
        render_preferences()
