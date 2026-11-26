"""Responsive overrides so the app fits phones, tablets and laptops. Injected after the other styles."""
import streamlit as st

CSS = """
<style>
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{overflow-x:hidden!important;max-width:100vw;}
img,svg,video,canvas{max-width:100%;}
[data-testid="stDataFrame"],[data-testid="stTable"],[data-testid="stPlotlyChart"],[data-testid="stVegaLiteChart"]{max-width:100%;overflow-x:auto;}
[data-testid="stMarkdownContainer"]{overflow-wrap:anywhere;}

@media(max-width:1100px){
.block-container{padding:1rem 1rem 2rem!important;}
.hero-title{font-size:clamp(1.7rem,5vw,2.6rem)!important;}
}

@media(max-width:900px){
.lg-art{height:340px!important;overflow:hidden!important;margin:1rem auto 0!important;}
.lg-left h1.lg-headline{white-space:normal!important;}
.st-key-hero{padding:1.3rem 1.2rem!important;min-height:0!important;}
.quote{max-width:100%!important;}
.quote-art{opacity:.2;}
}

@media(max-width:700px){
.lg-art,.lg-bg .s4,.lg-bg .s5{display:none!important;}
.lg-left{min-height:0!important;}
.lg-left .lg-text{max-width:100%!important;}
.lg-left ul.lg-features{display:none!important;}
.lg-left .lg-sub{margin-bottom:.6rem!important;}
.lg-tagline{display:none!important;}
.st-key-login_card{padding:1.3rem 1rem 1.2rem!important;border-radius:26px!important;}
.st-key-login_card input{padding-left:3rem!important;}
.st-key-login_social button{min-height:54px!important;}
.lg-demo{overflow-wrap:anywhere;word-break:break-word;}
.lg-demo code{display:inline-block;max-width:100%;}
.block-container{padding:.8rem .75rem 2rem!important;}
[data-testid="stVerticalBlock"]{gap:.7rem!important;}
[class*="st-key-card_"]{padding:1rem!important;border-radius:20px!important;}
.hero-art,.spark{display:none!important;}
.hero-title{font-size:1.9rem!important;}
.hero-sub{font-size:1rem!important;}
.stat-value{font-size:1.5rem!important;}
.job{flex-wrap:wrap;}
.match{margin-left:0!important;}
/* navbar becomes one swipeable row */
.st-key-navbar [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;overflow-x:auto!important;gap:.4rem!important;-webkit-overflow-scrolling:touch;padding-bottom:.3rem;}
.st-key-navbar [data-testid="stColumn"],.st-key-navbar [data-testid="column"]{flex:0 0 auto!important;width:auto!important;min-width:max-content!important;}
.st-key-navbar button{white-space:nowrap;}
.st-key-navbar button p{font-size:.8rem!important;white-space:nowrap;}
/* keep small inline rows (checkboxes, button pairs) from squashing, let wide layouts stack */
h1{font-size:1.7rem!important;}h2{font-size:1.4rem!important;}h3{font-size:1.15rem!important;}
[data-testid="stTabs"] [role="tablist"]{overflow-x:auto;}
.stButton>button,[data-testid="stDownloadButton"]>button{max-width:100%;}
}
</style>
"""

def inject_responsive() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
