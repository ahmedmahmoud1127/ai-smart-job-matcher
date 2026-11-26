"""Extra CSS for Smart Job Matching. Reuses the global tokens, cards, chips and badges of the existing pages."""
import streamlit as st

CSS = """
<style>
.match.high{background:var(--mint);color:var(--mint-ink);}
.match.mid{background:var(--blue-soft);color:var(--blue);}
.match.low{background:#FCEBCB;color:#9A6414;}
.jm-chips{display:flex;flex-wrap:wrap;gap:.35rem;margin:.7rem 0 .1rem;}
.jm-chips .chip{margin:0;}
.jm-chips .chip.soft{background:var(--lav);color:#5A4BB5;}
.jm-bar-row{display:flex;align-items:center;gap:.7rem;margin:.6rem 0 .1rem;font-size:.8rem;font-weight:600;color:var(--muted);}
.jm-bar-row .bar{flex:1;}
.jm-label{font-size:.72rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin:.55rem 0 0;}
.jm-skills{display:flex;flex-wrap:wrap;gap:.4rem;margin:.3rem 0 0;}
.jm-skills .badge{padding:.2rem .7rem;font-size:.8rem;box-shadow:none;}
.jm-skills .badge:hover{transform:none;box-shadow:none;}
.jm-comp{margin-bottom:.8rem;}
.jm-comp.off{opacity:.6;}
.jm-comp .ov-bar-head{margin-bottom:.3rem;}
.jm-comp .item-meta{margin-top:.3rem;}
.jm-head{display:flex;align-items:center;gap:.9rem;margin-bottom:.4rem;}
.jm-head .logo{width:58px;height:58px;}
.jm-count{font-size:.86rem;color:var(--muted);font-weight:600;margin:.1rem 0 .2rem;}
.jm-learn-top{display:flex;justify-content:space-between;align-items:center;gap:.6rem;}
.jm-gain{background:var(--mint);color:var(--mint-ink);font-weight:700;font-size:.78rem;padding:.15rem .6rem;border-radius:999px;white-space:nowrap;}
.jm-hint{font-size:.86rem;line-height:1.5;margin-top:.35rem;}

[class*="st-key-card_jm_job_"]{gap:.45rem;}
[class*="st-key-card_jm_job_"] button[data-testid="stBaseButton-secondary"],
.st-key-card_jm_filters button[data-testid="stBaseButton-secondary"],[class*="st-key-item_jm_learn_"] button[data-testid="stBaseButton-secondary"]{
border:1px solid var(--line);background:#fff;font-weight:600;color:var(--blue);transition:all .2s;}
[class*="st-key-card_jm_job_"] button[data-testid="stBaseButton-secondary"]:hover,
.st-key-card_jm_filters button[data-testid="stBaseButton-secondary"]:hover,[class*="st-key-item_jm_learn_"] button[data-testid="stBaseButton-secondary"]:hover{
background:var(--blue);color:#fff;border-color:var(--blue);}
[class*="st-key-card_jm_job_"] button[data-testid="stBaseButton-primary"]{background:var(--blue);color:#fff;border:none;}
.st-key-jm_more button{width:100%;background:var(--blue-soft);color:var(--blue);border:none;border-radius:16px;padding:.7rem;font-weight:600;}
.st-key-jm_more button:hover{background:#D3E1FB;color:var(--blue);}
.st-key-card_jm_filters label p{font-size:.82rem;font-weight:600;color:var(--muted);}
[data-baseweb="tab-list"]{gap:.4rem;}
[data-baseweb="tab"]{border-radius:999px;font-weight:600;}
</style>
"""


def inject_jobs_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
