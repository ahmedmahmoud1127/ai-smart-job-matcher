"""Right-hand column: the data used for matching and the personalised 'skills to learn' advice."""
from html import escape as esc

import streamlit as st

from components.icons import icon
from components.navbar import go
from components.profile.widgets import section_title
from utils.helpers import friendly_date

SKILL_PREVIEW = 14


def _set_search(skill: str) -> None:
    st.session_state.update({"jm_search": skill, "jm_work": "All", "jm_emp": "All", "jm_level": "All", "jm_city": "All",
                             "jm_role": "All", "jm_min": 0, "jm_limit": 8})


def render_profile_card(cand: dict) -> None:
    skills = sorted(cand["skills"].items(), key=lambda kv: (-kv[1]["credit"], kv[0]))
    edu, exp, prefs, cv = cand["education"], cand["experience"], cand["preferences"], cand["cv"]
    with st.container(key="card_jm_profile"):
        section_title("layers", "Your Match Profile", "Built from My Profile and your latest CV analysis.")
        if skills:
            shown = "".join(f'<span class="badge ok" title="{esc(", ".join(v["sources"]))}">{esc(n)}</span>'
                            for n, v in skills[:SKILL_PREVIEW])
            more = f'<span class="badge more">+ {len(skills) - SKILL_PREVIEW} more</span>' if len(skills) > SKILL_PREVIEW else ""
            st.markdown(f'<div class="cat">Skills · {len(skills)}</div><div class="skills">{shown}{more}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty">No skills yet. Add skills in My Profile or analyze your CV to get accurate matches.</div>',
                        unsafe_allow_html=True)
        if edu:
            line = " · ".join(esc(x) for x in (edu["degree"], edu["major"], edu["university"]) if x) or "Education found"
            edu_txt = line + (" (studying)" if edu["in_progress"] else "")
        else:
            edu_txt = "Not added yet"
        exp_txt = (f'about {exp["years"]:g} year(s) · {exp["positions"]} position(s), {exp["projects"]} project(s)'
                   if exp["years"] or exp["positions"] or exp["projects"] else "None added yet")
        pref_bits = [p for p in (prefs.get("effective_role"), prefs.get("work_type"), prefs.get("employment_type")) if p]
        cv_txt = f'{esc(cv["file_name"])} · {friendly_date(cv["created_at"])}' if cv else "No CV analyzed yet"
        st.markdown('<div class="kv-grid" style="grid-template-columns:1fr;gap:.55rem">'
                    f'<div class="kv"><span>Education</span><b>{edu_txt}</b></div>'
                    f'<div class="kv"><span>Experience</span><b>{exp_txt}</b></div>'
                    f'<div class="kv"><span>Career preferences</span><b>{esc(" · ".join(pref_bits)) if pref_bits else "Not set"}</b></div>'
                    f'<div class="kv"><span>CV analysis used</span><b>{cv_txt}</b></div></div>', unsafe_allow_html=True)
        a, b = st.columns(2)
        a.button("My Profile", icon=":material/person:", key="jm_go_profile", on_click=go, args=("My Profile",), use_container_width=True)
        b.button("CV Analyzer", icon=":material/description:", key="jm_go_cv", on_click=go, args=("CV Analyzer",), use_container_width=True)


def render_skill_recs(rec: dict) -> None:
    skills, proj = rec["skills"], rec["projection"]
    with st.container(key="card_jm_learn"):
        section_title("bulb", "Skills to Learn Next", "Ranked by how much each skill would raise your real match scores.")
        if not skills:
            st.markdown('<div class="empty">Great news: no skill gaps found for your best-fitting jobs. Keep your profile up to date.</div>',
                        unsafe_allow_html=True)
            return
        if proj and (proj["avg_after"] > proj["avg_before"] or proj["strong_after"] > proj["strong_before"]):
            names = ", ".join(proj["skills"][:-1]) + (" and " if len(proj["skills"]) > 1 else "") + proj["skills"][-1]
            extra = f' and give you <b>{proj["strong_after"] - proj["strong_before"]}</b> more strong match(es)' \
                if proj["strong_after"] > proj["strong_before"] else ""
            st.markdown(f'<div class="tip">{icon("bulb", 26)}<div>Learning <b>{esc(names)}</b> could lift your average top-5 match from '
                        f'<b>{proj["avg_before"]:g}%</b> to <b>{proj["avg_after"]:g}%</b>{extra}.</div></div>', unsafe_allow_html=True)
        for i, s in enumerate(skills):
            with st.container(key=f"item_jm_learn_{i}"):
                unlock = f" · unlocks {s['unlocked']} strong match(es)" if s["unlocked"] else ""
                st.markdown(
                    f'<div class="jm-learn-top"><div class="item-title">{i + 1}. {esc(s["skill"])}</div>'
                    f'<span class="jm-gain">+{s["avg_gain"]:g}% avg match</span></div>'
                    f'<div class="item-meta">Improves {s["jobs"]} of your top jobs ({s["required_in"]} require it){unlock}</div>'
                    f'<div class="jm-hint">{esc(s["hint"])}</div>'
                    f'<div class="item-meta" style="margin-top:.3rem">Helps with: {esc(", ".join(s["top_jobs"]))}</div>', unsafe_allow_html=True)
                st.button("Show jobs needing this", icon=":material/search:", key=f"jm_learn_filter_{i}",
                          on_click=_set_search, args=(s["skill"],))
        st.markdown('<div class="disclaimer">Gains are calculated by re-scoring your best-fitting jobs as if you had learned each '
                    'skill to an intermediate level.</div>', unsafe_allow_html=True)
