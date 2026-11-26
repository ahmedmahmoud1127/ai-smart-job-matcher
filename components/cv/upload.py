"""Left column: upload card, pro tip and previous analyses."""
from html import escape as esc

import streamlit as st

from components.icons import icon
from components.profile.widgets import flash, section_title
from data.job_requirements import ROLE_NAMES
from database import cv_repository as cv_repo
from database import repository as repo
from services.cv_analyzer import analyze_cv
from services.cv_extractor import CVError, extract_text, fetch_from_link
from utils.helpers import format_size, friendly_date


def default_role() -> str:
    prefs = repo.get_preferences()
    role = prefs.get("target_role", "")
    return role if role in ROLE_NAMES else "Software Engineer"


def _remove_file() -> None:
    st.session_state.cv_uploader_key += 1


def _run_analysis(upload, link: str, role: str) -> None:
    try:
        with st.spinner("Analyzing your CV... extracting text, detecting skills and scoring"):
            if upload is not None:
                data, name, source = upload.getvalue(), upload.name, ""
            elif link.strip():
                data, name = fetch_from_link(link)
                source = link.strip()
            else:
                raise CVError("Please upload a CV file or paste a link first.")
            text = extract_text(data, name)
            result = analyze_cv(text, role)
            meta = {"file_name": name, "file_type": name.rsplit(".", 1)[-1].lower(), "file_size": len(data), "source_link": source}
            st.session_state.cv_current_id = cv_repo.save_analysis(meta, text, result)
        flash("CV analyzed and saved to your history.")
        st.rerun()
    except CVError as exc:
        st.error(str(exc))
    except Exception:  # keep the page alive on unexpected parser problems
        st.error("Something went wrong while analyzing this file. Please try another CV.")


def _open(analysis_id: int) -> None:
    st.session_state.cv_current_id = analysis_id


def _delete(analysis_id: int) -> None:
    cv_repo.delete_analysis(analysis_id)
    if st.session_state.get("cv_current_id") == analysis_id:
        st.session_state.cv_current_id = None
    flash("Analysis deleted.")


def render_upload_card() -> None:
    with st.container(key="card_cv_upload"):
        section_title("book", "Upload Your CV", "PDF or DOCX, up to 5 MB.")
        with st.container(key="cv_uploader"):
            upload = st.file_uploader("Drag and drop your CV here", type=["pdf", "docx"], accept_multiple_files=False,
                                      key=f"cv_file_{st.session_state.cv_uploader_key}",
                                      help="Supported formats: PDF, DOCX. Maximum size 5 MB.")
        too_big = upload is not None and upload.size > 5 * 1024 * 1024
        if upload is not None:
            ext = upload.name.rsplit(".", 1)[-1].upper()[:4]
            c1, c2 = st.columns([4, 1.3], vertical_alignment="center")
            c1.markdown(f'<div class="file-card"><div class="file-ico">{esc(ext)}</div><div>'
                        f'<div class="file-name">{esc(upload.name)}</div><div class="file-size">{format_size(upload.size)}</div></div></div>',
                        unsafe_allow_html=True)
            c2.button("Remove", icon=":material/close:", key="cv_remove", on_click=_remove_file, use_container_width=True)
            if too_big:
                st.error("File is too large. The maximum size is 5 MB.")
        link = st.text_input("Paste Your CV Link (optional)", placeholder="https://example.com/my-cv.pdf",
                             help="A direct download link to a PDF or DOCX. Used only if no file is uploaded.")
        role = st.selectbox("Target job role", ROLE_NAMES, index=ROLE_NAMES.index(default_role()), key="cv_role_pick")
        if st.button("Analyze CV", icon=":material/auto_awesome:", type="primary", key="cv_analyze",
                     use_container_width=True, disabled=too_big):
            _run_analysis(upload, link, role)
        st.markdown(f'<div class="protip">{icon("bulb", 22)}<div><b>Pro Tip</b><br>A well-structured CV gets better analysis '
                    'results. Use clear headings such as Education, Skills, Experience and Projects.</div></div>',
                    unsafe_allow_html=True)


def render_history() -> None:
    rows = cv_repo.list_analyses()
    with st.container(key="card_cv_history"):
        section_title("chart", "Previous Analyses", "Reopen or delete saved results.")
        if not rows:
            st.markdown('<div class="empty">No saved analyses yet. Your results will appear here.</div>', unsafe_allow_html=True)
            return
        current = st.session_state.get("cv_current_id")
        for r in rows[:10]:
            with st.container(key=f"item_cvh_{r['id']}"):
                st.markdown(f'<div class="hist-row"><div><div class="item-title">{esc(r["file_name"])}</div>'
                            f'<div class="item-meta">{esc(r["target_role"])} · {friendly_date(r["created_at"])}</div></div>'
                            f'<div class="hist-score">{r["score"]}</div></div>', unsafe_allow_html=True)
                a, b, _ = st.columns([1, 1, 1.4])
                a.button("Opened" if r["id"] == current else "Open", icon=":material/visibility:", key=f"cvh_open_{r['id']}",
                         on_click=_open, args=(r["id"],), disabled=r["id"] == current, use_container_width=True)
                with b.popover("Delete", icon=":material/delete:", use_container_width=True):
                    st.caption("Delete this analysis?")
                    st.button("Yes, delete", key=f"cvh_del_{r['id']}", type="primary", on_click=_delete, args=(r["id"],))
