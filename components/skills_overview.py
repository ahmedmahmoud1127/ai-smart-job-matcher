"""Skill badges with View All toggle."""
import streamlit as st

from components.icons import icon
from data.sample_data import SKILLS, VISIBLE_SKILLS


def _toggle() -> None:
    st.session_state.show_all_skills = not st.session_state.show_all_skills


def render_skills_overview() -> None:
    show_all = st.session_state.show_all_skills
    shown = SKILLS if show_all else SKILLS[:VISIBLE_SKILLS]
    badges = "".join(f'<span class="badge"><i style="background:{s["color"]}"></i>{s["name"]}</span>' for s in shown)
    if not show_all:
        badges += f'<span class="badge more">+ {len(SKILLS) - VISIBLE_SKILLS} More</span>'
    with st.container(key="card_skills"):
        head, link = st.columns([3, 1], vertical_alignment="center")
        head.markdown(f'<div class="sec-title">{icon("layers", 22)}Your Skills Overview</div>', unsafe_allow_html=True)
        with link.container(key="link_skills"):
            st.button("Show less" if show_all else "View All", key="skills_all", on_click=_toggle)
        st.markdown(f'<div class="skills">{badges}</div>', unsafe_allow_html=True)
