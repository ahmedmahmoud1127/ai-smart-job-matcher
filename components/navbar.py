"""Top navigation bar (no sidebar)."""
import streamlit as st

from components.icons import icon
from components.login.page import sign_out
from data.sample_data import NOTIFICATIONS, USER
from database import repository as repo

PAGES = [
    ("Dashboard", ":material/home:"),
    ("My Profile", ":material/person:"),
    ("CV Analyzer", ":material/description:"),
    ("Jobs", ":material/search:"),
    ("Learning Roadmap", ":material/school:"),
    ("Skill Gap Analysis", ":material/insights:"),
    ("Analytics", ":material/bar_chart:"),
]


def go(page: str) -> None:
    st.session_state.page = page


def render_navbar() -> None:
    full_name = repo.get_user().get("full_name") or USER["full_name"]
    with st.container(key="navbar"):
        cols = st.columns([1.9, 1.1, 1.1, 1.3, 0.8, 1.65, 1.9, 1.1, 0.42, 1.45], vertical_alignment="center")
        cols[0].markdown(
            f'<div class="brand"><div class="brand-mark">{icon("briefcase", 20, "#fff")}</div>'
            '<span><b>AI</b> Smart Job Matcher</span></div>', unsafe_allow_html=True)
        for col, (name, ico) in zip(cols[1:8], PAGES):
            col.button(name, icon=ico, key=f"nav_{name}", on_click=go, args=(name,),
                       type="primary" if st.session_state.page == name else "secondary",
                       use_container_width=True)
        with cols[8].popover("", icon=":material/notifications:", use_container_width=True):
            st.markdown("**Notifications**")
            for n in NOTIFICATIONS:
                st.markdown(f"- {n}")
        with cols[9].popover(full_name, icon=":material/account_circle:", use_container_width=True):
            st.markdown(f"**{full_name}**")
            st.button("Open My Profile", key="profile_open", on_click=go, args=("My Profile",))
            st.button("Back to Dashboard", key="profile_home", on_click=go, args=("Dashboard",))
            st.button("Sign Out", key="profile_signout", icon=":material/logout:", on_click=sign_out)
