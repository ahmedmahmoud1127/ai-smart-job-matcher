"""Four statistic cards with decorative sparklines."""
import streamlit as st

from components.icons import icon
from data.sample_data import STATS

LINE = {"blue": "#5E92EC", "mint": "#3FB07F", "cream": "#EBB45A", "lav": "#8A79DB"}


def sparkline(values: list, color: str, uid: str) -> str:
    w, h, lo, hi = 200, 52, min(values), max(values)
    pts = [(i * w / (len(values) - 1), h - 6 - (v - lo) / ((hi - lo) or 1) * (h - 16)) for i, v in enumerate(values)]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<svg class="spark" viewBox="0 0 {w} {h}" preserveAspectRatio="none"><defs>'
            f'<linearGradient id="g{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{color}" stop-opacity=".28"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
            f'<path d="{line} L{w},{h} L0,{h} Z" fill="url(#g{uid})"/>'
            f'<path d="{line}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>')


def render_statistics() -> None:
    for col, s in zip(st.columns(4), STATS):
        with col.container(key=f"card_stat_{s['key']}"):
            st.markdown(
                f'<div class="stat"><div class="stat-icon tone-{s["tone"]}">{icon(s["icon"], 26)}</div>'
                f'<div><div class="stat-label">{s["label"]}<span class="delta">↑ {s["delta"]}</span></div>'
                f'<div class="stat-value">{s["value"]}</div><div class="stat-sub">{s["sub"]}</div></div>'
                f'{sparkline(s["trend"], LINE[s["tone"]], s["key"])}</div>', unsafe_allow_html=True)
