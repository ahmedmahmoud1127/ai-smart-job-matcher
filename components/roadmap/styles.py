"""Extra CSS for the Learning Roadmap page. Reuses the global tokens, glass cards, item tiles, pills, chips and badges."""
import streamlit as st

CSS = """
<style>
.rm-stage-head{display:flex;align-items:center;gap:.9rem;flex-wrap:wrap;}
.rm-stage-title{flex:1;min-width:200px;}
.rm-num{width:42px;height:42px;border-radius:14px;flex:none;display:grid;place-items:center;font-weight:800;color:#fff;
background:linear-gradient(135deg,#7FA2EA,#2F6FDE);box-shadow:0 6px 14px rgba(47,111,222,.25);}
.rm-num.done,.rm-num.covered{background:linear-gradient(135deg,#6FD1A6,#2E9C6D);box-shadow:0 6px 14px rgba(46,156,109,.25);}
.rm-num.todo{background:linear-gradient(135deg,#B9C6E6,#8EA0CB);box-shadow:none;}
.rm-chips{display:flex;gap:.35rem;flex-wrap:wrap;align-items:center;}
.rm-chips .chip{margin:0;}.rm-chips .chip.soft{background:var(--lav);color:#5A4BB5;}
.rm-stage-bar{display:flex;align-items:center;gap:.7rem;margin:.7rem 0 .2rem;font-size:.8rem;font-weight:600;color:var(--muted);}
.rm-stage-bar .bar{flex:1;}
.rm-skill-meta{display:flex;gap:.35rem;flex-wrap:wrap;margin:.05rem 0 0 1.75rem;}
.rm-skill-meta .chip{margin:0;font-size:.72rem;}
.rm-skill-meta .chip.core{background:var(--blue-soft);color:var(--blue);}
.rm-skill-meta .chip.bonus{background:var(--lav);color:#5A4BB5;}
.rm-res-list{display:flex;flex-direction:column;gap:.35rem;}
.rm-res-title{font-size:.72rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-bottom:.1rem;}
.rm-res{display:flex;flex-direction:column;gap:.05rem;padding:.4rem .7rem;border-radius:12px;background:#fff;border:1px solid var(--line);
text-decoration:none!important;color:var(--ink)!important;font-weight:600;font-size:.84rem;line-height:1.3;transition:transform .2s,box-shadow .2s,border-color .2s;}
a.rm-res:hover{transform:translateY(-1px);border-color:rgba(47,111,222,.35);box-shadow:0 6px 14px rgba(70,95,160,.12);}
.rm-res span{font-size:.72rem;font-weight:500;color:var(--muted);}
.rm-res.plain{background:rgba(236,233,251,.55);border-style:dashed;font-weight:500;}
.rm-timeline{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:.5rem;margin-top:.5rem;}
.rm-timeline div{background:rgba(255,255,255,.7);border:1px solid var(--line);border-radius:14px;padding:.5rem .7rem;font-size:.8rem;}
.rm-timeline b{display:block;font-size:.9rem;}
.mini .v.sm{font-size:1.05rem;line-height:1.25;}
.mini .s{font-size:.74rem;color:var(--muted);}
.rm-next{display:flex;gap:.6rem;align-items:center;background:var(--blue-soft);border-radius:16px;padding:.7rem .9rem;font-size:.86rem;color:#24407A;}
.rm-next svg{color:var(--blue);flex:none;}
.rm-hint{font-size:.82rem;color:var(--muted);margin-top:-.2rem;}
.rm-actions{margin-top:.5rem;}
.st-key-card_rm_form label p{font-size:.84rem;font-weight:600;color:var(--muted);}
[class*="st-key-card_rm_"] button[data-testid="stBaseButton-secondary"],[class*="st-key-item_rm_"] button[data-testid="stBaseButton-secondary"]{
border:1px solid var(--line);background:#fff;font-weight:600;color:var(--blue);transition:all .2s;}
[class*="st-key-card_rm_"] button[data-testid="stBaseButton-secondary"]:hover,[class*="st-key-item_rm_"] button[data-testid="stBaseButton-secondary"]:hover{
background:var(--blue);color:#fff;border-color:var(--blue);}
[class*="st-key-item_rm_skill_"] [data-testid="stCheckbox"] label p{font-weight:700;font-size:.98rem;}
[class*="st-key-item_rm_skill_"]{padding:.8rem 1rem;}
</style>
"""


def inject_roadmap_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
