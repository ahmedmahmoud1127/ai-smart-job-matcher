"""Extra CSS for My Profile. Reuses the global tokens from components/styles.py."""
import streamlit as st

CSS = """
<style>
.page-title{font-size:clamp(1.7rem,3vw,2.3rem);font-weight:800;letter-spacing:-.02em;margin-top:.4rem;}
.page-sub{color:var(--muted);font-size:1.02rem;margin-top:-.4rem;}
.sec-sub{color:var(--muted);font-size:.84rem;margin:-.1rem 0 .3rem 2rem;}
.ov{display:flex;gap:1rem;align-items:center;margin-bottom:.8rem;}
.avatar{width:84px;height:84px;border-radius:50%;flex:none;display:grid;place-items:center;font-size:2.1rem;font-weight:800;
color:#2F6FDE;background:linear-gradient(145deg,#DCE7FB,#E7E1FA);border:3px solid #fff;box-shadow:0 8px 20px rgba(70,95,160,.18);}
.ov-name{font-size:1.4rem;font-weight:800;letter-spacing:-.01em;}
.ov-line{color:var(--muted);font-size:.9rem;overflow-wrap:anywhere;}
.ov-bar-head{display:flex;justify-content:space-between;font-size:.85rem;font-weight:600;margin-bottom:.35rem;}
.ov-bar{margin-bottom:.8rem;}
.miss{display:flex;justify-content:space-between;gap:.8rem;align-items:center;background:var(--lav);border-radius:12px;padding:.5rem .75rem;margin-bottom:.4rem;font-size:.84rem;}
.miss b{color:#5A4BB5;white-space:nowrap;}
.kv-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:.7rem 1.2rem;margin-top:.4rem;}
.kv span{display:block;font-size:.76rem;color:var(--muted);font-weight:600;}
.kv b{font-size:.93rem;font-weight:600;overflow-wrap:anywhere;}
.empty{background:rgba(236,233,251,.55);border:1px dashed rgba(106,88,208,.3);border-radius:16px;padding:1rem;color:#5A4BB5;font-size:.9rem;text-align:center;}

[class*="st-key-item_"]{background:rgba(255,255,255,.75);border:1px solid var(--line);border-radius:18px;padding:.9rem 1rem;
box-shadow:0 4px 12px rgba(70,95,160,.06);transition:transform .2s,box-shadow .2s;gap:.5rem;}
[class*="st-key-item_"]:hover{transform:translateY(-2px);box-shadow:0 10px 22px rgba(70,95,160,.13);}
.item-title{font-weight:700;font-size:1rem;}
.item-meta{color:var(--muted);font-size:.86rem;margin-top:.1rem;}
.item-desc{font-size:.88rem;margin-top:.35rem;line-height:1.5;}
.chip{display:inline-block;background:var(--blue-soft);color:var(--blue);font-size:.74rem;font-weight:600;padding:.12rem .6rem;border-radius:999px;margin:.15rem .25rem .15rem 0;}
.chips{margin-top:.4rem;}
.links{margin-top:.4rem;font-size:.85rem;font-weight:600;}
.links a{color:var(--blue);text-decoration:none;margin-right:.8rem;}
.links a:hover{text-decoration:underline;}
.dots{display:inline-flex;gap:5px;}
.dots i{width:22px;height:6px;border-radius:99px;background:#DCE5F8;display:inline-block;}
.dots i.on{background:#7FA2EA;}
.lvl-intermediate .dots i.on{background:#5E92EC;}.lvl-advanced .dots i.on{background:#2F6FDE;}
.lvl-expert .dots i.on,.lvl-native .dots i.on{background:#6A58D0;}
.lvl{margin-top:.5rem;}

[data-baseweb="input"],[data-baseweb="select"]>div,[data-baseweb="textarea"]{border-radius:12px!important;}
[data-testid="stForm"]{border:1px solid var(--line);border-radius:18px;background:rgba(255,255,255,.55);padding:1rem;}
.stButton button[kind="primary"],[data-testid="stFormSubmitButton"] button[kind="primary"]{background:var(--blue);border:none;border-radius:999px;font-weight:600;}
[data-testid="stFormSubmitButton"] button{border-radius:999px;font-weight:600;}
@media(max-width:700px){.ov{flex-direction:column;align-items:flex-start;}}
</style>
"""


def inject_profile_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
