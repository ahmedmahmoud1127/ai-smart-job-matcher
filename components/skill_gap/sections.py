"""Skill Gap Analysis page sections."""
from html import escape as esc

import plotly.graph_objects as go_
import streamlit as st

from components.icons import icon
from components.profile.widgets import flash, section_title
from components.skill_gap import state as S
from data.roadmaps import LEVELS
from data.skill_gap_requirements import FOCUS_MODES
from services import skill_gap

ART = """<svg class="sg-art" viewBox="0 0 420 170" preserveAspectRatio="xMaxYMax meet" xmlns="http://www.w3.org/2000/svg">
<ellipse cx="215" cy="164" rx="190" ry="7" fill="#9DB3E6" opacity=".25"/>
<circle cx="70" cy="40" r="26" fill="#ECE9FB"/><circle cx="360" cy="30" r="16" fill="#DCEAFD"/><circle cx="330" cy="92" r="8" fill="#FCEBCB"/>
<rect x="60" y="120" width="70" height="40" rx="9" fill="#C9D8F5"/><rect x="125" y="95" width="70" height="65" rx="9" fill="#A9BFEF"/>
<rect x="190" y="68" width="70" height="92" rx="9" fill="#8AA4E8"/><rect x="255" y="40" width="70" height="120" rx="9" fill="#6F82C4"/>
<path d="M95 112l30-14M160 86l30-16M225 58l30-16" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-dasharray="2 7" opacity=".9"/>
<path d="M290 40V6" stroke="#3A4A85" stroke-width="3" stroke-linecap="round"/><path d="M290 6h30l-8 8 8 8h-30z" fill="#E58BB0"/>
<g fill="none" stroke="#7A6AE0" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity=".85"><path d="M350 70l-14 14 14 14"/><path d="M376 70l14 14-14 14"/></g>
</svg>"""


def render_header() -> None:
    with st.container(key="card_sg_header"):
        st.markdown(f'{ART}<div class="page-title">Skill Gap Analysis</div><div class="page-sub">Compare your skills with job '
                    'requirements and discover what you need to learn.</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------ target job
@st.dialog("Edit target career", width="large")
def edit_dialog(state: dict) -> None:
    careers = skill_gap.careers()
    career = st.selectbox("Target job", careers, index=careers.index(state["career"]))
    st.caption(f"Category: {skill_gap.career_category(career)}")
    level = st.radio("Experience level", LEVELS, index=LEVELS.index(state["level"]), horizontal=True)
    hours = st.slider("Study hours per day", 0.5, 10.0, float(state["hours_per_day"]), 0.5,
                      help="Time estimates assume 5 study days per week.")
    focus = st.selectbox("Learning focus", list(FOCUS_MODES), index=list(FOCUS_MODES).index(state["focus"]), help="How skills are ordered inside each stage and in the recommendations.")
    st.caption(FOCUS_MODES[focus])
    a, b = st.columns(2)
    if a.button("Save", type="primary", use_container_width=True):
        S._save(state, career=career, level=level, hours_per_day=hours, focus=focus)
        flash(f"Target set to {career}. Your skill match was recalculated.")
        st.rerun()
    if b.button("Cancel", use_container_width=True):
        st.rerun()


def render_target_card(state: dict, skills: list) -> None:
    with st.container(key="card_sg_target"):
        head, btn = st.columns([3, 1], vertical_alignment="center")
        with head:
            st.markdown(f'<div class="sg-label">Target Job</div><div class="sg-target"><span class="name">{esc(state["career"])}</span>'
                        f'<span class="sg-pill">{esc(skill_gap.career_category(state["career"]))}</span>'
                        f'<span class="sg-pill lav">{esc(state["level"])} level</span>'
                        f'<span class="sg-pill mint">{state["hours_per_day"]:g} h/day</span></div>', unsafe_allow_html=True)
        if btn.button("Edit", icon=":material/edit:", key="sg_edit", use_container_width=True):
            edit_dialog(state)
        chips = "".join(f'<span class="sg-chip{" added" if s["source"] == "Added here" else ""}" title="{esc(s["source"])}">{esc(s["name"])}'
                        f' <small>{esc(s["level"])}</small></span>' for s in skills)
        st.markdown(f'<div class="sg-label" style="margin-top:.7rem">Current Skills · {len(skills)}</div>'
                    + (f'<div class="sg-chips">{chips}</div>' if skills else
                       '<div class="empty">No skills yet. Add skills below, in My Profile, or analyze your CV.</div>')
                    + '<div class="sg-note">Skills come from My Profile, your latest CV analysis, projects and experience. '
                      'Changes made here only affect this analysis (dashed = added here).</div>', unsafe_allow_html=True)
        with st.form("sg_add_form", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1.2, 0.9], vertical_alignment="bottom")
            c1.text_input("Add a skill", key="sg_new_name", placeholder="e.g. Docker, OOP, Django")
            c2.selectbox("Level", LEVELS, index=LEVELS.index(state["level"]), key="sg_new_level")
            c3.form_submit_button("Add", icon=":material/add:", on_click=S.add_skill, use_container_width=True)
        r1, r2, _ = st.columns([1, 1.6, 1])
        with r1.popover("Remove", icon=":material/delete:", use_container_width=True):
            key = f"sg_rm_{len(skills)}"
            st.multiselect("Skills to remove", [s["name"] for s in skills], key=key, placeholder="Choose skills")
            st.button("Remove selected", key="sg_rm_go", on_click=S.remove_skills, args=(key,), type="primary")
        r2.button("Reset from My Profile & CV", icon=":material/restart_alt:", key="sg_reset", on_click=S.reset_skills, use_container_width=True)


# ------------------------------------------------------------------------------------------ overview ring
def _ring(pct: int) -> go_.Figure:
    fig = go_.Figure(go_.Pie(values=[pct, 100 - pct], hole=0.74, sort=False, direction="clockwise", textinfo="none",
                             marker=dict(colors=["#3FB07F", "#F28DA6"], line=dict(color="#fff", width=3)),
                             hovertemplate="%{label}: %{value}%<extra></extra>", labels=["Skills match", "Skills gap"], showlegend=False))
    fig.update_layout(height=230, margin=dict(t=4, b=4, l=4, r=4), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      annotations=[dict(text=f"<b style='font-size:38px'>{pct}%</b><br><span style='font-size:13px;color:#6B7A99'>Skills Match</span>",
                                        showarrow=False, font=dict(color="#16233F"))])
    return fig


def render_overview(r: dict) -> None:
    with st.container(key="card_sg_overview"):
        section_title("target", "Skills Match Overview", f"Compared with {r['total']} requirements of a {esc(r['career'])}.")
        a, b = st.columns([1, 1], vertical_alignment="center")
        a.plotly_chart(_ring(r["match_pct"]), use_container_width=True, config={"displayModeBar": False})
        b.markdown(f'<div class="sg-ring-legend"><div class="sg-leg"><span class="sg-dot green"></span><div><b>{r["have"]}</b><br><span>Skills You Have</span></div></div>'
                   f'<div class="sg-leg"><span class="sg-dot pink"></span><div><b>{r["need"]}</b><br><span>Skills You Need</span></div></div></div>',
                   unsafe_allow_html=True)
        rows = "".join(f'<div class="sg-cov-row"><span>{esc(c)}</span><div class="bar"><i style="width:{p}%"></i></div><em>{p}%</em></div>'
                       for c, p in sorted(r["category_coverage"].items(), key=lambda kv: kv[1]))
        st.markdown(f'<div class="sg-label" style="margin-top:.4rem">Coverage by area</div><div class="sg-cov">{rows}</div>'
                    '<div class="sg-note">Match % weights each requirement by its importance. A skill below the required level earns partial credit.</div>',
                    unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------ missing skills
def _miss_row(i: dict) -> str:
    pri = {"High": "h", "Medium": "m"}.get(i["importance"], "l")
    tag = "improve" if i["status"] == "partial" else "missing"
    return (f'<div class="sg-miss-row"><span class="sg-pri {pri}"></span>{esc(i["name"])}'
            f'<span class="meta">{tag} · {i["importance"]} · {i["hours"]} h</span></div>')


def render_missing(r: dict) -> None:
    show_all = st.session_state.get("sg_show_all", False)
    todo = r["missing"]
    with st.container(key="card_sg_missing"):
        head, btn = st.columns([2.2, 1.3], vertical_alignment="center")
        with head:
            section_title("bulb", f"Missing Skills ({len(todo)})", "Skills to learn or improve for this job.")
        if len(todo) > 8:
            btn.button("Show less" if show_all else "View All", key="sg_view_all", on_click=S.toggle_all_missing, use_container_width=True)
        if not todo:
            st.markdown('<div class="empty">No missing skills. You cover every requirement for this career. 🎉</div>', unsafe_allow_html=True)
            return
        if show_all:
            for cat, items in r["missing_groups"].items():
                st.markdown(f'<div class="cat">{esc(cat)} · {len(items)}</div>' + "".join(_miss_row(i) for i in items), unsafe_allow_html=True)
        else:
            st.markdown("".join(_miss_row(i) for i in todo[:8]), unsafe_allow_html=True)
            if len(todo) > 8:
                st.caption(f"+ {len(todo) - 8} more. Press View All to see them grouped by category.")
        st.markdown('<div class="sg-note"><span class="sg-pri h" style="display:inline-block"></span> High &nbsp;'
                    '<span class="sg-pri m" style="display:inline-block"></span> Medium &nbsp;'
                    '<span class="sg-pri l" style="display:inline-block"></span> Nice to have</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------ learning roadmap
def _stage_html(s: dict) -> str:
    if s["items"]:
        chips = "".join(f'<span class="sg-chip {"part" if i["status"] == "partial" else "miss"}" title="{esc(i["purpose"])}">'
                        f'{esc(i["name"])} <small>{i["hours"]} h</small></span>' for i in s["items"])
        period = f'Weeks {s["start_week"]}–{s["end_week"]}' if s["end_week"] != s["start_week"] else f'Week {s["start_week"]}'
        sub = f'{period} · {s["hours"]} study hours'
    else:
        chips, sub = "", "Nothing to learn here - you already cover this stage."
    known = "".join(f'<span class="sg-chip known">✓ {esc(n)}</span>' for n in s["known"])
    return (f'<div class="sg-stage {s["color"]}"><div class="sg-node">{s["index"]}</div><div class="sg-body">'
            f'<div class="sg-stage-head"><span class="sg-stage-title">Stage {s["index"]}: {esc(s["name"])}</span>'
            f'<span class="sg-dur">{esc(s["duration"])}</span></div><div class="sg-sub">{sub}</div>'
            f'<div class="sg-prog"><div class="bar"><i style="width:{s["progress_pct"]}%"></i></div>{s["progress_pct"]}% covered</div>'
            f'<div class="sg-chips">{chips}{known}</div></div></div>')


def render_roadmap(r: dict, state: dict) -> None:
    with st.container(key="card_sg_roadmap"):
        head, btn = st.columns([2.2, 1.4], vertical_alignment="center")
        with head:
            section_title("map", "Personalized Learning Roadmap",
                          f"{r['total_duration']} in total · {r['total_hours']} study hours at {r['hours_per_day']:g} h/day" if r["total_hours"] else "You already cover everything.")
        btn.button("Regenerate Roadmap", icon=":material/autorenew:", key="sg_regen", on_click=S.regenerate, use_container_width=True)
        st.session_state.sg_focus_pick = state["focus"]  # keep the widget in sync with the saved state (e.g. after the edit dialog)
        st.selectbox("Learning focus", list(FOCUS_MODES), key="sg_focus_pick", on_change=S.save_focus, help=FOCUS_MODES[state["focus"]])
        st.markdown('<div class="sg-timeline">' + "".join(_stage_html(s) for s in r["stages"]) + "</div>"
                    '<div class="sg-note">Durations come from skill complexity, your experience level and study hours per day '
                    '(5 study days per week). They are estimates, not promises.</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------ recommendations
def render_recommendations(r: dict) -> None:
    with st.container(key="card_sg_recs"):
        section_title("trophy", "Top Recommendations", "Based on your missing skills.")
        st.markdown("".join(f'<div class="sg-rec"><div class="n">{n}</div><div><b>{esc(rec["title"])}</b><span>{esc(rec["reason"])}</span></div></div>'
                            for n, rec in enumerate(r["recommendations"], start=1)), unsafe_allow_html=True)
        with st.container(key="sg_start"):
            st.button("Start Learning Plan", icon=":material/rocket_launch:", key="sg_start_btn", on_click=S.start_learning_plan)
        st.markdown('<div class="sg-note">Opens the Learning Roadmap with this career, level and your skills filled in.</div>', unsafe_allow_html=True)
