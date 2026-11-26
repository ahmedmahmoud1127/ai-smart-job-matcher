"""Login / sign-up page: AI branding on the left, translucent glass card on the right.

The card has two modes (``st.session_state["auth_mode"]``): ``login`` and ``signup``. In both, the user can
continue with Google, GitHub or LinkedIn; a successful sign-in or sign-up lands straight on the Dashboard.
The rest of the app is only rendered once ``st.session_state["authenticated"]`` is True (see app.py).
"""
import json
import re
import time
from html import escape

import streamlit as st

from components.login.art import ROBOT_SCENE, feature_icon, logo_mark
from components.login.styles import inject_login_styles
from database.db import SAMPLE_USER_ID
from database import auth_repository as auth
from database import repository as repo
from services import oauth

SHOW_DEMO_HINT = True      # shows the sample account under the card; set to False for a real deployment
MAX_ATTEMPTS = 5           # failed attempts before a short lock-out
LOCK_SECONDS = 30
EMAIL_RE = auth.EMAIL_RE

FEATURES = [("bolt", "AI-Powered Matching"), ("chart", "Personalized Recommendations"), ("rocket", "Track Your Progress")]
SOCIAL = [("google", "Google"), ("github", "GitHub"), ("linkedin", "LinkedIn")]

_ALERT_ICON = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
               'stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>')


def sign_out() -> None:
    """Callback for the navbar's Sign Out button. Clears the whole session so no data leaks to the next user."""
    st.session_state.clear()


def _left_html() -> str:
    features = "".join(f"<li><i>{feature_icon(icon)}</i>{escape(text)}</li>" for icon, text in FEATURES)
    return (
        '<div class="lg-bg" aria-hidden="true"><span class="s1"></span><span class="s2"></span><span class="s3"></span>'
        '<span class="s4"></span><span class="s5"></span><span class="s6"></span></div>'
        '<div class="lg-left"><div class="lg-text">'
        f'<div class="lg-brand">{logo_mark(58, "l")}<div class="lg-name">AI Smart<b>Job Matcher</b></div></div>'
        '<h1 class="lg-headline">Smarter Matches.<br><span>Brighter Career.</span></h1>'
        '<div class="lg-sub">Let our AI find the best job opportunities that match your skills and goals.</div>'
        f'<ul class="lg-features">{features}</ul></div>{ROBOT_SCENE}</div>')


def _mode() -> str:
    return st.session_state.get("auth_mode", "login")


def _set_mode(mode: str) -> None:
    st.session_state["auth_mode"] = mode


def _card_head() -> str:
    if _mode() == "signup":
        return (f'<div class="lg-card-head">{logo_mark(68, "c")}<h1>Create Account</h1>'
                '<div class="lg-card-sub">Join us and find your perfect job 🚀</div></div>')
    return (f'<div class="lg-card-head">{logo_mark(84, "c")}<h1>Welcome Back!</h1>'
            '<div class="lg-card-sub">Sign in to continue your journey 🚀</div></div>')


def _alert(message: str) -> None:
    st.markdown(f'<div class="lg-alert" role="alert">{_ALERT_ICON}<span>{escape(message)}</span></div>', unsafe_allow_html=True)


def _start_session(user_id: int, remembered_email: str | None = None, welcome: str | None = None) -> None:
    """Mark the session as signed in and go straight to the Dashboard (reruns the app)."""
    for key in ("login_password", "signup_password", "signup_confirm", "login_locked_until"):
        st.session_state.pop(key, None)  # never keep passwords around in the session
    st.session_state.update(authenticated=True, user_id=user_id, login_failures=0, page="Dashboard")
    if remembered_email:
        st.session_state["remembered_email"] = remembered_email
    else:
        st.session_state.pop("remembered_email", None)
    if welcome:
        st.session_state["welcome_message"] = welcome
    st.rerun()


def _sign_in(email: str, password: str, remember: bool) -> str | None:
    """Validate and authenticate. Returns an error message, or reruns the app on success."""
    now = time.time()
    locked_until = st.session_state.get("login_locked_until", 0.0)
    if now < locked_until:
        return f"Too many failed attempts. Please wait {int(locked_until - now) + 1} seconds and try again."
    email = email.strip()
    if not email or not password:
        return "Please enter your email and password."
    if not EMAIL_RE.match(email):
        return "Please enter a valid email address."

    with st.spinner("Signing you in…"):  # loading state
        time.sleep(0.6)                  # short pause so the loading state is visible
        user_id = auth.authenticate(email, password)

    if user_id is None:
        failures = st.session_state.get("login_failures", 0) + 1
        st.session_state["login_failures"] = failures
        if failures >= MAX_ATTEMPTS:
            st.session_state["login_locked_until"] = time.time() + LOCK_SECONDS
            st.session_state["login_failures"] = 0
            return f"Too many failed attempts. Please wait {LOCK_SECONDS} seconds and try again."
        return "Incorrect email or password. Please try again."

    _start_session(user_id, remembered_email=email if remember else None)
    return None


def _login_form() -> str | None:
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email Address", key="login_email", placeholder="Email Address",
                              label_visibility="collapsed", autocomplete="email")
        password = st.text_input("Password", key="login_password", type="password", placeholder="Password",
                                 label_visibility="collapsed", autocomplete="current-password")  # built-in show/hide eye
        # Sign In is declared first so Enter submits it; CSS moves it below the Remember Me row.
        with st.container(key="login_signin"):
            submitted = st.form_submit_button("Sign In", type="primary", icon=":material/login:", use_container_width=True)
        left, right = st.columns(2)
        remember = left.checkbox("Remember Me", key="login_remember")
        with right, st.container(key="login_forgot"):
            forgot = st.form_submit_button("Forgot Password?")
    if forgot:
        st.toast("Password reset by email isn't set up yet. Please use the demo account below.", icon=":material/info:")
        return None
    if submitted:
        return _sign_in(email, password, remember)
    return None


def _sign_up(name: str, email: str, password: str, confirm: str) -> str | None:
    """Validate and create an account. Returns an error message, or signs the user in and reruns on success."""
    name, email = name.strip(), email.strip()
    if not (name and email and password and confirm):
        return "Please fill in all the fields."
    if len(name) < 2:
        return "Please enter your full name."
    if not EMAIL_RE.match(email):
        return "Please enter a valid email address."
    problem = auth.validate_password(password)
    if problem:
        return problem
    if password != confirm:
        return "Passwords do not match."
    with st.spinner("Creating your account…"):
        time.sleep(0.4)
        try:
            user_id = auth.create_user(name, email, password)
        except auth.AccountExistsError:
            return "An account with this email already exists. Please sign in instead."
    _start_session(user_id, welcome=f"Welcome, {name.split()[0]}! Your account is ready.")
    return None


def _signup_form() -> str | None:
    with st.form("signup_form", clear_on_submit=False):
        name = st.text_input("Full Name", key="signup_name", placeholder="Full Name", label_visibility="collapsed",
                             autocomplete="name")
        email = st.text_input("Email Address", key="signup_email", placeholder="Email Address",
                              label_visibility="collapsed", autocomplete="email")
        password = st.text_input("Password", key="signup_password", type="password", placeholder="Password (8+ characters)",
                                 label_visibility="collapsed", autocomplete="new-password")
        confirm = st.text_input("Confirm Password", key="signup_confirm", type="password", placeholder="Confirm Password",
                                label_visibility="collapsed", autocomplete="new-password")
        with st.container(key="login_signin"):
            submitted = st.form_submit_button("Create Account", type="primary", icon=":material/person_add:",
                                              use_container_width=True)
    if submitted:
        return _sign_up(name, email, password, confirm)
    return None


def _redirect_script(url: str) -> None:
    """Send the browser to the provider in the *same* tab (falls back to the visible link below)."""
    js = f"window.location.href = {json.dumps(url)};"
    try:
        st.html(f"<script>{js}</script>", unsafe_allow_javascript=True)
    except TypeError:  # older Streamlit: run it from a component iframe instead
        import streamlit.components.v1 as components
        components.html(f"<script>window.parent.location.href = {json.dumps(url)};</script>", height=0)


def _social_buttons() -> None:
    verb = "Sign up" if _mode() == "signup" else "Continue"
    clicked = None
    with st.container(key="login_social"):
        for col, (key, label) in zip(st.columns(3), SOCIAL):
            if col.button(label, key=f"social_{key}", help=f"{verb} with {label}", use_container_width=True):
                clicked = (key, label)
    if not clicked:
        return
    key, label = clicked
    try:
        url = oauth.build_auth_url(key)
    except oauth.OAuthError:
        st.toast(f"{label} sign-in isn't set up yet. Add its client ID and secret (see README → Social sign-in).",
                 icon=":material/info:")
        return
    _redirect_script(url)
    with st.container(key="login_redirect"):  # shown while the browser is being redirected (or if it was blocked)
        st.link_button(f"Continue to {label}", url, icon=":material/open_in_new:", use_container_width=True)


def _switch_row() -> None:
    signup = _mode() == "signup"
    prompt = "Already have an account?" if signup else "Don't have an account?"
    with st.container(key="login_signup"):
        text, link = st.columns(2)
        text.markdown(f'<div class="lg-signup-text">{escape(prompt)}</div>', unsafe_allow_html=True)
        with link, st.container(key="login_signup_btn"):
            st.button("Sign In" if signup else "Sign Up", key="login_signup_link",
                      on_click=_set_mode, args=("login" if signup else "signup",))


def _demo_hint() -> None:
    email = escape(repo.get_user(SAMPLE_USER_ID).get("email", ""))
    st.markdown(f'<div class="lg-demo">Demo account &nbsp;<code>{email}</code> &nbsp;<code>{escape(auth.DEMO_PASSWORD)}</code></div>',
                unsafe_allow_html=True)


def _handle_oauth_callback() -> str | None:
    """When the provider sends the user back (``?code=...&state=...``), finish the sign-in and open the Dashboard."""
    params = {k: v for k, v in st.query_params.items() if k in ("code", "state", "error", "error_description")}
    if not params:
        return None
    st.query_params.clear()  # a code can only be used once; keep it out of the address bar and the history
    try:
        user_id, created = oauth.complete_login(params)
    except oauth.OAuthError as exc:
        return str(exc)
    name = (repo.get_user(user_id).get("full_name") or "").split()
    welcome = f"Welcome{', ' + name[0] if name else ''}! Your account is ready." if created else None
    _start_session(user_id, welcome=welcome)
    return None


def render_login_page() -> None:
    inject_login_styles()
    callback_error = _handle_oauth_callback()
    st.session_state.setdefault("login_email", st.session_state.get("remembered_email", ""))  # "Remember Me"
    left, right = st.columns([1.5, 1], gap="large")
    with left:
        st.markdown(_left_html(), unsafe_allow_html=True)
    with right:
        st.markdown('<div class="lg-tagline">Find Your Perfect Job with AI ✨</div>', unsafe_allow_html=True)
        signup = _mode() == "signup"
        with st.container(key="login_card"):
            st.markdown(_card_head(), unsafe_allow_html=True)
            error = _signup_form() if signup else _login_form()
            if error or callback_error:
                _alert(error or callback_error)
            st.markdown(f'<div class="lg-or">or {"sign up" if signup else "continue"} with</div>', unsafe_allow_html=True)
            _social_buttons()
            _switch_row()
            if SHOW_DEMO_HINT and not signup:
                _demo_hint()
