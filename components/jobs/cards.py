"""Job cards, the job-details dialog and the Save Job action."""
from html import escape as esc
from typing import Optional

import streamlit as st

from components.career_readiness import donut
from components.profile.widgets import flash
from database import job_repository as job_repo
from services.job_matching import learn_hint
from utils.helpers import friendly_date

PALETTE = ["#2F6FDE", "#6A58D0", "#1F9466", "#D9921B", "#D2553E", "#2E9DB5", "#C77DA8"]


def _logo(company: str) -> str:
    color = PALETTE[sum(map(ord, company)) % len(PALETTE)]
    return f'<div class="logo" style="color:{color}">{esc(company[:1].upper())}</div>'


def salary_text(job: dict) -> str:
    return f"${job['salary_min']:,} – ${job['salary_max']:,} / month"


def posted_text(days: int) -> str:
    return "Posted today" if days <= 0 else "Posted yesterday" if days == 1 else f"Posted {days} days ago"


def _badges(items: list, cls: str = "", limit: Optional[int] = None) -> str:
    """Skill badges. Items are skill names or {'skill', 'via'} dicts (partial credit through a related skill)."""
    shown = items if limit is None else items[:limit]
    out = []
    for it in shown:
        if isinstance(it, dict):
            out.append(f'<span class="badge sug" title="Partial credit through {esc(it["via"])}">{esc(it["skill"])} ≈ {esc(it["via"])}</span>')
        else:
            out.append(f'<span class="badge {cls}">{esc(it)}</span>')
    if limit is not None and len(items) > limit:
        out.append(f'<span class="badge more">+ {len(items) - limit} more</span>')
    return "".join(out)


def _toggle_save(job_id: str, title: str) -> None:
    now_saved = job_repo.toggle_saved(job_id)
    flash(f"Saved “{title}”." if now_saved else f"Removed “{title}” from saved jobs.")


def breakdown_html(components: list) -> str:
    rows = []
    for c in components:
        if c["used"]:
            rows.append(f'<div class="jm-comp"><div class="ov-bar-head"><span>{esc(c["label"])}</span>'
                        f'<b>{c["pct"]}% · {c["points"]:g}/{c["weight"]:g} pts</b></div>'
                        f'<div class="bar"><i style="width:{c["pct"]}%"></i></div>'
                        f'<div class="item-meta">{esc(c["note"])}</div></div>')
        else:
            rows.append(f'<div class="jm-comp off"><div class="ov-bar-head"><span>{esc(c["label"])}</span><b>Not included</b></div>'
                        f'<div class="bar"><i style="width:0%"></i></div><div class="item-meta">{esc(c["note"])}</div></div>')
    return "".join(rows)


def _empty_none() -> str:
    return '<span class="item-meta">None</span>'


# ------------------------------------------------------------------------------------------ dialog
@st.dialog("Job details", width="large")
def job_dialog(r: dict, saved: bool) -> None:
    j = r["job"]
    st.markdown(f'<div class="jm-head">{_logo(j["company"])}<div><div class="item-title" style="font-size:1.25rem">{esc(j["title"])}</div>'
                f'<div class="item-meta">{esc(j["company"])} • {esc(j["city"])}, {esc(j["country"])} • {esc(j["work_type"])}</div></div>'
                f'<span class="match {r["tier"]}">{r["score"]}% Match</span></div>', unsafe_allow_html=True)
    a, b = st.columns([1, 1.5], vertical_alignment="center")
    a.plotly_chart(donut(r["score"], "Compatibility"), use_container_width=True, config={"displayModeBar": False},
                   key=f"jm_donut_{j['id']}")
    with b:
        st.markdown(f'<div class="score-label">{esc(r["label"])}</div>'
                    f'<div class="item-desc">{esc(j["summary"])}</div>'
                    f'<div class="jm-chips"><span class="chip">{esc(j["employment_type"])}</span><span class="chip">{esc(j["level"])}</span>'
                    f'<span class="chip">{esc(salary_text(j))}</span><span class="chip soft">{esc(posted_text(j["posted_days"]))}</span></div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="cat">Match score breakdown</div>' + breakdown_html(r["components"]), unsafe_allow_html=True)
    st.markdown(f'<div class="disclaimer">Calculated from your profile and CV by comparing them with this job\'s requirements. '
                'It is an estimate of fit, not the probability of being hired.</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="cat">Matching skills · {len(r["matched_required"]) + len(r["matched_preferred"])}</div>'
                f'<div class="skills">{_badges(r["matched_required"] + r["matched_preferred"], "ok") or _empty_none()}</div>'
                f'<div class="cat">Missing required skills · {len(r["missing_required"])}</div>'
                f'<div class="skills">{_badges(r["missing_required"], "miss") or _empty_none()}</div>'
                f'<div class="cat">Missing preferred skills · {len(r["missing_preferred"])}</div>'
                f'<div class="skills">{_badges(r["missing_preferred"], "miss") or _empty_none()}</div>', unsafe_allow_html=True)
    related = r["related_required"] + r["related_preferred"]
    if related:
        st.markdown(f'<div class="cat">Partly covered by related skills</div><div class="skills">{_badges(related)}</div>'
                    '<div class="item-meta">Related skills earn half credit toward the requirement.</div>', unsafe_allow_html=True)

    resp = "".join(f"<li>{esc(x)}</li>" for x in j["responsibilities"])
    exp_txt = "No experience required" if not j["min_years"] else "{:g}+ year(s)".format(j["min_years"])
    st.markdown(f'<div class="cat">Responsibilities</div><ul class="fb">{resp}</ul>'
                f'<div class="cat">Requirements</div><div class="kv-grid">'
                f'<div class="kv"><span>Education</span><b>{esc(j["education"])} (or equivalent)</b></div>'
                f'<div class="kv"><span>Experience</span><b>{exp_txt}</b></div>'
                f'<div class="kv"><span>Industry</span><b>{esc(j["industry"])}</b></div>'
                f'<div class="kv"><span>Work type</span><b>{esc(j["work_type"])}</b></div></div>', unsafe_allow_html=True)

    gaps = r["missing_required"][:3]
    if gaps:
        tips = "".join(f"<li><b>{esc(s)}:</b> {esc(learn_hint(s))}</li>" for s in gaps)
        st.markdown(f'<div class="cat">How to close the gap</div><ul class="fb rec">{tips}</ul>', unsafe_allow_html=True)

    if st.button("Saved ✓ (click to remove)" if saved else "Save job", icon=":material/bookmark:", key=f"jm_dlg_save_{j['id']}",
                 type="primary" if saved else "secondary", use_container_width=True):
        _toggle_save(j["id"], j["title"])
        st.rerun()


# ------------------------------------------------------------------------------------------ card
def render_job_card(r: dict, saved: bool, prefix: str, note: str = "") -> None:
    j = r["job"]
    matched = r["matched_required"] + r["matched_preferred"]
    with st.container(key=f"card_jm_job_{prefix}_{j['id']}"):
        st.markdown(
            f'<div class="job">{_logo(j["company"])}<div><div class="job-title">{esc(j["title"])}</div>'
            f'<div class="job-meta">{esc(j["company"])} • {esc(j["city"])}, {esc(j["country"])}</div></div>'
            f'<span class="match {r["tier"]}">{r["score"]}% Match</span></div>'
            f'<div class="jm-chips"><span class="chip">{esc(j["work_type"])}</span><span class="chip">{esc(j["employment_type"])}</span>'
            f'<span class="chip">{esc(j["level"])}</span><span class="chip">{esc(salary_text(j))}</span>'
            f'<span class="chip soft">{esc(posted_text(j["posted_days"]))}</span></div>'
            f'<div class="jm-bar-row"><span>{esc(r["label"])}</span><div class="bar"><i style="width:{r["score"]}%"></i></div>'
            f'<span>{len(r["matched_required"])}/{len(j["required"])} required skills</span></div>'
            f'<div class="jm-label">Matching skills</div><div class="jm-skills">{_badges(matched, "ok", 6) or _empty_none()}</div>'
            f'<div class="jm-label">Missing required skills</div>'
            f'<div class="jm-skills">{_badges(r["missing_required"], "miss", 4) if r["missing_required"] else "<span class=item-meta>None – you have every required skill</span>"}</div>'
            + (f'<div class="item-meta" style="margin-top:.5rem">{esc(note)}</div>' if note else ""), unsafe_allow_html=True)
        a, b, _ = st.columns([1.1, 1, 1.6])
        if a.button("View Details", icon=":material/visibility:", key=f"jm_{prefix}_view_{j['id']}", use_container_width=True):
            job_dialog(r, saved)
        b.button("Saved" if saved else "Save Job", icon=":material/bookmark:" if saved else ":material/bookmark_border:",
                 key=f"jm_{prefix}_save_{j['id']}", type="primary" if saved else "secondary", use_container_width=True,
                 on_click=_toggle_save, args=(j["id"], j["title"]))


def saved_note(saved_at: str) -> str:
    return f"Saved on {friendly_date(saved_at)}"
