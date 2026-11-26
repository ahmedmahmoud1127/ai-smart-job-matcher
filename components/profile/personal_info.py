"""Section 02 – Personal information (read view + edit form)."""
from html import escape as esc

import streamlit as st

from components.profile.validation import EMAIL_RE, PHONE_RE, normalize_url, valid_url
from components.profile.widgets import flash, render_fields, section_title
from database import repository as repo

FIELDS = [
    dict(name="full_name", label="Full Name", required=True),
    dict(name="email", label="Email Address", required=True),
    dict(name="phone", label="Phone Number", placeholder="+20 100 123 4567"),
    dict(name="country", label="Country"),
    dict(name="city", label="City"),
    dict(name="linkedin", label="LinkedIn Profile", placeholder="https://linkedin.com/in/you"),
    dict(name="github", label="GitHub Profile", placeholder="https://github.com/you"),
    dict(name="portfolio", label="Portfolio Website", placeholder="https://yoursite.com"),
]


def start_editing() -> None:
    st.session_state.profile_edit = True


def stop_editing() -> None:
    st.session_state.profile_edit = False


def _validate(d: dict) -> list:
    errs = []
    for f in FIELDS:
        if f.get("required") and not d[f["name"]]:
            errs.append(f"{f['label']} is required.")
    if d["email"] and not EMAIL_RE.match(d["email"]):
        errs.append("Enter a valid email address.")
    if d["phone"] and not PHONE_RE.match(d["phone"]):
        errs.append("Enter a valid phone number (digits, spaces, + - and brackets only).")
    for name, label, host in (("linkedin", "LinkedIn", "linkedin.com"), ("github", "GitHub", "github.com"), ("portfolio", "Portfolio", "")):
        d[name] = normalize_url(d[name])
        if d[name] and (not valid_url(d[name]) or (host and host not in d[name].lower())):
            errs.append(f"{label} link is not valid.")
    return errs


def render_personal_info() -> None:
    user = repo.get_user()
    with st.container(key="card_prof_personal"):
        head, btn = st.columns([3, 1.3], vertical_alignment="center")
        with head:
            section_title("map", "Personal Information", "Your contact details and online profiles.")
        editing = st.session_state.get("profile_edit", False)
        if not editing:
            btn.button("Edit", icon=":material/edit:", key="personal_edit", on_click=start_editing, use_container_width=True)
            cells = "".join(
                f'<div class="kv"><span>{f["label"]}</span><b>{esc(user.get(f["name"]) or "—")}</b></div>' for f in FIELDS)
            st.markdown(f'<div class="kv-grid">{cells}</div>', unsafe_allow_html=True)
            return
        with st.form("personal_form"):
            data = render_fields(FIELDS, user, "personal")
            c1, c2, _ = st.columns([1, 1, 3])
            saved = c1.form_submit_button("Save Changes", type="primary", use_container_width=True)
            cancel = c2.form_submit_button("Cancel", use_container_width=True)
        if cancel:
            stop_editing()
            st.rerun()
        if saved:
            errors = _validate(data)
            if errors:
                for e in errors:
                    st.error(e)
            else:
                repo.update_user(data)
                flash("Personal information saved.")
                stop_editing()
                st.rerun()
