"""Sections of the Analytics Dashboard. All numbers come from services.analytics; nothing is calculated or invented here."""
from datetime import date
from html import escape as esc

import streamlit as st

from components.analytics import charts
from components.career_readiness import donut
from components.icons import icon
from components.navbar import go
from components.profile.widgets import section_title
from services.analytics import DEFAULT_WINDOW, WINDOWS

PLOT = {"displayModeBar": False}
STATUS_LABEL = {"done": "Completed ✓", "covered": "Already known ✓", "doing": "In Progress", "todo": "Not Started"}
STATUS_PILL = {"done": "done", "covered": "done", "doing": "now", "todo": "todo"}


# ------------------------------------------------------------------------------------------ helpers
def _num(value, unit: str = "") -> str:
    return f"{value:g}{unit}"


def _empty(text: str, key: str, buttons: list = ()) -> None:
    """Empty state used instead of an invented value. buttons = [(label, page, material icon)]."""
    st.markdown(f'<div class="empty">{text}</div>', unsafe_allow_html=True)
    for i, (label, page, ico) in enumerate(buttons):
        st.button(label, icon=ico, key=f"{key}_{i}", on_click=go, args=(page,))


def _nice(iso: str) -> str:
    try:
        return date.fromisoformat(iso[:10]).strftime("%d %b %Y")
    except ValueError:
        return iso


def _tiles(items: list) -> str:
    """items = [(label, value, small text)]"""
    return '<div class="an-tiles">' + "".join(
        f'<div class="an-tile"><span>{esc(l)}</span><b>{v}</b>' + (f"<small>{esc(s)}</small>" if s else "") + "</div>"
        for l, v, s in items) + "</div>"


def _badges(items: list, css: str = "", limit: int = 14) -> str:
    """items = [(name, extra)]"""
    out = "".join(f'<span class="badge {css}">{esc(n)}' + (f' <small>{esc(str(x))}</small>' if x != "" else "") + "</span>" for n, x in items[:limit])
    if len(items) > limit:
        out += f'<span class="badge more">+ {len(items) - limit} more</span>'
    return f'<div class="an-badges">{out}</div>'


def _bar(pct: float, tone: str = "") -> str:
    return f'<div class="bar {tone}"><i style="width:{max(0, min(100, pct))}%"></i></div>'


# ------------------------------------------------------------------------------------------ header + summary cards
def render_header(first_name: str) -> str:
    """Welcome message, title, description and the date-range filter. Returns the selected window label."""
    left, right = st.columns([2.3, 1.5], vertical_alignment="bottom")
    left.markdown(f'<div class="an-eyebrow"><span class="hero-chip">Welcome back, {esc(first_name)} 👋</span></div>'
                  '<div class="page-title">Analytics Dashboard</div>'
                  '<div class="page-sub">Track your career development, learning progress, skills growth and job matching in one place.</div>',
                  unsafe_allow_html=True)
    with right.container(key="an_range"):
        st.markdown('<div class="an-range-note">Date range</div>', unsafe_allow_html=True)
        picked = st.segmented_control("Date range", list(WINDOWS), key="an_window", label_visibility="collapsed")
    return picked or DEFAULT_WINDOW


def _card_html(c: dict) -> str:
    has = c["value"] is not None
    delta = ""
    if has and c["delta"] is not None:
        d = c["delta"]
        cls, arrow = ("up", "▲") if d > 0 else ("down", "▼") if d < 0 else ("flat", "●")
        shown = f"{abs(d):g}{c['delta_unit']}" if d else "no change"
        delta = f'<span class="an-delta {cls}">{arrow} {shown}' + (f' <i>{esc(c["delta_note"])}</i>' if c.get("delta_note") else "") + "</span>"
    value = f'{_num(c["value"])}<small>{esc(c["unit"].strip())}</small>' if has else "–"
    tone_cls = {"blue": "", "mint": "t-mint", "cream": "t-cream", "lav": "t-lav"}[c["tone"]]
    bar = _bar(c["progress"], tone_cls) if has and c["progress"] is not None else ""
    sub = c["sub"] if has else c["empty"]
    return (f'<div class="an-stat"><div class="an-stat-top"><div class="stat-icon tone-{c["tone"]}">{icon(c["icon"], 24)}</div>{delta}</div>'
            f'<div class="an-stat-label">{esc(c["label"])}</div><div class="an-stat-value{"" if has else " none"}">{value}</div>'
            f'{bar}<div class="an-stat-sub">{esc(sub)}</div></div>')


def render_cards(d: dict) -> None:
    for col, c in zip(st.columns(4), d["cards"]):
        with col.container(key=f"card_an_stat_{c['key']}"):
            st.markdown(_card_html(c), unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------ career progress
def render_career(d: dict) -> None:
    c, rm = d["career"], d["roadmap"]
    with st.container(key="card_an_career"):
        section_title("target", "Career Progress", "Your overall readiness and development toward your target career.")
        if not c["has_career"]:
            _empty("No target career yet. Choose one in Skill Gap Analysis and your readiness, remaining skills and stages will appear here.",
                   "an_career_empty", [("Open Skill Gap Analysis", "Skill Gap Analysis", ":material/insights:")])
            return
        a, b = st.columns([1, 1.05], vertical_alignment="center")
        a.plotly_chart(donut(int(c["readiness"]), "Career Readiness"), use_container_width=True, config=PLOT, key="an_ready_donut")
        b.markdown(f'<div class="an-target"><span>Target career</span><b>{esc(c["career"])}</b>'
                   f'<small>{c["have"]} of {c["total"]} requirements met</small></div>'
                   + (f'<div class="an-target"><span>Estimated time to go</span><b>{esc(c["total_duration"])}</b>'
                      f'<small>{c["total_weeks"]} study week(s) at your Skill Gap pace</small></div>' if c["need"] else
                      '<div class="an-target"><b>You meet every requirement 🎉</b></div>'), unsafe_allow_html=True)
        stages_txt = f'{rm["stages_completed"]}/{rm["stage_count"]}' if rm.get("has_roadmap") else "–"
        stages_sub = ("completed in your roadmap" if rm.get("has_roadmap") else "no roadmap yet")
        st.markdown(_tiles([("Roadmap stages", stages_txt, stages_sub), ("Remaining skills", str(c["need"]),
                            f'{c["missing_count"]} missing · {c["partial_count"]} partial')]), unsafe_allow_html=True)
        st.markdown('<div class="an-sub">Career development progress</div>', unsafe_allow_html=True)
        rows = "".join(f'<div class="an-row"><div class="an-row-top"><span class="an-row-name">{i}. {esc(s["name"])}</span>'
                       f'<span class="pill {"done" if s["pct"] >= 100 else "now" if s["pct"] else "todo"}">{s["pct"]}%</span></div>'
                       f'{_bar(s["pct"])}<div class="an-row-meta">{s["left"]} skill(s) left</div></div>' for i, s in enumerate(c["stages"], 1))
        st.markdown(rows, unsafe_allow_html=True)
        if len(c["history"]) >= 2:
            st.markdown('<div class="an-sub">Readiness over time</div>', unsafe_allow_html=True)
            st.plotly_chart(charts.readiness_history(c["history"]), use_container_width=True, config=PLOT, key="an_ready_hist")
        else:
            st.markdown('<div class="an-note">Readiness history is recorded each day you open this page. A trend line appears after your next visit.</div>',
                        unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------ skills
def render_skills(d: dict) -> None:
    s = d["skills"]
    with st.container(key="card_an_skills"):
        section_title("layers", "Skills Analytics", "Current, acquired and missing skills by category.")
        if not s["groups"]:
            _empty("No skills to analyse yet. Add skills in My Profile, upload your CV or choose a target career.", "an_skills_empty",
                   [("Open My Profile", "My Profile", ":material/person:"), ("Open CV Analyzer", "CV Analyzer", ":material/description:")])
            return
        st.markdown(_tiles([("Current skills", str(len(s["current"])), "profile, projects & CV"),
                            ("Acquired", str(s["acquired_count"]), f'via roadmap · {d["window"].lower()}'),
                            ("Missing", str(len(s["missing"])), "for your target career")]), unsafe_allow_html=True)
        view = st.segmented_control("Show", ["All", "Current", "Acquired", "Missing"], key="an_skill_view", label_visibility="collapsed") or "All"
        st.plotly_chart(charts.skills_by_category(s["groups"], view), use_container_width=True, config=PLOT, key="an_skill_chart")
        _skill_lists(s, view)
        st.markdown('<div class="an-note">Categories follow the skill catalogue; missing skills come from your Skill Gap Analysis. '
                    'Hover a bar to see the skills behind it.</div>', unsafe_allow_html=True)


def render_recent(d: dict) -> None:
    s = d["skills"]
    with st.container(key="card_an_recent"):
        section_title("check", "Recently Acquired Skills", f'Skills you completed in your Learning Roadmap · {d["window"].lower()}.')
        if s["recent"]:
            st.markdown('<div class="an-list">' + "".join(
                f'<div class="an-li"><div class="ico">{icon("check", 16)}</div><div><div class="t">{esc(e["skill"])}</div>'
                f'<div class="m">{esc(e["stage"])} · {e["date"]:%d %b %Y}</div></div><div class="r">{e["hours"]} h</div></div>' for e in s["recent"])
                + "</div>", unsafe_allow_html=True)
        elif not d["roadmap"].get("has_roadmap"):
            _empty("Skills you complete in the Learning Roadmap appear here.", "an_recent_empty",
                   [("Open Learning Roadmap", "Learning Roadmap", ":material/school:")])
        else:
            st.markdown(f'<div class="empty">No skills completed in this period ({esc(d["window"].lower())}).</div>', unsafe_allow_html=True)


def _skill_lists(s: dict, view: str) -> None:
    css = {"Current": "", "Acquired": "ok", "Missing": "miss"}
    keys = {"Current": "current_names", "Acquired": "acquired_names", "Missing": "missing_names"}
    for label in ([view] if view != "All" else ["Current", "Acquired", "Missing"]):
        groups = [g for g in s["groups"] if g[keys[label]]]
        if not groups:
            continue
        if view == "All":
            names = [(n, "") for g in groups for n in g[keys[label]]]
            st.markdown(f'<div class="an-sub">{label} skills ({len(names)})</div>' + _badges(names, css[label], 12), unsafe_allow_html=True)
        else:
            html = "".join(f'<div class="cat">{esc(g["group"])}</div>' + _badges([(n, "") for n in g[keys[label]]], css[label], 20) for g in groups)
            st.markdown(html, unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------ learning activity
def render_learning(d: dict) -> None:
    L = d["learning"]
    with st.container(key="card_an_learning"):
        section_title("chart", "Learning Activity", "Estimated study time from the skills you complete in your Learning Roadmap.")
        if not L["has_data"]:
            msg = ("You have a roadmap but no completed skills yet. Tick a skill and your daily, weekly and monthly hours will appear here."
                   if d["roadmap"].get("has_roadmap") else "No learning activity yet. Generate a Learning Roadmap and tick skills as you finish them.")
            _empty(msg, "an_learn_empty", [("Open Learning Roadmap", "Learning Roadmap", ":material/school:")])
            return
        cons = f'{L["consistency"]}%' if L["consistency"] is not None else "–"
        st.markdown(_tiles([("Today", _num(L["today_hours"], " h"), "daily"), ("Last 7 days", _num(L["week_hours"], " h"), "weekly"),
                            ("Last 30 days", _num(L["month_hours"], " h"), "monthly"),
                            ("Tasks completed", str(L["total_tasks"]), f'{L["window_tasks"]} in {d["window"].lower()}'),
                            ("Consistency", cons, f'{L["active_days"]} active day(s) · streak {L["streak"]}')]), unsafe_allow_html=True)
        week, heat = st.columns(2)
        with week:
            st.markdown('<div class="an-sub">Weekly activity · hours per day</div>', unsafe_allow_html=True)
            st.plotly_chart(charts.weekly_hours(L["weekly"]), use_container_width=True, config=PLOT, key="an_week_chart")
            best = L["best_day"]
            if best:
                st.markdown(f'<div class="an-note">Most active day this week: <b>{esc(best["full"])}</b> ({best["hours"]:g} h).</div>', unsafe_allow_html=True)
        with heat:
            st.markdown('<div class="an-sub">Activity heatmap · darker = more hours</div>', unsafe_allow_html=True)
            st.plotly_chart(charts.activity_heatmap(L["heatmap"]), use_container_width=True, config=PLOT, key="an_heat_chart")
        st.markdown('<div class="an-note">The app has no study timer, so hours are estimated: when you tick a skill, the hours planned for it in your roadmap '
                    'are credited to that day. Consistency = active days ÷ days in the selected period.</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------ roadmap
def render_roadmap(d: dict) -> None:
    r = d["roadmap"]
    with st.container(key="card_an_roadmap"):
        section_title("map", "Learning Roadmap Analytics", "Connected to your Learning Roadmap.")
        if not r["has_roadmap"]:
            _empty("You have no learning roadmap yet. Create one and your stage and task progress will be tracked here.", "an_rm_empty",
                   [("Create a Roadmap", "Learning Roadmap", ":material/school:")])
            return
        a, b = st.columns([1, 1.2], vertical_alignment="center")
        a.plotly_chart(donut(int(r["pct"]), "Completed"), use_container_width=True, config=PLOT, key="an_rm_donut")
        b.markdown(f'<div class="an-target"><span>Roadmap</span><b>{esc(r["career"])}</b><small>{esc(r["level"])} level'
                   + (f' · finish {esc(_nice(r["finish_on"]))}' if r.get("finish_on") else "") + "</small></div>"
                   + f'<div class="an-target"><span>Study hours</span><b>{r["hours_done"]} / {r["plan_hours"]} h</b><small>{r["hours_left"]} h left</small></div>',
                   unsafe_allow_html=True)
        st.markdown(_tiles([("Completed stages", f'{r["stages_completed"]}/{r["stage_count"]}', ""), ("In progress", str(r["stages_in_progress"]), ""),
                            ("Remaining", str(r["stages_remaining"]), ""), ("Tasks done", f'{r["done"]}/{r["total"]}', "skills completed")]),
                    unsafe_allow_html=True)
        st.markdown('<div class="an-sub">Stage progress</div>' + "".join(
            f'<div class="an-row"><div class="an-row-top"><span class="an-row-name">{s["index"]}. {esc(s["name"])}</span>'
            f'<span class="pill {STATUS_PILL[s["status"]]}">{STATUS_LABEL[s["status"]]}</span></div>{_bar(s["pct"])}'
            f'<div class="an-row-meta">{s["done"]} of {s["total"]} skills · {s["hours"]} h</div></div>' for s in r["stages"]), unsafe_allow_html=True)
        st.markdown('<div class="an-sub">Upcoming learning tasks</div>', unsafe_allow_html=True)
        if r["upcoming"]:
            st.markdown('<div class="an-list">' + "".join(
                f'<div class="an-li"><div class="ico todo">{icon("book", 16)}</div><div><div class="t">{esc(u["name"])}</div>'
                f'<div class="m">{esc(u["stage"])} · {esc(u["priority"])}</div></div><div class="r">{u["hours"]} h</div></div>' for u in r["upcoming"][:4])
                + "</div>" + (f'<div class="an-note">+ {len(r["upcoming"]) - 4} more upcoming task(s)</div>' if len(r["upcoming"]) > 4 else ""),
                unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty">Every roadmap task is completed. Great work! 🎉</div>', unsafe_allow_html=True)
        st.button("Open Learning Roadmap", icon=":material/school:", key="an_rm_open", on_click=go, args=("Learning Roadmap",))


# ------------------------------------------------------------------------------------------ jobs
def render_jobs(d: dict) -> None:
    j = d["jobs"]
    with st.container(key="card_an_jobs"):
        section_title("briefcase", "Job Matching Analytics", "Connected to Smart Job Matching: scores are recalculated from your current profile and CV.")
        if not j["total"]:
            _empty("No jobs are available to analyse.", "an_jobs_empty")
            return
        if j["no_skills"]:
            st.markdown('<div class="empty">Your profile has no skills yet, so every match is low. Add skills in My Profile or analyse your CV for accurate scores.</div>',
                        unsafe_allow_html=True)
        best = j["best"]
        st.markdown(_tiles([("Jobs analysed", str(j["total"]), "in the job catalogue"), ("Best match", f'{best["score"]}%', esc_short(best["job"]["title"])),
                            ("Average match", _num(j["avg"], "%"), "across all jobs"), (f'Highly matched', str(j["strong"]), f'score {j["strong_at"]}% or more')]),
                    unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1.25, 1.05, 1])
        with c1:
            st.markdown('<div class="an-sub">Your best matches</div>', unsafe_allow_html=True)
            st.plotly_chart(charts.top_jobs(j["top"]), use_container_width=True, config=PLOT, key="an_jobs_top")
        with c2:
            st.markdown('<div class="an-sub">Match score history</div>', unsafe_allow_html=True)
            if len(j["history"]) >= 2:
                st.plotly_chart(charts.match_history(j["history"]), use_container_width=True, config=PLOT, key="an_jobs_hist")
            else:
                st.markdown('<div class="empty">History is not available yet. Your scores are recorded once a day when you open this page, '
                            'so a comparison chart appears after your next visit.</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="an-sub">Most requested skills · top {j["requested_from"]} matches</div>', unsafe_allow_html=True)
            if j["requested"]:
                st.markdown(_badges([(r["skill"], f'{r["jobs"]} jobs') for r in j["requested"] if r["have"]], "ok", 8)
                            + _badges([(r["skill"], f'{r["jobs"]} jobs') for r in j["requested"] if not r["have"]], "miss", 8)
                            + '<div class="an-legend"><span><i style="background:#3FB07F"></i>You have it</span>'
                              '<span><i style="background:#E5A23A"></i>Not in your profile yet</span></div>', unsafe_allow_html=True)
        st.button("Open Smart Job Matching", icon=":material/search:", key="an_jobs_open", on_click=go, args=("Jobs",))


def esc_short(text: str, n: int = 28) -> str:
    return text if len(text) <= n else text[: n - 1] + "…"


# ------------------------------------------------------------------------------------------ CV
def render_cv(d: dict) -> None:
    cv = d["cv"]
    with st.container(key="card_an_cv"):
        section_title("book", "CV Analytics", "Based on the analyses stored by the CV Analyzer.")
        if not cv["has_cv"]:
            _empty("No CV analysis found. Upload your CV in the CV Analyzer to see your score, detected skills and improvement here.", "an_cv_empty",
                   [("Open CV Analyzer", "CV Analyzer", ":material/description:")])
            return
        lt = cv["latest"]
        a, b = st.columns([1, 1.1], vertical_alignment="center")
        a.plotly_chart(donut(int(lt["score"]), "CV Score"), use_container_width=True, config=PLOT, key="an_cv_donut")
        chg = cv["since_last"]
        b.markdown(f'<div class="an-target"><span>Latest analysis</span><b>{esc(lt["label"] or "Analysed")}</b>'
                   f'<small>{esc(lt["file_name"])} · {esc(lt["role"])}'
                   + (f' · {lt["date"]:%d %b %Y}' if lt["date"] else "") + "</small></div>"
                   + (f'<div class="an-target"><span>Since previous CV</span><b>{"+" if chg > 0 else ""}{chg} pts</b></div>' if chg is not None else ""),
                   unsafe_allow_html=True)
        tiles = [("Analyses", str(cv["count"]), "stored"), ("Skills found", str(len(lt["skills"])), "in your latest CV"),
                 ("Missing skills", str(len(lt["missing"])), f'for {lt["role"]}')]
        if cv["improvement"] is not None:
            tiles.append(("Overall change", f'{"+" if cv["improvement"] > 0 else ""}{cv["improvement"]} pts', "first → latest"))
        st.markdown(_tiles(tiles), unsafe_allow_html=True)
        st.markdown('<div class="an-sub">Skills detected in your CV</div>' + (
            _badges([(n, "") for n in lt["skills"]], "ok", 12) if lt["skills"] else '<div class="empty">No skills were detected.</div>'), unsafe_allow_html=True)
        st.markdown(f'<div class="an-sub">Missing skills identified for {esc(lt["role"])}</div>' + (
            _badges([(n, "") for n in lt["missing"]], "miss", 10) if lt["missing"] else '<div class="empty">No missing skills for this role. 🎉</div>'),
                    unsafe_allow_html=True)
        st.markdown('<div class="an-sub">CV analysis history</div>', unsafe_allow_html=True)
        if len(cv["history"]) >= 2:
            st.plotly_chart(charts.cv_history(cv["history"]), use_container_width=True, config=PLOT, key="an_cv_hist")
        elif cv["history"]:
            st.markdown('<div class="an-note">Only one analysis in this period. Analyse an improved CV to see your progress as a trend line.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="empty">No CV analyses in this period ({esc(d["window"].lower())}). Your latest score is shown above.</div>', unsafe_allow_html=True)
        if cv["history"]:
            st.markdown('<div class="an-list">' + "".join(
                f'<div class="an-li"><div class="ico todo">{icon("book", 16)}</div><div><div class="t">{esc(h["file"])}</div>'
                f'<div class="m">{esc(h["role"])} · {h["date"]:%d %b %Y}</div></div><div class="r">{h["score"]}/100</div></div>'
                for h in reversed(cv["history"][-3:])) + "</div>", unsafe_allow_html=True)
        st.button("Open CV Analyzer", icon=":material/description:", key="an_cv_open", on_click=go, args=("CV Analyzer",))


# ------------------------------------------------------------------------------------------ insights
def render_insights(d: dict) -> None:
    with st.container(key="card_an_insights"):
        section_title("bulb", "Your Career Insights", "Generated from your real statistics. They update as your data changes.")
        st.markdown('<div class="an-ins">' + "".join(
            f'<div class="an-ins-item"><div class="stat-icon tone-{i["tone"]}">{icon(i["icon"], 20)}</div><div><b>{esc(i["title"])}</b><p>{esc(i["text"])}</p></div></div>'
            for i in d["insights"]) + "</div>", unsafe_allow_html=True)
