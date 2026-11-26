"""Global CSS. Streamlit stays in control; CSS only skins it."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root{--ink:#16233F;--muted:#6B7A99;--blue:#2F6FDE;--blue-soft:#E6EEFD;--lav:#ECE9FB;--cream:#FBF6EA;
--mint:#DDF3E8;--mint-ink:#1F7A52;--line:rgba(120,140,190,.16);
--glass:rgba(255,255,255,.62);--shadow:0 10px 30px rgba(70,95,160,.10);--shadow-hover:0 16px 38px rgba(70,95,160,.16);}
html,body,[class*="css"],.stApp{font-family:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif;color:var(--ink);}
.stApp{background:radial-gradient(1000px 520px at 8% -5%,#E4ECFC 0%,transparent 60%),
radial-gradient(900px 520px at 100% 0%,#EEEAFB 0%,transparent 55%),linear-gradient(180deg,#F6F8FD 0%,#FBF8F1 100%);}
[data-testid="stSidebar"],[data-testid="collapsedControl"],[data-testid="stSidebarCollapsedControl"],
[data-testid="stHeader"],[data-testid="stToolbar"],footer{display:none!important;}
.block-container{max-width:1320px;padding:1.1rem 1.6rem 2.5rem;}
[data-testid="stVerticalBlock"]{gap:.9rem;}

[class*="st-key-card_"],.st-key-navbar,.st-key-hero{background:var(--glass);backdrop-filter:blur(14px);
-webkit-backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,.85);border-radius:24px;box-shadow:var(--shadow);
transition:box-shadow .25s ease,transform .25s ease;}
[class*="st-key-card_"]{padding:1.2rem 1.35rem;}
[class*="st-key-card_"]:hover{box-shadow:var(--shadow-hover);transform:translateY(-2px);}
.st-key-navbar{padding:.55rem 1rem;border-radius:22px;}

.brand{display:flex;align-items:center;gap:.65rem;font-weight:700;font-size:1.02rem;white-space:nowrap;}
.brand-mark{width:38px;height:38px;border-radius:12px;background:linear-gradient(145deg,#2C3A63,#4A5C91);display:grid;place-items:center;color:#fff;box-shadow:0 6px 14px rgba(44,58,99,.3);}
.brand b{color:var(--blue);font-weight:800;}
.st-key-navbar button{border:none;background:transparent;color:var(--muted);font-weight:600;border-radius:999px;box-shadow:none;transition:background .2s,color .2s;}
.st-key-navbar button:hover{background:var(--blue-soft);color:var(--blue);}
.st-key-navbar button[data-testid="stBaseButton-primary"]{background:var(--blue-soft);color:var(--blue);}
.st-key-navbar button p{font-size:.9rem;white-space:nowrap;}
@media(max-width:1350px){.st-key-navbar button p{font-size:.78rem;}.brand span{font-size:.9rem;}}

.st-key-hero{position:relative;overflow:hidden;padding:2rem 2.4rem;min-height:230px;
background:linear-gradient(110deg,rgba(255,255,255,.85) 0%,rgba(236,242,254,.9) 55%,rgba(251,246,234,.9) 100%);}
.hero-chip{display:inline-block;background:var(--blue-soft);color:var(--blue);font-weight:600;font-size:.82rem;padding:.3rem .8rem;border-radius:999px;}
.hero-title{font-size:clamp(2rem,4vw,3.1rem);font-weight:800;letter-spacing:-.02em;margin:.7rem 0 .2rem;line-height:1.1;}
.hero-title span{color:var(--blue);}
.hero-sub{font-size:1.15rem;color:var(--muted);font-weight:500;margin-bottom:.4rem;}
.hero-art{position:absolute;right:1.5rem;bottom:0;width:min(46%,560px);height:100%;pointer-events:none;}
.st-key-hero button{background:#0F1B3A;color:#fff;border:none;border-radius:999px;padding:.55rem 1.4rem;font-weight:600;box-shadow:0 8px 18px rgba(15,27,58,.28);transition:transform .2s,box-shadow .2s;}
.st-key-hero button:hover{background:#1B2B57;color:#fff;transform:translateY(-2px);}
.st-key-hero button p{color:#fff;}
.st-key-hero [data-testid="stButton"]{position:relative;z-index:2;}
@media(max-width:900px){.hero-art{opacity:.25;width:70%}}

.stat{display:flex;align-items:center;gap:.9rem;position:relative;min-height:84px;}
.stat-icon{width:54px;height:54px;border-radius:16px;display:grid;place-items:center;flex:none;box-shadow:inset 0 1px 0 #fff,0 6px 14px rgba(70,95,160,.12);}
.tone-blue{background:#DCEAFD;color:#2F6FDE}.tone-mint{background:#D6F1E3;color:#1F9466}
.tone-cream{background:#FCEBCB;color:#D9921B}.tone-lav{background:#E5E1FA;color:#6A58D0}
.stat-label{font-size:.92rem;font-weight:600;display:flex;gap:.6rem;align-items:center;}
.stat-label .delta{font-size:.76rem;color:var(--mint-ink);font-weight:700;background:var(--mint);padding:.05rem .45rem;border-radius:999px;}
.stat-value{font-size:1.85rem;font-weight:800;letter-spacing:-.02em;line-height:1.15;}
.stat-sub{font-size:.76rem;color:var(--muted);}
.spark{position:absolute;right:0;bottom:0;width:42%;height:52px;opacity:.9;}

.sec-title{display:flex;align-items:center;gap:.6rem;font-weight:700;font-size:1.08rem;margin-bottom:.2rem;}
.sec-title svg{color:var(--blue);}

.metric-note{text-align:center;font-size:.82rem;color:var(--muted);}
.win{text-align:center;}
.win .trophy{color:#D9A21B;margin-bottom:.2rem;}
.win h4{margin:.1rem 0;font-size:1.1rem;font-weight:800;}
.tip{display:flex;gap:.7rem;align-items:center;background:var(--lav);border-radius:16px;padding:.7rem .9rem;font-size:.85rem;color:#3B4668;}
.tip svg{color:#7B6BD6;flex:none;}

.job{display:flex;align-items:center;gap:.9rem;}
.logo{width:50px;height:50px;border-radius:15px;background:#fff;display:grid;place-items:center;box-shadow:0 4px 12px rgba(70,95,160,.12);flex:none;font-weight:800;font-size:1.3rem;}
.job-title{font-weight:700;font-size:1.02rem;line-height:1.25;}
.job-meta{font-size:.84rem;color:var(--muted);}
.match{margin-left:auto;background:var(--mint);color:var(--mint-ink);font-weight:700;font-size:.85rem;padding:.35rem .8rem;border-radius:999px;white-space:nowrap;}
[class*="st-key-job_"] button{border-radius:999px;border:1px solid var(--line);background:#fff;font-weight:600;color:var(--blue);transition:all .2s;}
[class*="st-key-job_"] button:hover{background:var(--blue);color:#fff;border-color:var(--blue);}

.road{position:relative;padding-left:2.1rem;}
.road:before{content:"";position:absolute;left:.78rem;top:.9rem;bottom:.9rem;width:2px;background:linear-gradient(#2F6FDE,#C9D4EE);}
.step{position:relative;display:flex;flex-wrap:wrap;align-items:center;gap:.2rem .6rem;padding:.55rem .7rem;border-radius:14px;margin-bottom:.3rem;}
.step.active{background:var(--blue-soft);}
.dot{position:absolute;left:-2.1rem;top:1.1rem;width:20px;height:20px;border-radius:50%;background:#fff;border:2px solid #B8C5E4;display:grid;place-items:center;color:#fff;}
.dot.done{background:var(--blue);border-color:var(--blue);}
.dot.now{border-color:var(--blue);}
.step-name{font-weight:600;font-size:.95rem;flex:1;}
.pill{font-size:.78rem;font-weight:600;padding:.25rem .7rem;border-radius:999px;white-space:nowrap;}
.pill.done{background:var(--mint);color:var(--mint-ink)}.pill.now{background:#fff;color:var(--blue)}.pill.todo{background:#EDF0F6;color:#7B88A6}
.bar{height:5px;background:#DCE5F8;border-radius:99px;overflow:hidden;width:100%}
.bar i{display:block;height:100%;background:linear-gradient(90deg,#5E92EC,#2F6FDE);border-radius:99px;transition:width .5s;}

.skills{display:flex;flex-wrap:wrap;gap:.6rem;margin:.6rem 0 .2rem;}
.badge{display:inline-flex;align-items:center;gap:.5rem;background:#fff;border:1px solid var(--line);padding:.45rem .9rem;border-radius:999px;font-weight:600;font-size:.88rem;box-shadow:0 3px 8px rgba(70,95,160,.07);transition:transform .2s,box-shadow .2s;}
.badge:hover{transform:translateY(-2px);box-shadow:0 8px 16px rgba(70,95,160,.14);}
.badge i{width:9px;height:9px;border-radius:50%;display:inline-block;}
.badge.more{background:var(--lav);color:#5A4BB5;}

.st-key-card_quote{background:linear-gradient(110deg,rgba(255,255,255,.7),rgba(232,238,252,.9));overflow:hidden;position:relative;min-height:150px;}
.quote{font-size:1.2rem;font-style:italic;font-weight:500;line-height:1.5;max-width:60%;position:relative;z-index:1;}
.quote small{display:block;font-style:normal;color:var(--muted);font-size:.78rem;margin-top:.5rem;}
.quote-art{position:absolute;right:0;bottom:0;width:48%;height:100%;pointer-events:none;}

.stButton>button[data-testid="stBaseButton-secondary"]{border-radius:999px;font-weight:600;}
[class*="st-key-link_"] button{background:transparent;border:none;color:var(--blue);font-weight:600;padding:0;box-shadow:none;}
[class*="st-key-link_"] button:hover{background:transparent;color:#1B4FB0;}
.st-key-continue button{width:100%;background:var(--blue-soft);color:var(--blue);border:none;border-radius:16px;padding:.7rem;}
.st-key-continue button:hover{background:#D3E1FB;color:var(--blue);}
button:focus-visible{outline:2px solid var(--blue)!important;outline-offset:2px;}
@media(prefers-reduced-motion:reduce){*{transition:none!important;}}
</style>
"""


def inject_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
