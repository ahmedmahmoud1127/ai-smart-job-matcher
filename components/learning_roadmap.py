"""Learning roadmap timeline with working Continue Learning action."""
import streamlit as st

from components.icons import icon
from components.navbar import go


def _status(p: int) -> str:
    return "done" if p >= 100 else "now" if p > 0 else "todo"


def continue_learning() -> None:
    steps = st.session_state.roadmap
    for s in steps:
        if s["progress"] < 100:
            s["progress"] = min(100, s["progress"] + 15)
            break


def render_learning_roadmap() -> None:
    steps = st.session_state.roadmap
    active = next((i for i, s in enumerate(steps) if s["progress"] < 100), None)
    html = ""
    for i, s in enumerate(steps):
        st_, p = _status(s["progress"]), s["progress"]
        label = {"done": "Completed ✓", "now": f"In Progress · {p}%", "todo": "Not Started"}[st_]
        dot = icon("check", 12, "#fff", 3) if st_ == "done" else ""
        bar = f'<div class="bar"><i style="width:{p}%"></i></div>' if st_ == "now" else ""
        html += (f'<div class="step{" active" if i == active and st_ == "now" else ""}">'
                 f'<span class="dot {st_}">{dot}</span><span class="step-name">{s["title"]}</span>'
                 f'<span class="pill {st_}">{label}</span>{bar}</div>')
    with st.container(key="card_roadmap"):
        head, link = st.columns([3, 1], vertical_alignment="center")
        head.markdown(f'<div class="sec-title">{icon("cap", 22)}Your Learning Roadmap</div>', unsafe_allow_html=True)
        with link.container(key="link_plan"):
            st.button("View Plan", key="plan", on_click=go, args=("Learning Roadmap",))
        st.markdown(f'<div class="road">{html}</div>', unsafe_allow_html=True)
        with st.container(key="continue"):
            if active is None:
                st.success("Roadmap complete! 🎉")
            else:
                st.button("Continue Learning", icon=":material/menu_book:", key="cont", on_click=continue_learning)
