"""Welcome hero with minimal vector illustration (no people)."""
from html import escape

import streamlit as st

from components.navbar import go
from database import repository as repo
from data.sample_data import USER

ART = """
<svg class="hero-art" viewBox="0 0 560 230" preserveAspectRatio="xMaxYMax meet" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="bag" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4A5C8F"/><stop offset="1" stop-color="#2A3560"/></linearGradient></defs>
<ellipse cx="300" cy="222" rx="270" ry="10" fill="#9DB3E6" opacity=".25"/>
<g transform="translate(10,40)"><path d="M62 38v-14a10 10 0 0 1 10-10h40a10 10 0 0 1 10 10v14" fill="none" stroke="#2A3560" stroke-width="9" stroke-linecap="round"/>
<rect x="10" y="36" width="160" height="130" rx="22" fill="url(#bag)"/><rect x="10" y="36" width="160" height="26" rx="13" fill="#fff" opacity=".09"/>
<rect x="78" y="80" width="26" height="26" rx="6" fill="#E8C98B"/><rect x="85" y="88" width="12" height="9" rx="2" fill="#B8925A"/></g>
<g transform="rotate(7 300 110)"><rect x="190" y="30" width="130" height="165" rx="10" fill="#fff"/><rect x="190" y="30" width="130" height="165" rx="10" fill="none" stroke="#DCE4F6"/>
<text x="258" y="62" font-family="Georgia,serif" font-style="italic" font-weight="700" font-size="26" fill="#3B4F8C">CV</text>
<circle cx="224" cy="95" r="13" fill="#C8D5F2"/><path d="M204 122a20 14 0 0 1 40 0z" fill="#C8D5F2"/>
<rect x="256" y="80" width="46" height="6" rx="3" fill="#DCE4F6"/><rect x="256" y="96" width="46" height="6" rx="3" fill="#DCE4F6"/>
<rect x="206" y="140" width="96" height="6" rx="3" fill="#DCE4F6"/><rect x="206" y="156" width="80" height="6" rx="3" fill="#DCE4F6"/><rect x="206" y="172" width="60" height="6" rx="3" fill="#7FA2EA"/></g>
<g transform="translate(345,40)"><path d="M55 120c-30-5-45-30-38-58 24 4 38 25 38 58z" fill="#6E9A6A"/><path d="M60 120c-6-35 8-62 40-72 8 30-8 62-40 72z" fill="#86AE7E"/><path d="M58 122c-2-30-2-55 10-82" stroke="#5B8656" stroke-width="2" fill="none"/>
<path d="M30 120h60l-8 62a8 8 0 0 1-8 7H46a8 8 0 0 1-8-7z" fill="#F4F1EA"/><ellipse cx="60" cy="120" rx="30" ry="6" fill="#E6E1D6"/></g>
<g transform="translate(455,60)"><circle cx="55" cy="75" r="62" fill="#4A5473"/><circle cx="55" cy="75" r="48" fill="#E9EDF7"/><circle cx="55" cy="75" r="34" fill="#6A7699"/><circle cx="55" cy="75" r="20" fill="#E9EDF7"/><circle cx="55" cy="75" r="9" fill="#3A4468"/>
<path d="M55 75 100 22" stroke="#3A4468" stroke-width="5" stroke-linecap="round"/><path d="M92 14l14-6-6 14-8-2z" fill="#3A4468"/></g>
</svg>"""


def render_hero() -> None:
    name = (repo.get_user().get("full_name") or USER["full_name"]).split()[0]
    name = escape(name)
    with st.container(key="hero"):
        st.markdown(
            f'{ART}<div class="hero-chip">Your Career Journey Starts Here ✦</div>'
            f'<div class="hero-title">Welcome Back, <span>{name}</span>!</div>'
            '<div class="hero-sub">Find the right job. Build the right skills.</div>',
            unsafe_allow_html=True)
        st.button("Explore Jobs", icon=":material/search:", key="explore_jobs", on_click=go, args=("Jobs",))
