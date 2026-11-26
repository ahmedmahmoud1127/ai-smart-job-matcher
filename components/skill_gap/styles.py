"""CSS for Skill Gap Analysis. Reuses the global tokens, glass cards and chips; adds ring legend, timeline and recommendations."""
import streamlit as st

CSS = """
<style>
.st-key-card_sg_header{position:relative;overflow:hidden;min-height:150px;padding-right:min(36%,420px);
background:linear-gradient(110deg,rgba(255,255,255,.85) 0%,rgba(236,242,254,.9) 55%,rgba(240,234,252,.9) 100%);}
.sg-art{position:absolute;right:1rem;bottom:0;height:100%;width:min(36%,420px);pointer-events:none;}
@media(max-width:900px){.st-key-card_sg_header{padding-right:1.35rem}.sg-art{opacity:.2;width:70%}}
.sg-label{font-size:.76rem;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.15rem;}
.sg-target{display:flex;align-items:center;gap:.8rem;flex-wrap:wrap;}
.sg-target .name{font-size:1.5rem;font-weight:800;letter-spacing:-.01em;}
.sg-pill{display:inline-block;font-size:.76rem;font-weight:700;padding:.25rem .75rem;border-radius:999px;background:var(--blue-soft);color:var(--blue);}
.sg-pill.lav{background:var(--lav);color:#5A4BB5}.sg-pill.mint{background:var(--mint);color:var(--mint-ink)}
.sg-chips{display:flex;flex-wrap:wrap;gap:.45rem;margin:.35rem 0 .2rem;}
.sg-chip{display:inline-flex;align-items:center;gap:.4rem;background:#fff;border:1px solid var(--line);padding:.3rem .8rem;border-radius:999px;
font-weight:600;font-size:.84rem;box-shadow:0 3px 8px rgba(70,95,160,.06);transition:transform .2s,box-shadow .2s;}
.sg-chip:hover{transform:translateY(-2px);box-shadow:0 8px 16px rgba(70,95,160,.14);}
.sg-chip small{color:var(--muted);font-weight:600;font-size:.7rem;}
.sg-chip.added{border-style:dashed;border-color:#8A79DB;}
.sg-chip.miss{background:#FDEEF2;border-color:#F6CAD6;color:#B23A5B;}
.sg-chip.part{background:#FFF4E2;border-color:#F4DDB8;color:#9A6414;}
.sg-chip.ok{background:var(--mint);border-color:#BFE6D0;color:var(--mint-ink);}
.sg-ring-legend{display:flex;flex-direction:column;gap:.9rem;}
.sg-leg{display:flex;align-items:center;gap:.8rem;}
.sg-dot{width:14px;height:14px;border-radius:50%;flex:none;}
.sg-dot.green{background:#3FB07F}.sg-dot.pink{background:#F28DA6}
.sg-leg b{font-size:1.6rem;line-height:1;letter-spacing:-.02em;}.sg-leg span{font-size:.86rem;color:var(--muted);font-weight:600;}
.sg-cov{margin-top:.5rem;}.sg-cov-row{display:flex;align-items:center;gap:.6rem;font-size:.78rem;font-weight:600;color:var(--muted);margin:.28rem 0;}
.sg-cov-row span{width:8.5rem;flex:none;}.sg-cov-row .bar{flex:1;}.sg-cov-row em{width:2.4rem;text-align:right;font-style:normal;color:var(--ink);}
.sg-miss-row{display:flex;align-items:center;gap:.6rem;padding:.4rem 0;border-bottom:1px solid var(--line);font-size:.9rem;font-weight:600;}
.sg-miss-row:last-child{border-bottom:none}.sg-miss-row .meta{margin-left:auto;font-size:.72rem;color:var(--muted);font-weight:600;white-space:nowrap;}
.sg-pri{width:9px;height:9px;border-radius:50%;flex:none;}.sg-pri.h{background:#E5668A}.sg-pri.m{background:#E5A23A}.sg-pri.l{background:#9AA6C0}
.sg-timeline{position:relative;}
.sg-stage{position:relative;display:flex;gap:1rem;padding-bottom:1.1rem;}
.sg-stage:not(:last-child):before{content:"";position:absolute;left:19px;top:42px;bottom:-2px;width:3px;border-radius:3px;background:linear-gradient(var(--c1),var(--c2));opacity:.55;}
.sg-node{width:40px;height:40px;border-radius:50%;flex:none;display:grid;place-items:center;font-weight:800;color:#fff;box-shadow:0 6px 14px rgba(70,95,160,.2);background:var(--c1);}
.sg-body{flex:1;background:rgba(255,255,255,.72);border:1px solid var(--line);border-left:4px solid var(--c1);border-radius:18px;padding:.8rem 1rem;transition:transform .2s,box-shadow .2s;}
.sg-body:hover{transform:translateY(-2px);box-shadow:0 10px 22px rgba(70,95,160,.13);}
.sg-stage.blue{--c1:#5E92EC;--c2:#8A79DB}.sg-stage.purple{--c1:#8A79DB;--c2:#E58BB0}.sg-stage.pink{--c1:#E58BB0;--c2:#E58BB0}
.sg-stage-head{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;}
.sg-stage-title{font-weight:800;font-size:1rem;flex:1;min-width:150px;}
.sg-dur{font-size:.76rem;font-weight:700;padding:.2rem .65rem;border-radius:999px;background:#fff;border:1px solid var(--line);color:var(--ink);white-space:nowrap;}
.sg-sub{font-size:.76rem;color:var(--muted);font-weight:600;margin:.1rem 0 .35rem;}
.sg-prog{display:flex;align-items:center;gap:.6rem;font-size:.76rem;font-weight:700;color:var(--muted);margin:.35rem 0;}.sg-prog .bar{flex:1;}
.sg-stage.blue .bar i{background:linear-gradient(90deg,#8DB3F2,#5E92EC)}.sg-stage.purple .bar i{background:linear-gradient(90deg,#B0A3EA,#8A79DB)}
.sg-stage.pink .bar i{background:linear-gradient(90deg,#F2B2CB,#E58BB0)}
.sg-chip.known{background:var(--mint);border-color:#BFE6D0;color:var(--mint-ink);opacity:.85;}
.sg-rec{display:flex;gap:.8rem;align-items:flex-start;padding:.7rem .2rem;border-bottom:1px solid var(--line);}
.sg-rec:last-of-type{border-bottom:none}.sg-rec .n{width:30px;height:30px;border-radius:10px;background:var(--lav);color:#5A4BB5;font-weight:800;display:grid;place-items:center;flex:none;}
.sg-rec b{display:block;font-size:.95rem;line-height:1.3;}.sg-rec span{font-size:.8rem;color:var(--muted);line-height:1.4;}
.st-key-sg_start button{width:100%;padding:.75rem 1rem;border:none;border-radius:16px;font-weight:700;font-size:1rem;color:#fff;
background:linear-gradient(120deg,#4C86EC,#7A6AE0);box-shadow:0 10px 22px rgba(76,134,236,.32);transition:transform .2s,box-shadow .2s;}
.st-key-sg_start button:hover{transform:translateY(-2px);box-shadow:0 14px 28px rgba(76,134,236,.4);color:#fff;}
.st-key-sg_start button p{color:#fff;font-size:1rem;}
[class*="st-key-card_sg_"] button[data-testid="stBaseButton-secondary"]{border:1px solid var(--line);background:#fff;font-weight:600;color:var(--blue);transition:all .2s;}
[class*="st-key-card_sg_"] button[data-testid="stBaseButton-secondary"]:hover{background:var(--blue);color:#fff;border-color:var(--blue);}
.sg-note{font-size:.76rem;color:var(--muted);margin-top:.4rem;line-height:1.5;}
@media(max-width:700px){.sg-cov-row span{width:6rem}}
</style>
"""


def inject_skill_gap_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
