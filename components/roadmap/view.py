"""Roadmap results: summary stats, progress, skills overview and the learning stages with progress tracking."""
from datetime import date
from html import escape as esc

import streamlit as st

from components.career_readiness import donut
from components.icons import icon
from components.profile.widgets import flash, section_title
from database import roadmap_repository as roadmap_repo

STATUS_LABEL = {"done": "Completed ✓", "doing": "In Progress", "todo": "Not Started", "covered": "Already known ✓"}
PILL_CLASS = {"done": "done", "doing": "now", "todo": "todo", "covered": "done"}


def _nice_date(iso: str) -> str:
    try:
        return date.fromisoformat(iso[:10]).strftime("%d %b %Y")
    except ValueError:
        return iso


def _done_key(rid: int, skill: str) -> str:
    return f"rm_done_{rid}_{skill}"


# ------------------------------------------------------------------------------------------ callbacks
def _toggle_skill(rid: int, skill: str) -> None:
    done = bool(st.session_state[_done_key(rid, skill)])
    roadmap_repo.set_completed(rid, skill, done)
    if done:
        flash(f"Completed “{skill}”. Keep going!")


def _set_skills(rid: int, skills: list, done: bool, message: str = "") -> None:
    roadmap_repo.set_many_completed(rid, skills, done)
    for s in skills:  # keep the checkboxes in sync with the database
        st.session_state[_done_key(rid, s)] = done
    if message:
        flash(message)


# ------------------------------------------------------------------------------------------ summary
def render_stats(plan: dict, prog: dict) -> None:
    items = [("Career goal", plan["career"], f'{plan["level"]} level', "target", "blue", True),
             ("Skills to learn", str(plan["missing_count"]), f'You already cover {plan["coverage_pct"]}% of this roadmap', "layers", "mint", False),
             ("Estimated time", plan["total_duration"] or "Done", f'{plan["total_hours"]} h at {plan["hours_per_day"]:g} h/day', "cap", "cream", False),
             ("Progress", f'{prog["pct"]}%', f'{prog["done"]} of {prog["total"]} skills completed', "trophy", "lav", False)]
    for col, (label, val, sub, ico, tone, small) in zip(st.columns(4), items):
        with col.container(key=f"card_rmstat_{ico}"):
            st.markdown(f'<div class="mini"><div class="stat-icon tone-{tone}">{icon(ico, 22)}</div><div>'
                        f'<div class="v{" sm" if small else ""}">{esc(val)}</div><div class="l">{label}</div>'
                        f'<div class="s">{esc(sub)}</div></div></div>', unsafe_allow_html=True)


def render_progress_card(rid: int, plan: dict, prog: dict) -> None:
    all_skills = [s["name"] for st_ in plan["stages"] for s in st_["skills"]]
    with st.container(key="card_rm_progress"):
        section_title("trophy", "Your Progress", "Tick skills as you finish them and the percentage updates automatically.")
        if not all_skills:
            st.markdown('<div class="empty">You already know every skill in this roadmap. Choose another career or enable bonus '
                        'skills, then regenerate.</div>', unsafe_allow_html=True)
            return
        st.plotly_chart(donut(prog["pct"], "Completed"), use_container_width=True, config={"displayModeBar": False}, key="rm_donut")
        st.markdown(f'<div class="rm-timeline"><div><span class="item-meta">Skills done</span><b>{prog["done"]} / {prog["total"]}</b></div>'
                    f'<div><span class="item-meta">Hours left</span><b>≈ {prog["hours_left"]} h</b></div>'
                    f'<div><span class="item-meta">Planned finish</span><b>{_nice_date(plan["finish_on"])}</b></div></div>',
                    unsafe_allow_html=True)
        if prog["next"]:
            n = prog["next"]
            st.markdown(f'<div class="rm-next" style="margin-top:.7rem">{icon("bulb", 22)}<div><b>Next up: {esc(n["skill"])}</b><br>'
                        f'{esc(n["stage"])} · about {n["hours"]} h</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="rm-next" style="margin-top:.7rem">{icon("trophy", 22)}<div><b>Roadmap complete!</b><br>'
                        'Update your skills above and regenerate to plan what comes next.</div></div>', unsafe_allow_html=True)
        st.button("Reset progress", icon=":material/restart_alt:", key="rm_reset", on_click=_set_skills,
                  args=(rid, all_skills, False, "Progress reset."), disabled=prog["done"] == 0)


def render_skill_cards(plan: dict, completed: set) -> None:
    known = plan["known_skills"]
    inferred = plan["inferred"]
    with st.container(key="card_rm_known"):
        section_title("check", "Current Skills", "What you already know for this career and beyond.")
        if known or inferred:
            html = "".join(f'<span class="badge ok">{esc(s)}</span>' for s in known)
            html += "".join(f'<span class="badge sug" title="Counted as known because you know {esc(v)}">{esc(s)} (from {esc(v)})</span>'
                            for s, v in inferred.items())
            st.markdown(f'<div class="skills">{html}</div>', unsafe_allow_html=True)
            if inferred:
                st.markdown('<div class="disclaimer">Purple skills are basics counted as known because you know a skill that builds on them.</div>',
                            unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty">No skills entered yet, so the roadmap starts from the very beginning.</div>', unsafe_allow_html=True)
    with st.container(key="card_rm_missing"):
        section_title("bulb", "Missing Skills", "Skills you need to acquire, in the order you should learn them.")
        pending = [(s, st_) for st_ in plan["stages"] for s in st_["skills"]]
        if not pending:
            st.markdown('<div class="empty">Nothing missing. You cover every skill in this roadmap.</div>', unsafe_allow_html=True)
            return
        core = "".join(f'<span class="badge {"ok" if s["name"] in completed else "miss"}">{esc(s["name"])}</span>'
                       for s, _ in pending if s["priority"] == "core")
        bonus = "".join(f'<span class="badge {"ok" if s["name"] in completed else "sug"}">{esc(s["name"])}</span>'
                        for s, _ in pending if s["priority"] == "bonus")
        st.markdown(f'<div class="cat">Core skills for the job</div><div class="skills">{core or "<span class=item-meta>None</span>"}</div>'
                    + (f'<div class="cat">Bonus skills</div><div class="skills">{bonus}</div>' if bonus else "")
                    + '<div class="disclaimer">Green means you have marked the skill as completed.</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------ stages
def _resources_html(resources: list) -> str:
    out = ['<div class="rm-res-title">Learning resources</div><div class="rm-res-list">']
    for r in resources:
        meta = f'{esc(r["provider"])} · {esc(r["kind"])} · {"Free" if r["free"] else "Free to audit / paid"}'
        if r["url"]:
            out.append(f'<a class="rm-res" href="{esc(r["url"])}" target="_blank" rel="noopener noreferrer">{esc(r["title"])}<span>{meta}</span></a>')
        else:
            out.append(f'<div class="rm-res plain">{esc(r["title"])}<span>{esc(r["provider"])} · {esc(r["kind"])}</span></div>')
    return "".join(out) + "</div>"


def _render_skill_row(rid: int, stage_i: int, k: int, skill: dict, completed: set) -> None:
    key = _done_key(rid, skill["name"])
    with st.container(key=f"item_rm_skill_{stage_i}_{k}"):
        left, right = st.columns([1.1, 2.2], gap="medium")
        with left:
            st.session_state[key] = skill["name"] in completed  # the database is the source of truth
            st.checkbox(skill["name"], key=key, on_change=_toggle_skill, args=(rid, skill["name"]))
            st.markdown(f'<div class="rm-skill-meta"><span class="chip {skill["priority"]}">{"Core" if skill["priority"] == "core" else "Bonus"}</span>'
                        f'<span class="chip">≈ {skill["hours"]} h</span><span class="chip">{skill["days"]} study day(s)</span></div>',
                        unsafe_allow_html=True)
        right.markdown(_resources_html(skill["resources"]), unsafe_allow_html=True)


def _render_stage(rid: int, stage: dict, sp: dict, completed: set) -> None:
    status = sp["status"]
    num = icon("check", 20, "#fff", 3) if status in ("done", "covered") else stage["index"]
    chips = ""
    if stage["skills"]:
        weeks = f'Week {stage["start_week"]}' if stage["start_week"] == stage["end_week"] else f'Weeks {stage["start_week"]}–{stage["end_week"]}'
        chips = (f'<span class="chip soft">{weeks}</span><span class="chip">{stage["duration"]}</span>'
                 f'<span class="chip">{stage["hours"]} h</span>')
    with st.container(key=f"card_rm_stage_{stage['index']}"):
        st.markdown(
            f'<div class="rm-stage-head"><div class="rm-num {status}">{num}</div><div class="rm-stage-title">'
            f'<div class="item-title">Stage {stage["index"]}: {esc(stage["name"])}</div><div class="item-meta">{esc(stage["goal"])}</div></div>'
            f'<div class="rm-chips">{chips}<span class="pill {PILL_CLASS[status]}">{STATUS_LABEL[status]}</span></div></div>',
            unsafe_allow_html=True)
        if not stage["skills"]:
            badges = "".join(f'<span class="badge ok">{esc(s)}</span>' for s in stage["covered"])
            st.markdown(f'<div class="item-meta" style="margin:.6rem 0 .3rem">You already know everything in this stage, so you can skip it.</div>'
                        f'<div class="skills">{badges}</div>', unsafe_allow_html=True)
            return
        st.markdown(f'<div class="rm-stage-bar"><span>{sp["done"]} of {sp["total"]} skills completed</span>'
                    f'<div class="bar"><i style="width:{sp["pct"]}%"></i></div><span>{sp["pct"]}%</span></div>', unsafe_allow_html=True)
        if stage["covered"]:
            st.markdown('<div class="item-meta">Already known here: ' + ", ".join(esc(s) for s in stage["covered"]) + "</div>", unsafe_allow_html=True)
        for k, skill in enumerate(stage["skills"]):
            _render_skill_row(rid, stage["index"], k, skill, completed)
        st.markdown(f'<div class="tip">{icon("bulb", 22)}<div><b>Mini project:</b> {esc(stage["project"])}</div></div>', unsafe_allow_html=True)
        names = [s["name"] for s in stage["skills"]]
        all_done = sp["done"] == sp["total"]
        st.button("Mark all as not done" if all_done else "Mark stage as completed",
                  icon=":material/undo:" if all_done else ":material/done_all:", key=f"rm_stage_btn_{rid}_{stage['index']}",
                  on_click=_set_skills, args=(rid, names, not all_done,
                                              "" if all_done else f"Stage {stage['index']} completed. Well done!"))


def render_stages(rid: int, plan: dict, prog: dict, completed: set) -> None:
    with st.container(key="rm_stages_title"):
        section_title("map", "Learning Stages", f'{len(plan["stages"])} stages · studying {plan["hours_per_day"]:g} h/day, '
                      f'{plan["study_days_per_week"]} days/week · generated on {_nice_date(plan["generated_on"])}')
    for stage, sp in zip(plan["stages"], prog["stages"]):
        _render_stage(rid, stage, sp, completed)
