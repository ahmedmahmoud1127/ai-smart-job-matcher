"""Job search box and filters (state lives in st.session_state under jm_* keys)."""
import streamlit as st

from components.profile.widgets import section_title
from data.jobs_catalog import JOBS, LEVELS

PAGE_SIZE = 8
SORTS = ["Best match", "Highest salary", "Newest", "Title (A-Z)"]
DEFAULTS = {"jm_search": "", "jm_work": "All", "jm_emp": "All", "jm_level": "All", "jm_city": "All",
            "jm_role": "All", "jm_min": 0, "jm_sort": "Best match", "jm_limit": PAGE_SIZE}


def init_filter_state() -> None:
    for k, v in DEFAULTS.items():
        st.session_state.setdefault(k, v)


def _reset_limit() -> None:
    st.session_state.jm_limit = PAGE_SIZE


def reset_filters() -> None:
    st.session_state.update(DEFAULTS)


def filters_active() -> bool:
    return any(st.session_state[k] != v for k, v in DEFAULTS.items() if k not in ("jm_sort", "jm_limit"))


def _opts(values) -> list:
    return ["All"] + sorted(set(values))


def render_filters() -> dict:
    """Draw the filter card and return the chosen filters as kwargs for services.job_matching.filter_jobs."""
    with st.container(key="card_jm_filters"):
        section_title("target", "Find Your Next Job", "Search by title, company or skill, then narrow the list with filters.")
        c1, c2, c3 = st.columns([3, 1.2, 0.9], vertical_alignment="bottom")
        c1.text_input("Search jobs", key="jm_search", placeholder="e.g. Python, Data Analyst, Cairo, Remote...",
                      on_change=_reset_limit)
        c2.selectbox("Sort by", SORTS, key="jm_sort", on_change=_reset_limit)
        c3.button("Reset filters", icon=":material/restart_alt:", key="jm_reset", on_click=reset_filters,
                  use_container_width=True, disabled=not filters_active() and st.session_state.jm_sort == "Best match")
        f1, f2, f3, f4, f5, f6 = st.columns([1, 1, 1, 1, 1.25, 1.25])
        f1.selectbox("Work type", _opts(j["work_type"] for j in JOBS), key="jm_work", on_change=_reset_limit)
        f2.selectbox("Employment", _opts(j["employment_type"] for j in JOBS), key="jm_emp", on_change=_reset_limit)
        f3.selectbox("Level", ["All"] + [lv for lv in LEVELS if any(j["level"] == lv for j in JOBS)], key="jm_level",
                     on_change=_reset_limit)
        f4.selectbox("City", _opts(j["city"] for j in JOBS), key="jm_city", on_change=_reset_limit)
        f5.selectbox("Job field", _opts(j["role"] for j in JOBS), key="jm_role", on_change=_reset_limit)
        f6.slider("Minimum match %", 0, 100, step=5, key="jm_min", on_change=_reset_limit)
    ss = st.session_state
    return dict(search=ss.jm_search, work_type=ss.jm_work, employment=ss.jm_emp, level=ss.jm_level, city=ss.jm_city,
                role=ss.jm_role, min_score=ss.jm_min, sort=ss.jm_sort)
