"""CSS for the login page (glassmorphism, soft purple/blue/white). Injected only while the user is signed out."""
from urllib.parse import quote

import streamlit as st


def _uri(svg: str) -> str:
    return "url(\"data:image/svg+xml;utf8," + quote(svg, safe="/:=,;()' ") + "\")"


_STROKE = "fill='none' stroke='#6B77A8' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'"
ICON_MAIL = _uri(f"<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' {_STROKE}>"
                 "<rect x='3' y='5' width='18' height='14' rx='2.5'/><path d='m3.5 7 8.5 6.5L20.5 7'/></svg>")
ICON_LOCK = _uri(f"<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' {_STROKE}>"
                 "<rect x='4.5' y='10.5' width='15' height='10' rx='2.5'/><path d='M8 10.5V8a4 4 0 0 1 8 0v2.5'/>"
                 "<circle cx='12' cy='15.5' r='1.3' fill='#6B77A8'/></svg>")
ICON_USER = _uri(f"<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' {_STROKE}>"
                 "<circle cx='12' cy='8' r='4'/><path d='M4.5 20.5c.8-3.6 3.9-5.5 7.5-5.5s6.7 1.9 7.5 5.5'/></svg>")
ICON_GOOGLE = _uri("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'>"
                   "<path fill='#FFC107' d='M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z'/>"
                   "<path fill='#FF3D00' d='M6.306 14.691l6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z'/>"
                   "<path fill='#4CAF50' d='M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238A11.91 11.91 0 0 1 24 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z'/>"
                   "<path fill='#1976D2' d='M43.611 20.083H42V20H24v8h11.303a12.04 12.04 0 0 1-4.087 5.571l.003-.002 6.19 5.238C36.971 39.205 44 34 44 24c0-1.341-.138-2.65-.389-3.917z'/></svg>")
ICON_GITHUB = _uri("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path fill='#14161F' d='M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12'/></svg>")
ICON_LINKEDIN = _uri("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='#0A66C2'><rect x='2' y='8.5' width='4.2' height='12.5' rx='.8'/>"
                     "<circle cx='4.1' cy='4.3' r='2.3'/><path d='M9.3 8.5h4v1.8c.6-1.1 2-2.1 4-2.1 4 0 4.7 2.6 4.7 6V21h-4.2v-5.9c0-1.4 0-3.1-1.9-3.1s-2.2 1.5-2.2 3V21H9.3z'/></svg>")
SWOOSH = _uri("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 16' preserveAspectRatio='none'><defs>"
              "<linearGradient id='g' x1='0' x2='1'><stop offset='0' stop-color='#7C3AED'/><stop offset='1' stop-color='#7C3AED' stop-opacity='0'/></linearGradient></defs>"
              "<path d='M4 11C60 2 170 1 296 8' fill='none' stroke='url(#g)' stroke-width='4' stroke-linecap='round'/></svg>")

CSS = """
<style>
:root{--lg-ink:#14183F;--lg-muted:#5B6490;--lg-purple:#7C3AED;--lg-violet:#5B3FD6;--lg-blue:#3B82F6;}
.stApp{background:radial-gradient(900px 600px at 0% 0%,#E7E1FF 0%,transparent 60%),radial-gradient(900px 700px at 100% 100%,#D6E6FF 0%,transparent 60%),
linear-gradient(135deg,#EFEBFF 0%,#E3E8FF 48%,#DCEBFF 100%)!important;}
.block-container{max-width:1620px!important;padding:2rem 3rem 2rem!important;position:relative;z-index:1;}
[data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] .lg-bg){height:0;margin:0;overflow:visible;}

/* ---------- floating background shapes ---------- */
.lg-bg{position:fixed;inset:0;z-index:0;overflow:hidden;pointer-events:none;}
.lg-bg span{position:absolute;display:block;border-radius:50%;filter:blur(2px);animation:lgDrift 18s ease-in-out infinite;}
.lg-bg .s1{width:460px;height:460px;left:-120px;top:-120px;background:radial-gradient(circle at 30% 30%,rgba(167,139,250,.55),rgba(167,139,250,0) 70%);}
.lg-bg .s2{width:520px;height:520px;right:-160px;top:12%;background:radial-gradient(circle at 40% 40%,rgba(96,165,250,.5),rgba(96,165,250,0) 70%);animation-duration:22s;animation-delay:-6s;}
.lg-bg .s3{width:380px;height:380px;left:30%;bottom:-160px;background:radial-gradient(circle at 50% 50%,rgba(196,181,253,.55),rgba(196,181,253,0) 70%);animation-duration:20s;animation-delay:-3s;}
.lg-bg .s4{width:84px;height:84px;left:49%;top:5%;border-radius:28px;background:linear-gradient(135deg,rgba(255,255,255,.7),rgba(255,255,255,.15));border:1px solid rgba(255,255,255,.8);transform:rotate(18deg);animation-name:lgDriftSq;animation-duration:16s;filter:none;}
.lg-bg .s5{width:56px;height:56px;right:8%;bottom:14%;border-radius:18px;background:linear-gradient(135deg,rgba(255,255,255,.65),rgba(255,255,255,.1));border:1px solid rgba(255,255,255,.8);animation-name:lgDriftSq;animation-duration:19s;animation-delay:-8s;filter:none;}
.lg-bg .s6{width:26px;height:26px;left:8%;bottom:30%;background:rgba(139,92,246,.35);animation-duration:14s;}
@keyframes lgDrift{0%,100%{transform:translate3d(0,0,0) scale(1)}50%{transform:translate3d(26px,-30px,0) scale(1.06)}}
@keyframes lgDriftSq{0%,100%{transform:translate3d(0,0,0) rotate(18deg)}50%{transform:translate3d(-18px,22px,0) rotate(30deg)}}

/* ---------- left: branding ---------- */
.lg-left{position:relative;min-height:calc(100vh - 4.5rem);display:flex;flex-direction:column;}
.lg-text{position:relative;z-index:2;max-width:56%;}
.lg-brand{display:flex;align-items:center;gap:.75rem;margin-bottom:2.6rem;}
.lg-brand .lg-name{font-size:1.75rem;font-weight:800;line-height:1.05;letter-spacing:-.02em;color:var(--lg-ink);}
.lg-brand .lg-name b{display:block;color:#4F46E5;font-weight:800;}
.lg-left h1.lg-headline{font-size:clamp(2.1rem,3.75vw,4.2rem)!important;white-space:nowrap;font-weight:800;line-height:1.04!important;letter-spacing:-.035em;margin:0!important;color:var(--lg-ink);padding:0!important;}
.lg-left h1.lg-headline span{display:inline-block;position:relative;background:linear-gradient(90deg,#7C3AED 0%,#3B82F6 100%);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent;padding-bottom:.35em;}
.lg-left h1.lg-headline span:after{content:"";position:absolute;left:0;bottom:.12em;width:62%;height:.2em;background:__SWOOSH__ no-repeat left center/100% 100%;}
.lg-left .lg-sub{font-size:clamp(1rem,1.35vw,1.3rem);line-height:1.55;color:var(--lg-muted);font-weight:500;max-width:30rem;margin:.4rem 0 1.9rem;}
.lg-left ul.lg-features{list-style:none;margin:0!important;padding:0!important;display:flex;flex-direction:column;gap:.85rem;}
.lg-left ul.lg-features li{display:flex;align-items:center;gap:.9rem;font-weight:600;color:#2A3158;font-size:1.02rem;padding-bottom:.85rem;border-bottom:1px solid rgba(124,134,190,.18);max-width:22rem;}
.lg-left ul.lg-features li:last-child{border-bottom:none;}
.lg-left ul.lg-features i{width:46px;height:46px;border-radius:15px;display:grid;place-items:center;flex:none;font-style:normal;
background:linear-gradient(145deg,rgba(255,255,255,.95),rgba(226,230,255,.7));border:1px solid rgba(255,255,255,.95);box-shadow:0 8px 20px rgba(99,102,241,.16);transition:transform .25s ease,box-shadow .25s ease;}
.lg-left ul.lg-features li:hover i{transform:translateY(-2px) scale(1.05);box-shadow:0 12px 26px rgba(99,102,241,.24);}
.lg-art{position:absolute;right:0;bottom:-.5rem;width:100%;height:calc(100% + .5rem);z-index:1;pointer-events:none;overflow:visible;}
.lg-robot{animation:lgFloat 5.5s ease-in-out infinite;}
.lg-float2{animation:lgFloatS 7s ease-in-out infinite;animation-delay:-2s;}
.lg-float3{animation:lgFloatS 8s ease-in-out infinite;animation-delay:-4s;}
.lg-eyes{animation:lgGlowPulse 3.6s ease-in-out infinite;}
.lg-spark path,.lg-spark circle{animation:lgTwinkle 3.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center;}
.lg-spark2 path{animation-delay:-1.6s;}
@keyframes lgFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-16px)}}
@keyframes lgFloatS{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes lgGlowPulse{0%,100%{opacity:1}50%{opacity:.78}}
@keyframes lgTwinkle{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.45;transform:scale(.8)}}

/* ---------- right: glass card ---------- */
.lg-tagline{text-align:right;font-weight:700;font-size:1rem;color:#1D2150;padding:.2rem .4rem 1rem;}
.st-key-login_card{position:relative;background:linear-gradient(160deg,rgba(255,255,255,.72),rgba(255,255,255,.42));
backdrop-filter:blur(24px) saturate(150%);-webkit-backdrop-filter:blur(24px) saturate(150%);border:1px solid rgba(255,255,255,.9);border-radius:38px;
box-shadow:0 30px 80px rgba(99,102,241,.22),0 8px 24px rgba(99,102,241,.10),inset 0 1px 0 rgba(255,255,255,.95);padding:2rem 2.5rem 1.8rem;
animation:lgRise .7s cubic-bezier(.2,.8,.2,1) both;}
.st-key-login_card:before{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;
background:radial-gradient(420px 220px at 15% 0%,rgba(255,255,255,.7),transparent 70%);}
@keyframes lgRise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
.st-key-login_card [data-testid="stVerticalBlock"]{gap:.85rem;}
.lg-card-head{text-align:center;}
.lg-card-head .lg-logo-mark{filter:drop-shadow(0 10px 18px rgba(91,63,214,.35));}
.st-key-login_card .lg-card-head h1{font-size:clamp(2rem,2.6vw,2.7rem)!important;font-weight:800;letter-spacing:-.03em;color:#0E1237;margin:.35rem 0 .1rem!important;padding:0!important;line-height:1.1!important;}
.lg-card-head .lg-card-sub{font-size:1.1rem;color:#38406F;font-weight:500;margin:0 0 .4rem;}

/* inputs */
.st-key-login_card [data-testid="stForm"]{border:none!important;padding:0!important;background:transparent!important;}
.st-key-login_card [data-testid="stForm"] [data-testid="stVerticalBlock"]{display:flex;flex-direction:column;}
.st-key-login_signin,[data-testid="stLayoutWrapper"]:has(>.st-key-login_signin){order:9;}
.st-key-login_card [data-testid="stTextInput"] label{display:none;}
.st-key-login_card [data-baseweb="input"]{background:rgba(255,255,255,.88)!important;border:1px solid rgba(255,255,255,.95)!important;border-radius:20px!important;
min-height:60px;box-shadow:0 8px 22px rgba(99,102,241,.12);transition:box-shadow .2s ease,border-color .2s ease,transform .2s ease;}
.st-key-login_card [data-baseweb="input"]:hover{box-shadow:0 10px 26px rgba(99,102,241,.18);}
.st-key-login_card [data-baseweb="input"]:focus-within{border-color:#8B5CF6!important;box-shadow:0 0 0 4px rgba(139,92,246,.20),0 10px 26px rgba(99,102,241,.18);}
.st-key-login_card [data-baseweb="base-input"]{background:transparent!important;border:none!important;}
.st-key-login_card input{color:#1B1F4B!important;font-size:1.08rem!important;font-weight:500;padding:0 1rem 0 3.5rem!important;height:58px;background-repeat:no-repeat!important;background-position:1.15rem center!important;background-size:24px 24px!important;}
.st-key-login_card input::placeholder{color:#7A84AC!important;opacity:1;font-weight:500;}
.st-key-login_email input,.st-key-signup_email input{background-image:__MAIL__!important;}
.st-key-login_password input,.st-key-signup_password input,.st-key-signup_confirm input{background-image:__LOCK__!important;}
.st-key-signup_name input{background-image:__USER__!important;}
.st-key-login_card [data-baseweb="input"] button{color:#4B5580;background:transparent;}
.st-key-login_card [data-baseweb="input"] button:hover{color:var(--lg-violet);background:rgba(139,92,246,.10);}

/* remember me / forgot */
.st-key-login_card [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:.6rem!important;align-items:center;}
.st-key-login_card [data-testid="stColumn"],.st-key-login_card [data-testid="column"]{min-width:0!important;width:auto!important;flex:1 1 0!important;}
.st-key-login_card [data-testid="stCheckbox"] label{gap:.55rem;}
.st-key-login_card [data-testid="stCheckbox"] p{font-size:1rem;font-weight:600;color:#1F2552;}
.st-key-login_card [data-baseweb="checkbox"]>span:first-of-type{border-radius:7px!important;border:2px solid #8D96C8!important;background:#fff!important;width:22px;height:22px;}
.st-key-login_card [data-baseweb="checkbox"] input:checked+div,.st-key-login_card [data-baseweb="checkbox"] [aria-checked="true"]>span:first-of-type{background:var(--lg-violet)!important;border-color:var(--lg-violet)!important;}
.st-key-login_forgot,.st-key-login_signup_btn{display:flex;}
.st-key-login_forgot{justify-content:flex-end;}
.st-key-login_forgot button,.st-key-login_signup_btn button{background:transparent!important;border:none!important;box-shadow:none!important;padding:.1rem .2rem!important;min-height:0!important;color:var(--lg-violet)!important;}
.st-key-login_forgot button p,.st-key-login_signup_btn button p{font-weight:700;font-size:1rem;color:var(--lg-violet)!important;white-space:nowrap;}
.st-key-login_forgot button:hover p,.st-key-login_signup_btn button:hover p{text-decoration:underline;color:#4527C0!important;}

/* sign in */
.st-key-login_signin button{width:100%;min-height:62px;border:none!important;border-radius:20px!important;color:#fff!important;
background:linear-gradient(90deg,#7C3AED 0%,#5B6CF6 50%,#38A5FA 100%)!important;background-size:140% 100%;background-position:0 0;
box-shadow:0 14px 30px rgba(91,63,214,.38),inset 0 1px 0 rgba(255,255,255,.4);transition:transform .2s ease,box-shadow .25s ease,background-position .4s ease,filter .2s ease;}
.st-key-login_signin button p{font-size:1.15rem;font-weight:700;color:#fff!important;}
.st-key-login_signin button:hover{transform:translateY(-2px);background-position:100% 0;box-shadow:0 18px 38px rgba(91,63,214,.48),0 0 0 4px rgba(124,58,237,.12),inset 0 1px 0 rgba(255,255,255,.45);filter:brightness(1.04);}
.st-key-login_signin button:active{transform:translateY(0) scale(.99);}
.st-key-login_signin button:focus-visible{outline:3px solid rgba(124,58,237,.45)!important;outline-offset:3px;}
.stApp[data-teststate="running"] .st-key-login_signin button{opacity:.85;pointer-events:none;}

/* divider + social */
.lg-or{display:flex;align-items:center;gap:1rem;color:#4A5382;font-size:1rem;font-weight:500;margin:.2rem 0 0;}
.lg-or:before,.lg-or:after{content:"";height:1px;flex:1;background:linear-gradient(90deg,transparent,rgba(124,134,190,.4),transparent);}
.st-key-login_social{max-width:340px;margin:0 auto;width:100%;}
.st-key-login_social button{width:100%;min-height:64px;border-radius:20px!important;border:1px solid rgba(255,255,255,.95)!important;background-color:rgba(255,255,255,.9)!important;
background-repeat:no-repeat!important;background-position:center!important;background-size:30px 30px!important;box-shadow:0 8px 20px rgba(99,102,241,.14);transition:transform .2s ease,box-shadow .2s ease;}
.st-key-login_social button p{font-size:0!important;color:transparent!important;}
.st-key-login_social button:hover{transform:translateY(-3px);box-shadow:0 14px 28px rgba(99,102,241,.24);border-color:#C4B5FD!important;}
.st-key-social_google button{background-image:__GOOGLE__!important;}
.st-key-social_github button{background-image:__GITHUB__!important;}
.st-key-social_linkedin button{background-image:__LINKEDIN__!important;}

.st-key-login_redirect{max-width:340px;margin:0 auto;width:100%;}
.st-key-login_redirect a{border-radius:16px!important;font-weight:700;}

/* sign up row (two equal columns meet in the middle) */
.st-key-login_signup [data-testid="stColumn"]:first-child,.st-key-login_signup [data-testid="column"]:first-child{text-align:right;}
.st-key-login_signup [data-testid="stColumn"]:last-child,.st-key-login_signup [data-testid="column"]:last-child{display:flex;justify-content:flex-start;}
.st-key-login_signup [data-testid="stHorizontalBlock"]{justify-content:center;gap:.4rem!important;}
.st-key-login_signup [data-testid="stColumn"],.st-key-login_signup [data-testid="column"]{flex:0 0 auto!important;width:auto!important;}
.lg-signup-text{font-size:1rem;font-weight:500;color:#2F375F;margin:0;padding-top:.15rem;white-space:nowrap;}

/* messages */
.lg-alert{display:flex;gap:.55rem;align-items:flex-start;background:rgba(254,226,226,.85);border:1px solid #FCA5A5;color:#991B1B;border-radius:16px;padding:.7rem 1rem;font-size:.92rem;font-weight:600;line-height:1.4;}
.lg-alert svg{flex:none;margin-top:2px;}
.lg-demo{text-align:center;font-size:.82rem;color:#4A5382;background:rgba(139,92,246,.08);border:1px dashed rgba(139,92,246,.35);border-radius:14px;padding:.55rem .8rem;line-height:1.5;}
.lg-demo code{background:rgba(255,255,255,.85);padding:.05rem .4rem;border-radius:7px;color:#3B2BA6;font-weight:600;font-size:.8rem;}

/* ---------- responsive ---------- */
@media(max-width:1100px){.lg-text{max-width:60%}.block-container{padding:1.5rem 1.5rem 2rem!important}}
@media(max-width:900px){
.lg-left{min-height:0}.lg-text{max-width:100%}.lg-brand{margin-bottom:1.4rem}
.lg-art{position:relative;right:auto;bottom:auto;width:100%;max-width:560px;height:auto;margin:1.2rem auto 0;display:block;}
.lg-features li{max-width:none}.lg-tagline{text-align:center;padding-top:1rem}
.st-key-login_card{padding:1.6rem 1.3rem 1.4rem;border-radius:30px}
.block-container{padding:1.1rem 1rem 2rem!important}
}
@media(max-width:480px){.lg-brand .lg-name{font-size:1.4rem}.lg-left h1.lg-headline{font-size:2.2rem!important}.st-key-login_card input{font-size:1rem!important}.st-key-login_social{max-width:100%}}
@media(prefers-reduced-motion:reduce){.lg-bg span,.lg-robot,.lg-float2,.lg-float3,.lg-eyes,.lg-spark path,.lg-spark circle,.st-key-login_card{animation:none!important;}}
</style>
"""

CSS = (CSS.replace("__SWOOSH__", SWOOSH).replace("__MAIL__", ICON_MAIL).replace("__USER__", ICON_USER).replace("__LOCK__", ICON_LOCK)
       .replace("__GOOGLE__", ICON_GOOGLE).replace("__GITHUB__", ICON_GITHUB).replace("__LINKEDIN__", ICON_LINKEDIN))


def inject_login_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
