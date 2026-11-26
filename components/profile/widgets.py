"""Reusable CRUD section used by Education, Skills, Experience, Projects and Languages."""
from datetime import date
from html import escape as esc
from typing import Callable, Optional

import streamlit as st

from components.icons import icon
from database import repository as repo

LEVEL_ORDER = ["Beginner", "Intermediate", "Advanced", "Expert", "Native"]


def flash(message: str, kind: str = "success") -> None:
    """Queue a notification to show after the next rerun."""
    st.session_state.setdefault("flash", []).append((kind, message))


def show_flash() -> None:
    for kind, msg in st.session_state.pop("flash", []):
        (st.toast(msg, icon="✅") if kind == "success" else st.toast(msg, icon="⚠️"))


def section_title(icon_name: str, text: str, sub: str = "") -> None:
    st.markdown(f'<div class="sec-title">{icon(icon_name, 22)}{text}</div>'
                + (f'<div class="sec-sub">{sub}</div>' if sub else ""), unsafe_allow_html=True)


def _to_date(v: str) -> date:
    try:
        return date.fromisoformat(v)
    except (TypeError, ValueError):
        return date.today()


def render_fields(fields: list, values: dict, prefix: str) -> dict:
    """Draw form widgets from a field spec and return the entered values."""
    out, halves = {}, [f for f in fields if not f.get("full")]
    cols = None
    for i, f in enumerate(halves + [f for f in fields if f.get("full")]):
        if f in halves:
            if i % 2 == 0:
                cols = st.columns(2)
            target = cols[i % 2]
        else:
            target = st
        key, cur, kind, label = f"{prefix}_{f['name']}", values.get(f["name"]), f.get("kind", "text"), f["label"]
        label = label + (" *" if f.get("required") else "")
        if kind == "select":
            opts = f["options"]
            out[f["name"]] = target.selectbox(label, opts, index=opts.index(cur) if cur in opts else 0, key=key)
        elif kind == "textarea":
            out[f["name"]] = target.text_area(label, value=cur or "", placeholder=f.get("placeholder", ""), key=key, height=90)
        elif kind == "year":
            out[f["name"]] = int(target.number_input(label, 1990, 2045, int(cur or date.today().year), 1, key=key))
        elif kind == "date":
            out[f["name"]] = target.date_input(label, _to_date(cur), date(1990, 1, 1), date(2045, 12, 31), key=key).isoformat()
        elif kind == "date_opt":
            ongoing = target.checkbox(f.get("ongoing_label", "Ongoing"), value=not cur and bool(values), key=key + "_on")
            d = target.date_input(label, _to_date(cur), date(1990, 1, 1), date(2045, 12, 31), key=key)
            out[f["name"]] = "" if ongoing else d.isoformat()
        elif kind == "float_opt":
            raw = target.text_input(label, value="" if cur is None else str(cur), placeholder=f.get("placeholder", ""), key=key)
            out[f["name"]] = raw.strip()
        else:
            out[f["name"]] = target.text_input(label, value=cur or "", placeholder=f.get("placeholder", ""), key=key).strip()
    return out


def crud_section(*, table: str, prefix: str, title: str, icon_name: str, subtitle: str, fields: list,
                 render_item: Callable[[dict], str], add_label: str, empty_text: str,
                 validate: Optional[Callable[[dict, Optional[dict]], list]] = None,
                 grid_cols: int = 1, quick: Optional[tuple] = None, noun: str = "item") -> None:
    """quick = (field, options) adds an inline selectbox to change one field instantly."""
    mode_key = f"{prefix}_mode"
    st.session_state.setdefault(mode_key, None)
    rows = repo.list_rows(table)
    mode = st.session_state[mode_key]

    with st.container(key=f"card_prof_{prefix}"):
        head, btn = st.columns([3, 1.3], vertical_alignment="center")
        with head:
            section_title(icon_name, title, subtitle)
        btn.button(add_label, icon=":material/add:", key=f"{prefix}_add", use_container_width=True,
                   on_click=lambda: st.session_state.update({mode_key: "new"}))

        if mode is not None:
            current = next((r for r in rows if r["id"] == mode), None) if mode != "new" else None
            if mode != "new" and current is None:
                st.session_state[mode_key] = None
                st.rerun()
            with st.form(f"{prefix}_form_{mode}"):
                st.markdown(f"**{'Add' if current is None else 'Edit'} {noun}**")
                data = render_fields(fields, current or {}, f"{prefix}_{mode}")
                c1, c2, _ = st.columns([1, 1, 3])
                saved = c1.form_submit_button("Save", type="primary", use_container_width=True)
                cancel = c2.form_submit_button("Cancel", use_container_width=True)
            if cancel:
                st.session_state[mode_key] = None
                st.rerun()
            if saved:
                errors = [f"{f['label']} is required." for f in fields if f.get("required") and not str(data[f["name"]]).strip()]
                errors += (validate(data, current) if validate and not errors else [])
                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    try:
                        if current is None:
                            repo.insert_row(table, data)
                        else:
                            repo.update_row(table, current["id"], data)
                    except repo.DuplicateError:
                        st.error(f"This {noun} already exists.")
                    else:
                        flash(f"{noun.capitalize()} {'added' if current is None else 'updated'}.")
                        st.session_state[mode_key] = None
                        st.rerun()

        if not rows:
            st.markdown(f'<div class="empty">{empty_text}</div>', unsafe_allow_html=True)
            return
        cols = st.columns(grid_cols) if grid_cols > 1 else None
        for i, row in enumerate(rows):
            holder = cols[i % grid_cols] if cols else st
            with holder.container(key=f"item_{prefix}_{row['id']}"):
                st.markdown(render_item(row), unsafe_allow_html=True)
                if quick:
                    field, opts = quick
                    qk = f"q_{prefix}_{row['id']}_{row[field]}"
                    st.selectbox(field, opts, index=opts.index(row[field]) if row[field] in opts else 0, key=qk,
                                 label_visibility="collapsed", on_change=_quick_update,
                                 args=(table, row["id"], field, qk, noun))
                a, b, _ = st.columns([1, 1, 1.2 if grid_cols > 1 else 4])
                a.button("Edit", icon=":material/edit:", key=f"{prefix}_edit_{row['id']}", use_container_width=True,
                         on_click=lambda rid=row["id"]: st.session_state.update({mode_key: rid}))
                with b.popover("Delete", icon=":material/delete:", use_container_width=True):
                    st.caption(f"Delete this {noun}?")
                    st.button("Yes, delete", key=f"{prefix}_del_{row['id']}", type="primary",
                              on_click=_delete, args=(table, row["id"], noun, mode_key))


def _quick_update(table: str, rid: int, field: str, key: str, noun: str) -> None:
    repo.update_row(table, rid, {field: st.session_state[key]})
    flash(f"{noun.capitalize()} {field} updated.")


def _delete(table: str, rid: int, noun: str, mode_key: str) -> None:
    repo.delete_row(table, rid)
    st.session_state[mode_key] = None
    flash(f"{noun.capitalize()} deleted.")
