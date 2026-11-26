"""Right column: analysis results dashboard."""
from html import escape as esc

import plotly.graph_objects as go_
import streamlit as st

from components.career_readiness import donut
from components.icons import icon
from components.profile.widgets import flash, section_title
from data.job_requirements import ROLE_NAMES
from database import cv_repository as cv_repo
from services import profile_sync
from services.cv_analyzer import analyze_cv
from services.cv_parser import SECTION_LABELS
from services.cv_report import build_pdf
from utils.helpers import friendly_date

CAT_COLOR = {"Programming Languages": "#3B7DD8", "Web Development": "#E5703A", "Data Science": "#7B6BD6",
             "Databases": "#2E9DB5", "Tools & Technologies": "#D2553E", "Soft Skills": "#3FA37A"}
VISIBLE = 12


def _badges(items: list, cls: str = "") -> str:
    return "".join(f'<span class="badge {cls}">{esc(i)}</span>' for i in items) or '<span class="item-meta">None</span>'


def _list(items: list, cls: str = "") -> str:
    return f'<ul class="fb {cls}">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def _change_role(aid: int) -> None:
    row = cv_repo.get_analysis(aid)
    if row:
        cv_repo.update_analysis(aid, analyze_cv(row["extracted_text"], st.session_state[f"cv_role_{aid}"]))
        flash("Role comparison updated.")


def _toggle_skills() -> None:
    st.session_state.cv_show_all = not st.session_state.cv_show_all


# ------------------------------------------------------------------ score + stats
def _score_card(row: dict, r: dict) -> None:
    sc = r["score"]
    with st.container(key="card_cv_score"):
        section_title("star", "Overall Score", f"{esc(row['file_name'])} · analyzed {friendly_date(row['created_at'])}")
        a, b = st.columns([1, 1.5], vertical_alignment="center")
        a.plotly_chart(donut(sc["total"], "CV Score"), use_container_width=True, config={"displayModeBar": False})
        with b:
            st.markdown(f'<div class="score-label">{esc(sc["label"])}</div><div class="item-desc">{esc(sc["explanation"])}</div>'
                        '<div class="disclaimer">This is an estimated CV quality score, not a guarantee of employment or ATS acceptance.</div>',
                        unsafe_allow_html=True)
            st.download_button("Download PDF report", data=build_pdf(r, row["file_name"], friendly_date(row["created_at"])),
                               file_name=f"cv_analysis_{row['id']}.pdf", mime="application/pdf", icon=":material/download:",
                               key=f"dl_{row['id']}")
        bd = sc["breakdown"]
        fig = go_.Figure(go_.Bar(x=[round(100 * v["points"] / v["max"]) for v in bd.values()], y=list(bd), orientation="h",
                                 marker_color="#7FA2EA", hovertemplate="%{y}: %{x}%<extra></extra>"))
        fig.update_layout(height=210, margin=dict(t=4, b=4, l=4, r=4), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(range=[0, 100], title="% of section points", gridcolor="#E3EAF8"),
                          yaxis=dict(autorange="reversed"), font=dict(color="#16233F"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _stats(r: dict) -> None:
    s = r["stats"]
    items = [("Skills Found", s["skills_found"], "layers", "blue"), ("Strengths", s["strengths"], "check", "mint"),
             ("Areas to Improve", s["improvements"], "target", "cream"), ("Keywords Matched", f'{s["keywords_pct"]}%', "star", "lav")]
    for col, (label, val, ico, tone) in zip(st.columns(4), items):
        with col.container(key=f"card_cvstat_{ico}"):
            st.markdown(f'<div class="mini"><div class="stat-icon tone-{tone}">{icon(ico, 22)}</div>'
                        f'<div><div class="v">{val}</div><div class="l">{label}</div></div></div>', unsafe_allow_html=True)


# ------------------------------------------------------------------ skills / feedback
def _skills_card(r: dict) -> None:
    skills, show_all = r["skills"], st.session_state.cv_show_all
    with st.container(key="card_cv_skills"):
        head, btn = st.columns([3, 1.3], vertical_alignment="center")
        with head:
            section_title("layers", f"Your Skills ({len(skills)})", "Detected from your CV text.")
        if len(skills) > VISIBLE:
            btn.button("Show less" if show_all else "View All", key="cv_skills_all", on_click=_toggle_skills, use_container_width=True)
        if not skills:
            st.markdown('<div class="empty">No known skills were detected. Add a Skills section with technologies you use.</div>',
                        unsafe_allow_html=True)
        elif show_all or len(skills) <= VISIBLE:
            for cat, names in r["skills_by_category"].items():
                st.markdown(f'<div class="cat">{esc(cat)} · {len(names)}</div><div class="skills">'
                            + "".join(f'<span class="badge"><i style="background:{CAT_COLOR[cat]}"></i>{esc(n)}</span>' for n in names)
                            + "</div>", unsafe_allow_html=True)
        else:
            badges = "".join(f'<span class="badge" title="{esc(s["category"])}"><i style="background:{CAT_COLOR[s["category"]]}"></i>{esc(s["name"])}</span>'
                             for s in skills[:VISIBLE])
            st.markdown(f'<div class="skills">{badges}<span class="badge more">+ {len(skills) - VISIBLE} more</span></div>', unsafe_allow_html=True)


def _feedback(r: dict) -> None:
    a, b = st.columns(2)
    with a.container(key="card_cv_strengths"):
        section_title("trophy", "Strengths")
        st.markdown(_list(r["strengths"]) if r["strengths"] else '<div class="empty">No clear strengths detected yet.</div>', unsafe_allow_html=True)
    with b.container(key="card_cv_improve"):
        section_title("bulb", "Areas to Improve")
        st.markdown(_list(r["improvements"], "warn") if r["improvements"] else '<div class="empty">Nothing major to fix.</div>', unsafe_allow_html=True)
    with st.container(key="card_cv_recs"):
        section_title("target", "Recommendations", "Based on what was found in your CV.")
        st.markdown(_list(r["recommendations"], "rec"), unsafe_allow_html=True)


# ------------------------------------------------------------------ role comparison
def _role_card(row: dict, r: dict) -> None:
    kw, aid = r["keywords"], row["id"]
    with st.container(key="card_cv_role"):
        section_title("briefcase", "Analyze CV for a Specific Job", "Compare your CV with predefined role requirements.")
        c1, c2 = st.columns([1.3, 1], vertical_alignment="center")
        c1.selectbox("Target role", ROLE_NAMES, index=ROLE_NAMES.index(r["role"]), key=f"cv_role_{aid}",
                     on_change=_change_role, args=(aid,))
        c2.markdown(f'<div class="ov-bar"><div class="ov-bar-head"><span>Skill compatibility</span><b>{kw["compatibility"]}%</b></div>'
                    f'<div class="bar"><i style="width:{kw["compatibility"]}%"></i></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="cat">Matching skills · {len(kw["matched"])}</div><div class="skills">{_badges(kw["matched"], "ok")}</div>'
                    f'<div class="cat">Missing core skills · {len(kw["missing_required"])}</div><div class="skills">{_badges(kw["missing_required"], "miss")}</div>'
                    f'<div class="cat">Missing nice-to-have skills</div><div class="skills">{_badges(kw["missing_preferred"][:10], "miss")}</div>'
                    f'<div class="cat">Other relevant skills you have</div><div class="skills">{_badges(kw["relevant"])}</div>'
                    f'<div class="cat">Suggested keywords</div><div class="skills">{_badges(kw["suggested_keywords"], "sug")}</div>',
                    unsafe_allow_html=True)
        roles = sorted(kw["all_roles"].items(), key=lambda kv: kv[1])
        fig = go_.Figure(go_.Bar(x=[v for _, v in roles], y=[k for k, _ in roles], orientation="h",
                                 marker_color=["#2F6FDE" if k == r["role"] else "#C9D8F5" for k, _ in roles],
                                 hovertemplate="%{y}: %{x}%<extra></extra>"))
        fig.update_layout(height=270, margin=dict(t=4, b=4, l=4, r=4), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(range=[0, 100], title="Skill overlap %", gridcolor="#E3EAF8"), font=dict(color="#16233F"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown(f'<div class="disclaimer">Compatibility is the weighted overlap between your detected skills and the role\'s keyword '
                    f'requirements (text similarity to the role description: {kw["text_similarity"]}%). It is not the probability of being hired.</div>',
                    unsafe_allow_html=True)


# ------------------------------------------------------------------ extracted details
def _details_card(r: dict) -> None:
    with st.container(key="card_cv_details"):
        section_title("cap", "What We Found in Your CV")
        t1, t2, t3 = st.tabs(["Education", "Experience & Projects", "CV Structure"])
        with t1:
            if not r["education"]:
                st.markdown('<div class="empty">Education details could not be identified.</div>', unsafe_allow_html=True)
            for e in r["education"]:
                cells = [("University", e["university"]), ("Faculty", e["faculty"]), ("Degree", e["degree"]),
                         ("Major", e["major"]), ("Graduation year", e["graduation_year"])]
                st.markdown('<div class="kv-grid">' + "".join(f'<div class="kv"><span>{k}</span><b>{esc(str(v)) if v else "—"}</b></div>'
                                                              for k, v in cells) + "</div>", unsafe_allow_html=True)
        with t2:
            if r["experience"]:
                for e in r["experience"]:
                    st.markdown(f'<div class="item-title">{esc(e["title"])} <span class="chip">{esc(e["type"])}</span></div>'
                                f'<div class="item-meta">{esc(e["company"] or "Company not detected")}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="empty">No work experience detected.</div>', unsafe_allow_html=True)
            p = r["projects"]
            st.markdown(f'<div class="cat">Projects · {p["count"]}</div>' + (_list(p["titles"]) if p["titles"] else
                        '<div class="item-meta">No projects detected.</div>'), unsafe_allow_html=True)
        with t3:
            cells = "".join(f'<div><span class="{"y" if ok else "n"}">{"✓" if ok else "!"}</span>{SECTION_LABELS[k]}</div>'
                            for k, ok in r["sections"].items())
            st.markdown(f'<div class="struct">{cells}</div>', unsafe_allow_html=True)
            missing = [SECTION_LABELS[k] for k, ok in r["sections"].items() if not ok]
            st.caption("Missing: " + ", ".join(missing) if missing else "All main sections were found.")


# ------------------------------------------------------------------ profile sync
@st.dialog("Confirm profile update")
def _confirm_dialog(skills: list, contact: dict) -> None:
    st.write("These changes will be added to **My Profile**. Existing information will not be overwritten.")
    if skills:
        st.markdown("**Skills to add** (level set to Intermediate, you can change it in My Profile):")
        st.markdown(", ".join(skills))
    for k, v in contact.items():
        st.markdown(f"**{profile_sync.CONTACT_FIELDS[k]}:** {v}")
    c1, c2 = st.columns(2)
    if c1.button("Confirm and update", type="primary", use_container_width=True):
        res = profile_sync.apply_updates(skills, contact)
        flash(f"Profile updated: {res['skills_added']} skill(s) added" + (f", {len(res['fields_updated'])} field(s) filled." if res["fields_updated"] else "."))
        st.rerun()
    if c2.button("Cancel", use_container_width=True):
        st.rerun()


def _sync_card(row: dict, r: dict) -> None:
    cmp_ = profile_sync.compare_skills([s["name"] for s in r["skills"]])
    contact_new = profile_sync.contact_suggestions(r["contact"])
    with st.container(key="card_cv_sync"):
        section_title("map", "Compare with My Profile", "Nothing changes until you confirm.")
        st.markdown(f'<div class="cat">In both · {len(cmp_["in_both"])}</div><div class="skills">{_badges(cmp_["in_both"], "ok")}</div>'
                    f'<div class="cat">In your profile but not found in your CV · {len(cmp_["profile_only"])}</div>'
                    f'<div class="skills">{_badges(cmp_["profile_only"], "miss")}</div>', unsafe_allow_html=True)
        picked = st.multiselect("In your CV but missing from your profile - select skills to add", cmp_["cv_only"],
                                key=f"sync_skills_{row['id']}_{len(cmp_['cv_only'])}", placeholder="Choose skills...")
        chosen = {}
        for k, v in contact_new.items():
            if st.checkbox(f"Fill empty {profile_sync.CONTACT_FIELDS[k]} with {v}", key=f"sync_{k}_{row['id']}"):
                chosen[k] = v
        if st.button("Review changes", icon=":material/fact_check:", key=f"sync_go_{row['id']}", disabled=not (picked or chosen)):
            _confirm_dialog(picked, chosen)


def render_results(row: dict) -> None:
    r = row["result"]
    _score_card(row, r)
    _stats(r)
    _skills_card(r)
    _feedback(r)
    _role_card(row, r)
    _details_card(r)
    _sync_card(row, r)
