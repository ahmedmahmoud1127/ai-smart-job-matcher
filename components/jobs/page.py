"""Smart Job Matching page: stats, filters, ranked jobs, saved jobs and skill advice."""
import streamlit as st

from components.cv.styles import inject_cv_styles
from components.icons import icon
from components.jobs.cards import render_job_card, saved_note
from components.jobs.filters import PAGE_SIZE, filters_active, init_filter_state, render_filters, reset_filters
from components.jobs.insights import render_profile_card, render_skill_recs
from components.jobs.styles import inject_jobs_styles
from components.navbar import go
from components.profile.styles import inject_profile_styles
from components.profile.widgets import section_title, show_flash
from database import job_repository as job_repo
from services.job_matching import UNLOCK_AT, build_candidate, filter_jobs, rank_jobs, recommend_skills


def _more() -> None:
    st.session_state.jm_limit += PAGE_SIZE


def _stats(results: list, saved_count: int) -> None:
    strong = sum(r["score"] >= UNLOCK_AT for r in results)
    items = [("Jobs Analyzed", len(results), "briefcase", "blue"), (f"Strong Matches ({UNLOCK_AT}%+)", strong, "target", "mint"),
             ("Best Match", f'{results[0]["score"]}%' if results else "–", "star", "cream"), ("Saved Jobs", saved_count, "check", "lav")]
    for col, (label, val, ico, tone) in zip(st.columns(4), items):
        with col.container(key=f"card_jmstat_{ico}"):
            st.markdown(f'<div class="mini"><div class="stat-icon tone-{tone}">{icon(ico, 22)}</div>'
                        f'<div><div class="v">{val}</div><div class="l">{label}</div></div></div>', unsafe_allow_html=True)


def _no_data_card(cand: dict) -> None:
    if cand["skills"]:
        return
    with st.container(key="card_jm_nodata"):
        section_title("bulb", "Add your skills to get accurate matches")
        st.markdown('<div class="empty">Your profile has no skills yet, so every job scores low. Add skills in My Profile or upload '
                    'your CV in the CV Analyzer, then come back.</div>', unsafe_allow_html=True)
        a, b, _ = st.columns([1, 1, 3])
        a.button("Open My Profile", icon=":material/person:", key="jm_nd_profile", on_click=go, args=("My Profile",), use_container_width=True)
        b.button("Open CV Analyzer", icon=":material/description:", key="jm_nd_cv", on_click=go, args=("CV Analyzer",), use_container_width=True)


def _recommended_tab(filtered: list, saved_ids: set, total: int) -> None:
    limit = st.session_state.jm_limit
    note = "filtered" if filters_active() else "all"
    st.markdown(f'<div class="jm-count">Showing {min(limit, len(filtered))} of {len(filtered)} jobs '
                f'({note}, {total} in total) · sorted by {st.session_state.jm_sort.lower()}</div>', unsafe_allow_html=True)
    if not filtered:
        st.markdown('<div class="empty">No jobs match your search and filters. Try removing a filter or lowering the minimum match.</div>',
                    unsafe_allow_html=True)
        st.button("Reset filters", icon=":material/restart_alt:", key="jm_reset_empty", on_click=reset_filters)
        return
    for r in filtered[:limit]:
        render_job_card(r, r["job"]["id"] in saved_ids, "rec")
    if limit < len(filtered):
        with st.container(key="jm_more"):
            st.button(f"Show more jobs ({len(filtered) - limit} left)", key="jm_more_btn", on_click=_more)


def _saved_tab(results: list, saved_rows: list) -> None:
    by_id = {r["job"]["id"]: r for r in results}
    rows = [row for row in saved_rows if row["job_id"] in by_id]
    if not rows:
        st.markdown('<div class="empty">No saved jobs yet. Press <b>Save Job</b> on any job to keep it here.</div>', unsafe_allow_html=True)
        return
    st.markdown(f'<div class="jm-count">{len(rows)} saved job(s) · scores are recalculated from your current profile</div>',
                unsafe_allow_html=True)
    for row in rows:
        render_job_card(by_id[row["job_id"]], True, "sv", saved_note(row["saved_at"]))


def render_jobs_page() -> None:
    init_filter_state()
    inject_profile_styles()  # shared card / list / chip styles
    inject_cv_styles()       # shared badges and mini stat cards
    inject_jobs_styles()
    show_flash()
    st.markdown('<div class="page-title">Smart Job Matching</div><div class="page-sub">Jobs ranked by how well your skills, education '
                'and experience fit each role, with clear gaps and what to learn next.</div>', unsafe_allow_html=True)

    cand = build_candidate()
    results = rank_jobs(cand)
    saved_rows = job_repo.list_saved()
    saved_ids = {r["job_id"] for r in saved_rows}
    valid_saved = [r for r in saved_rows if r["job_id"] in {x["job"]["id"] for x in results}]

    _no_data_card(cand)
    _stats(results, len(valid_saved))
    filters = render_filters()
    filtered = filter_jobs(results, **filters)

    left, right = st.columns([1.8, 1])
    with left:
        tab_rec, tab_saved = st.tabs(["Recommended Jobs", "Saved Jobs"])
        with tab_rec:
            _recommended_tab(filtered, saved_ids, len(results))
        with tab_saved:
            _saved_tab(results, saved_rows)
    with right:
        render_profile_card(cand)
        render_skill_recs(recommend_skills(cand, results))
