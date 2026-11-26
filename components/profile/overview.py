"""Section 01 – Profile overview, completion score and suggestions."""
from html import escape as esc

import streamlit as st

from components.career_readiness import donut
from components.icons import icon
from components.profile.personal_info import start_editing
from database import repository as repo
from services.profile_completion import compute_completion


def _edit_clicked() -> None:
    start_editing()
    st.session_state.setdefault("flash", []).append(("success", "Edit your details in Personal Information below."))


def render_overview() -> None:
    user, comp = repo.get_user(), compute_completion()
    edu = repo.list_rows("education")
    uni = esc(edu[0]["university"]) if edu else "Add your university"
    status = esc(" · ".join(x for x in (edu[0]["academic_year"], edu[0]["degree"]) if x)) if edu else "Add your education"
    initial = esc((user.get("full_name") or "?")[0].upper())
    total = comp["total"]
    with st.container(key="card_prof_overview"):
        left, mid, right = st.columns([1.5, 0.9, 1.3], vertical_alignment="center")
        with left:
            st.markdown(
                f'<div class="ov"><div class="avatar">{initial}</div><div>'
                f'<div class="ov-name">{esc(user.get("full_name", ""))}</div>'
                f'<div class="ov-line">{esc(user.get("email", ""))}</div>'
                f'<div class="ov-line">{uni}</div><div class="ov-line">{status}</div></div></div>'
                f'<div class="ov-bar"><div class="ov-bar-head"><span>Profile completion</span><b>{total}%</b></div>'
                f'<div class="bar"><i style="width:{total}%"></i></div></div>', unsafe_allow_html=True)
            st.button("Edit Profile", icon=":material/edit:", key="ov_edit", on_click=_edit_clicked)
        mid.plotly_chart(donut(total, "Complete"), use_container_width=True, config={"displayModeBar": False})
        with right:
            if not comp["missing"]:
                st.markdown(f'<div class="tip">{icon("trophy", 26)}<div><b>Profile complete!</b> You are ready for smarter matches.</div></div>',
                            unsafe_allow_html=True)
            else:
                items = "".join(
                    f'<div class="miss"><span>{esc(s["hint"])}</span><b>+{round(s["weight"] - s["earned"])}%</b></div>'
                    for s in sorted(comp["missing"], key=lambda s: s["earned"] - s["weight"])[:4])
                st.markdown(f'<div class="sec-sub" style="margin-bottom:.4rem"><b>Missing information</b></div>{items}',
                            unsafe_allow_html=True)
