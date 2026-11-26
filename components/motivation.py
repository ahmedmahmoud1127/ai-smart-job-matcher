"""Motivational card with a minimal mountain illustration."""
import streamlit as st

ART = """<svg class="quote-art" viewBox="0 0 400 150" preserveAspectRatio="xMaxYMax meet" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="90" cy="60" rx="34" ry="10" fill="#fff" opacity=".8"/><ellipse cx="330" cy="40" rx="30" ry="9" fill="#fff" opacity=".8"/>
<path d="M0 150 90 70 150 110 240 20 330 100 360 80 400 120V150z" fill="#C5D2F2"/>
<path d="M120 150 240 20 330 150z" fill="#6F82C4"/><path d="M240 20 205 70 232 62 245 78 262 60 280 78z" fill="#fff" opacity=".9"/>
<path d="M240 20V0" stroke="#3A4A85" stroke-width="2"/><path d="M240 0h22l-6 6 6 6h-22z" fill="#3A4A85"/></svg>"""


def render_motivation() -> None:
    with st.container(key="card_quote"):
        st.markdown(f'{ART}<div class="quote">“Dream big, work hard, and let AI help you reach your goals.”'
                    '<small>— AI Smart Job Matcher</small></div>', unsafe_allow_html=True)
