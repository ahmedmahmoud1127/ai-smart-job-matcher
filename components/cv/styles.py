"""CSS for the CV Analyzer page (reuses global design tokens)."""
import streamlit as st

CSS = """
<style>
.st-key-cv_uploader [data-testid="stFileUploaderDropzone"]{border:2px dashed rgba(47,111,222,.35);background:rgba(230,238,253,.45);
border-radius:20px;padding:1.6rem 1rem;transition:background .2s,border-color .2s;}
.st-key-cv_uploader [data-testid="stFileUploaderDropzone"]:hover{background:rgba(230,238,253,.8);border-color:var(--blue);}
.st-key-cv_uploader [data-testid="stFileUploaderDropzone"] button{border-radius:999px;font-weight:600;}
.st-key-cv_uploader [data-testid="stFileUploaderFile"]{display:none;}
.file-card{display:flex;align-items:center;gap:.8rem;background:#fff;border:1px solid var(--line);border-radius:16px;padding:.7rem .9rem;}
.file-ico{width:42px;height:42px;border-radius:12px;background:var(--blue-soft);color:var(--blue);display:grid;place-items:center;flex:none;font-weight:800;font-size:.72rem;}
.file-name{font-weight:700;font-size:.92rem;overflow-wrap:anywhere;}.file-size{color:var(--muted);font-size:.8rem;}
.protip{display:flex;gap:.7rem;align-items:flex-start;background:var(--cream);border-radius:16px;padding:.8rem .9rem;font-size:.86rem;color:#5B5238;}
.protip svg{color:#D9921B;flex:none;}
.empty-big{text-align:center;padding:3rem 1rem;color:var(--muted);}
.empty-big .ico{width:72px;height:72px;margin:0 auto .8rem;border-radius:22px;background:var(--lav);color:#6A58D0;display:grid;place-items:center;}
.empty-big h3{color:var(--ink);margin:.2rem 0;font-size:1.15rem;}
.disclaimer{font-size:.76rem;color:var(--muted);margin-top:.4rem;}
.score-label{font-size:1.5rem;font-weight:800;letter-spacing:-.01em;}
.mini{display:flex;align-items:center;gap:.7rem;}
.mini .stat-icon{width:44px;height:44px;border-radius:14px;}
.mini .v{font-size:1.5rem;font-weight:800;line-height:1.1;}.mini .l{font-size:.78rem;color:var(--muted);font-weight:600;}
.cat{font-size:.76rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin:.7rem 0 .1rem;}
.fb{list-style:none;padding:0;margin:.3rem 0 0;}
.fb li{display:flex;gap:.55rem;align-items:flex-start;padding:.4rem 0;font-size:.9rem;line-height:1.45;}
.fb li:before{content:"";flex:none;width:8px;height:8px;border-radius:50%;margin-top:.5rem;background:#3FB07F;}
.fb.warn li:before{background:#E5A23A;}
.fb.rec{counter-reset:r;}.fb.rec li:before{counter-increment:r;content:counter(r);width:22px;height:22px;border-radius:50%;margin-top:.1rem;
background:var(--blue-soft);color:var(--blue);font-size:.74rem;font-weight:700;display:grid;place-items:center;}
.badge.miss{background:#FDF1E1;border-color:#F4DDB8;color:#9A6414;}.badge.ok{background:var(--mint);border-color:#BFE6D0;color:var(--mint-ink);}
.badge.sug{background:var(--lav);color:#5A4BB5;}
.struct{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:.5rem;}
.struct div{display:flex;gap:.5rem;align-items:center;font-size:.88rem;padding:.45rem .7rem;border-radius:12px;background:rgba(255,255,255,.7);border:1px solid var(--line);}
.struct .y{color:var(--mint-ink);font-weight:800;}.struct .n{color:#C0792B;font-weight:800;}
.hist-row{display:flex;justify-content:space-between;gap:.6rem;align-items:center;}
.hist-score{font-weight:800;color:var(--blue);}
.section-gap{height:.2rem;}
</style>
"""


def inject_cv_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
