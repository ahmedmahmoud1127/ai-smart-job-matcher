"""Top recommended jobs with clickable detail dialogs."""
import pandas as pd
import streamlit as st

from components.icons import icon
from components.navbar import go
from data.sample_data import JOBS, READINESS

LOGOS = {
    "Meta": '<span style="color:#0866FF;font-size:1.6rem">∞</span>',
    "Google": '<span style="background:conic-gradient(#EA4335 0 25%,#FBBC05 0 50%,#34A853 0 75%,#4285F4 0);-webkit-background-clip:text;background-clip:text;color:transparent;font-size:1.5rem">G</span>',
    "Microsoft": '<svg width="26" height="26" viewBox="0 0 26 26"><rect width="12" height="12" fill="#F25022"/><rect x="14" width="12" height="12" fill="#7FBA00"/><rect y="14" width="12" height="12" fill="#00A4EF"/><rect x="14" y="14" width="12" height="12" fill="#FFB900"/></svg>',
}


@st.dialog("Job details", width="large")
def job_dialog(job: dict) -> None:
    st.markdown(f"### {job['title']}")
    st.caption(f"{job['company']} · {job['location']}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Match", f"{job['match']}%")
    c2.metric("Salary", job["salary"])
    c3.metric("Level", job["level"])
    st.write(job["summary"])
    have = [s for s in job["required"] if s in READINESS["available"]]
    lack = [s for s in job["required"] if s not in READINESS["available"]]
    st.markdown("**Skills you have:** " + (", ".join(have) or "–"))
    st.markdown("**Skills to learn:** " + (", ".join(lack) or "None – you're ready!"))
    saved = job["id"] in st.session_state.saved_jobs
    if st.button("Saved ✓" if saved else "Save job", key=f"save_{job['id']}"):
        st.session_state.saved_jobs.symmetric_difference_update({job["id"]})
        st.rerun()


def render_recommended_jobs() -> None:
    df = pd.DataFrame(JOBS).sort_values("match", ascending=False)
    with st.container(key="card_jobs"):
        head, link = st.columns([3, 1], vertical_alignment="center")
        head.markdown(f'<div class="sec-title">{icon("briefcase", 22)}Top Recommended Jobs</div>', unsafe_allow_html=True)
        with link.container(key="link_jobs"):
            st.button("See All", key="jobs_all", on_click=go, args=("Jobs",))
        for job in df.to_dict("records"):
            with st.container(key=f"job_{job['id']}"):
                info, btn = st.columns([4.3, 1.3], vertical_alignment="center")
                info.markdown(
                    f'<div class="job"><div class="logo">{LOGOS[job["company"]]}</div><div>'
                    f'<div class="job-title">{job["title"]}</div><div class="job-meta">{job["company"]} • {job["type"]}</div></div>'
                    f'<span class="match">{job["match"]}% Match</span></div>', unsafe_allow_html=True)
                if btn.button("View Details", key=f"view_{job['id']}", use_container_width=True):
                    job_dialog(job)
