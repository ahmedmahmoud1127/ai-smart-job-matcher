"""Extra CSS for the Analytics Dashboard. Reuses the global tokens, glass cards, bars, pills, badges and chips."""
import streamlit as st

CSS = """
<style>
.an-eyebrow{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;}
.an-range-note{font-size:.78rem;color:var(--muted);text-align:right;margin-top:.2rem;}
.st-key-an_range{align-items:flex-end;}
.st-key-an_range button,[class*="st-key-card_an_"] button[role="radio"]{border-radius:999px!important;font-weight:600;background:#fff;border:1px solid var(--line);color:var(--ink);}
.st-key-an_range button[aria-checked="true"],[class*="st-key-card_an_"] button[role="radio"][aria-checked="true"]{background:var(--blue)!important;
border-color:var(--blue)!important;color:#fff!important;box-shadow:0 6px 14px rgba(47,111,222,.28);}
.st-key-an_range button[aria-checked="true"] *,[class*="st-key-card_an_"] button[role="radio"][aria-checked="true"] *{color:#fff!important;}
.st-key-an_range button:hover,[class*="st-key-card_an_"] button[role="radio"]:hover{border-color:var(--blue);}
/* the profile styles also paint the active navbar button solid blue; keep the navbar look of the existing pages */
.st-key-navbar .stButton button[data-testid="stBaseButton-primary"]{background:var(--blue-soft)!important;color:var(--blue)!important;}

.an-stat-top{display:flex;justify-content:space-between;align-items:flex-start;gap:.6rem;}
.an-stat .stat-icon{width:46px;height:46px;border-radius:14px;}
.an-stat-label{font-size:.9rem;font-weight:600;margin-top:.6rem;}
.an-stat-value{font-size:2.05rem;font-weight:800;letter-spacing:-.02em;line-height:1.15;}
.an-stat-value small{font-size:1rem;font-weight:700;color:var(--muted);margin-left:.15rem;}
.an-stat-value.none{color:#B3BDD3;}
.an-stat .bar{margin:.55rem 0 .4rem;height:7px;}
.an-stat .bar.t-mint i{background:linear-gradient(90deg,#6FD1A6,#2E9C6D);}
.an-stat .bar.t-cream i{background:linear-gradient(90deg,#F4CC83,#D9921B);}
.an-stat .bar.t-lav i{background:linear-gradient(90deg,#A99BE8,#6A58D0);}
.an-stat-sub{font-size:.78rem;color:var(--muted);line-height:1.4;}
.an-delta{font-size:.74rem;font-weight:700;padding:.15rem .55rem;border-radius:999px;white-space:nowrap;}
.an-delta.up{background:var(--mint);color:var(--mint-ink);}
.an-delta.down{background:#FCEBCB;color:#9A6414;}
.an-delta.flat{background:#EDF0F6;color:#7B88A6;}
.an-delta i{font-style:normal;font-weight:500;opacity:.8;}

.an-tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:.6rem;margin:.5rem 0 .6rem;}
.an-tile{background:rgba(255,255,255,.72);border:1px solid var(--line);border-radius:16px;padding:.65rem .85rem;}
.an-tile span{display:block;font-size:.72rem;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.03em;}
.an-tile b{display:block;font-size:1.35rem;font-weight:800;letter-spacing:-.01em;line-height:1.25;}
.an-tile small{display:block;font-size:.74rem;color:var(--muted);}
.an-target{margin-bottom:.4rem;}
.an-target span{font-size:.72rem;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.04em;}
.an-target b{display:block;font-size:1.3rem;font-weight:800;letter-spacing:-.01em;}
.an-target small{color:var(--muted);font-size:.84rem;}

.an-row{margin-bottom:.8rem;}
.an-row-top{display:flex;justify-content:space-between;align-items:center;gap:.6rem;margin-bottom:.3rem;}
.an-row-name{font-weight:600;font-size:.9rem;overflow-wrap:anywhere;}
.an-row-meta{font-size:.76rem;color:var(--muted);margin-top:.25rem;}
.an-row .bar{height:7px;}
.an-list{display:flex;flex-direction:column;gap:.45rem;}
.an-li{display:flex;align-items:center;gap:.7rem;background:rgba(255,255,255,.72);border:1px solid var(--line);border-radius:14px;padding:.55rem .8rem;}
.an-li .ico{width:30px;height:30px;border-radius:10px;flex:none;display:grid;place-items:center;background:var(--mint);color:var(--mint-ink);}
.an-li .ico.todo{background:var(--blue-soft);color:var(--blue);}
.an-li .t{font-weight:600;font-size:.88rem;line-height:1.25;overflow-wrap:anywhere;}
.an-li .m{font-size:.75rem;color:var(--muted);}
.an-li .r{margin-left:auto;font-size:.76rem;font-weight:700;color:var(--blue);white-space:nowrap;}
.an-sub{font-size:.74rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin:.8rem 0 .4rem;}
.an-note{font-size:.78rem;color:var(--muted);margin-top:.3rem;line-height:1.45;}
.an-badges{display:flex;flex-wrap:wrap;gap:.4rem;margin:.2rem 0 .3rem;}
.an-badges .badge{padding:.22rem .7rem;font-size:.8rem;box-shadow:none;}
.an-badges .badge:hover{transform:none;box-shadow:none;}
.an-badges .badge small{font-weight:700;opacity:.7;}
.an-legend{display:flex;gap:1rem;flex-wrap:wrap;font-size:.76rem;color:var(--muted);margin-top:.2rem;}
.an-legend i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:.35rem;}

.an-ins{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:.8rem;margin-top:.4rem;}
.an-ins-item{display:flex;gap:.8rem;align-items:flex-start;background:rgba(255,255,255,.75);border:1px solid var(--line);border-radius:18px;
padding:.9rem 1rem;box-shadow:0 4px 12px rgba(70,95,160,.06);transition:transform .2s,box-shadow .2s;}
.an-ins-item:hover{transform:translateY(-2px);box-shadow:0 10px 22px rgba(70,95,160,.13);}
.an-ins-item .stat-icon{width:42px;height:42px;border-radius:13px;}
.an-ins-item b{display:block;font-size:.95rem;margin-bottom:.15rem;}
.an-ins-item p{margin:0;font-size:.86rem;line-height:1.5;color:#3B4668;}
.an-empty-btn{margin-top:.3rem;}
[class*="st-key-card_an_"] button[data-testid="stBaseButton-secondary"]{border:1px solid var(--line);background:#fff;font-weight:600;color:var(--blue);transition:all .2s;}
[class*="st-key-card_an_"] button[data-testid="stBaseButton-secondary"]:hover{background:var(--blue);color:#fff;border-color:var(--blue);}
[class*="st-key-card_an_"] [data-testid="stButtonGroup"] button{border-radius:999px;}
@media(max-width:700px){.an-tiles{grid-template-columns:repeat(2,1fr);}.an-range-note{text-align:left;}}
</style>
"""


def inject_analytics_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
