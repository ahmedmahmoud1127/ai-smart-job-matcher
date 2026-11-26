"""Which user is the app working for?

Every repository/service function takes ``user_id``. When the caller doesn't pass one, it is resolved here:
the signed-in user of the current Streamlit session, or the seeded sample user outside Streamlit (tests, scripts).
"""
from database.db import SAMPLE_USER_ID


def resolve_user_id(user_id: int | None = None) -> int:
    if user_id is not None:
        return user_id
    try:
        import streamlit as st
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx(suppress_warning=True) is None:  # not running inside a Streamlit session
            return SAMPLE_USER_ID
        current = st.session_state.get("user_id")
    except Exception:
        current = None
    return current if current is not None else SAMPLE_USER_ID
