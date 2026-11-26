"""Plotly figures for the Analytics Dashboard. Pure functions: data in, figure out (no Streamlit, no database)."""
import plotly.graph_objects as go_

INK, MUTED, GRID = "#16233F", "#6B7A99", "#E3EAF8"
COLORS = {"current": "#5E92EC", "acquired": "#3FB07F", "missing": "#EBB45A", "lav": "#8A79DB", "blue": "#2F6FDE"}
SERIES = [("Current", "current", "current_names"), ("Acquired", "acquired", "acquired_names"), ("Missing", "missing", "missing_names")]


def _base(fig: go_.Figure, height: int, **layout) -> go_.Figure:
    fig.update_layout(height=height, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Plus Jakarta Sans, system-ui, sans-serif", color=INK, size=12),
                      hoverlabel=dict(bgcolor="white", bordercolor=GRID, font=dict(color=INK, size=12)), **layout)
    return fig


def _names(names: list, limit: int = 8) -> str:
    if not names:
        return "–"
    return "<br>".join(names[:limit]) + (f"<br>+ {len(names) - limit} more" if len(names) > limit else "")


def skills_by_category(groups: list, show: str = "All") -> go_.Figure:
    """Horizontal grouped bars: current / acquired / missing skills per category. `show` picks one series or All."""
    fig = go_.Figure()
    order = list(reversed([g["group"] for g in groups]))
    by_group = {g["group"]: g for g in groups}
    for label, key, names_key in SERIES:
        if show not in ("All", label):
            continue
        fig.add_bar(name=label, y=order, x=[by_group[g][key] for g in order], orientation="h", marker=dict(color=COLORS[key], cornerradius=6),
                    customdata=[_names(by_group[g][names_key]) for g in order],
                    hovertemplate=f"<b>%{{y}}</b><br>{label}: %{{x}}<br>%{{customdata}}<extra></extra>")
    top = max([g[k] for g in groups for _, k, _ in SERIES] or [1])
    _base(fig, max(260, 62 * len(groups) + 40), barmode="group", bargap=0.35, bargroupgap=0.08,
          legend=dict(orientation="h", y=1.08, x=0, font=dict(size=12)),
          xaxis=dict(gridcolor=GRID, zeroline=False, dtick=1 if top <= 8 else None, range=[0, top + 0.6], title=dict(text="Number of skills", font=dict(color=MUTED, size=11))),
          yaxis=dict(showgrid=False, automargin=True))
    return fig


def weekly_hours(weekly: list) -> go_.Figure:
    """Hours per day for the last 7 days; today's bar is the strongest colour."""
    labels = [w["label"] for w in weekly]
    top = max([w["hours"] for w in weekly] + [1])
    fig = go_.Figure(go_.Bar(
        x=labels, y=[w["hours"] for w in weekly], text=[f"{w['hours']:g} h" if w["hours"] else "" for w in weekly], textposition="outside",
        marker=dict(color=[COLORS["blue"] if i == len(weekly) - 1 else "#9DBAF2" for i in range(len(weekly))], cornerradius=8),
        customdata=[[w["full"], w["tasks"], ", ".join(w["skills"][:4]) or "–"] for w in weekly],
        hovertemplate="<b>%{customdata[0]}</b><br>%{y} h estimated<br>Skills completed: %{customdata[1]}<br>%{customdata[2]}<extra></extra>"))
    _base(fig, 250, bargap=0.4, xaxis=dict(showgrid=False, fixedrange=True), yaxis=dict(gridcolor=GRID, zeroline=False, range=[0, top * 1.25], fixedrange=True,
          title=dict(text="Hours", font=dict(color=MUTED, size=11))), showlegend=False)
    return fig


def activity_heatmap(h: dict) -> go_.Figure:
    top = h["max"] or 1
    fig = go_.Figure(go_.Heatmap(z=h["z"], x=h["weeks"], y=h["days"], text=h["text"], xgap=4, ygap=4, showscale=False, zmin=0, zmax=top,
                                 colorscale=[[0, "#ECF1FB"], [0.001, "#C9DBF8"], [0.5, "#7FA2EA"], [1, "#2F6FDE"]],
                                 hovertemplate="%{text}<br><b>%{z} h</b> estimated<extra></extra>", hoverongaps=False))
    _base(fig, 250, xaxis=dict(showgrid=False, side="bottom", fixedrange=True, title=dict(text="Week starting", font=dict(color=MUTED, size=11))),
          yaxis=dict(showgrid=False, autorange="reversed", fixedrange=True))
    return fig


def top_jobs(top: list) -> go_.Figure:
    """Horizontal bars of the best job matches, coloured by match tier."""
    rows = list(reversed(top))
    tier = lambda s: COLORS["acquired"] if s >= 75 else COLORS["current"] if s >= 50 else COLORS["missing"]
    fig = go_.Figure(go_.Bar(
        x=[r["score"] for r in rows], y=[(r["title"] if len(r["title"]) <= 28 else r["title"][:27] + "…") for r in rows], orientation="h", marker=dict(color=[tier(r["score"]) for r in rows], cornerradius=6),
        text=[f"{r['score']}%" for r in rows], textposition="outside", cliponaxis=False,
        customdata=[[r["company"], r["label"], r["title"]] for r in rows],
        hovertemplate="<b>%{customdata[2]}</b> · %{customdata[0]}<br>%{x}% · %{customdata[1]}<extra></extra>"))
    _base(fig, max(240, 34 * len(rows) + 40), bargap=0.35, xaxis=dict(range=[0, 112], gridcolor=GRID, zeroline=False, fixedrange=True),
          yaxis=dict(showgrid=False, automargin=True, fixedrange=True), showlegend=False)
    return fig


def _line_fig(x: list, series: list, height: int, y_title: str = "") -> go_.Figure:
    fig = go_.Figure()
    for name, ys, color, extra in series:
        fig.add_scatter(x=x, y=ys, name=name, mode="lines+markers", line=dict(color=color, width=3, shape="spline", smoothing=0.6),
                        marker=dict(size=8, color="white", line=dict(color=color, width=2.5)), customdata=extra,
                        hovertemplate=f"<b>{name}</b><br>%{{x}}<br>%{{y}}{y_title}%{{customdata}}<extra></extra>")
    _base(fig, height, xaxis=dict(showgrid=False, type="category"), yaxis=dict(range=[0, 100], gridcolor=GRID, zeroline=False),
          legend=dict(orientation="h", y=1.12, x=0))
    return fig


def match_history(history: list) -> go_.Figure:
    x = [s["snap_date"] for s in history]
    blank = [""] * len(x)
    return _line_fig(x, [("Best match", [s["best_match"] for s in history], COLORS["acquired"], blank),
                         ("Top-5 average", [s["top5_avg"] for s in history], COLORS["blue"], blank),
                         ("Average (all jobs)", [s["avg_match"] for s in history], COLORS["lav"], blank)], 260, "%")


def readiness_history(history: list) -> go_.Figure:
    x = [s["snap_date"] for s in history]
    fig = _line_fig(x, [("Career readiness", [s["readiness"] for s in history], COLORS["blue"], [""] * len(x))], 170, "%")
    fig.update_layout(showlegend=False, margin=dict(t=6, b=6, l=6, r=6))
    return fig


def cv_history(history: list) -> go_.Figure:
    x = [h["date"].strftime("%d %b") + f" #{i + 1}" for i, h in enumerate(history)]
    fig = _line_fig(x, [("CV score", [h["score"] for h in history], COLORS["lav"],
                         [f"<br>{h['file']} · {h['role']}" for h in history])], 190, "/100")
    fig.update_layout(showlegend=False)
    return fig
