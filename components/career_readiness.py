"""Career readiness: interactive Plotly donut + skill groups."""
import plotly.graph_objects as go_
import streamlit as st

from components.icons import icon
from data.sample_data import READINESS as R


def donut(score: int, label: str = "Readiness Score") -> go_.Figure:
    fig = go_.Figure(go_.Pie(values=[score, 100 - score], hole=0.78, sort=False, direction="clockwise",
                             marker=dict(colors=["#2F6FDE", "#E3EAF8"]), textinfo="none",
                             hovertemplate="%{value}%<extra></extra>", showlegend=False))
    fig.update_layout(margin=dict(t=4, b=4, l=4, r=4), height=200, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", annotations=[dict(
                          text=f"<b style='font-size:34px'>{score}%</b><br><span style='font-size:12px;color:#6B7A99'>{label}</span>",
                          showarrow=False, font=dict(color="#16233F"))])
    return fig


def render_career_readiness() -> None:
    with st.container(key="card_readiness"):
        st.markdown(f'<div class="sec-title">{icon("chart", 22)}Your Career Readiness</div>', unsafe_allow_html=True)
        left, right = st.columns([1, 1], vertical_alignment="center")
        left.plotly_chart(donut(R["score"]), use_container_width=True, config={"displayModeBar": False})
        right.markdown(f'<div class="win"><div class="trophy">{icon("trophy", 38, stroke=1.5)}</div>'
                       f'<h4>{R["message_title"]}</h4><div class="metric-note">{R["message"]}</div></div>',
                       unsafe_allow_html=True)
        a, m, d = st.columns(3)
        for col, label, key in ((a, "Available", "available"), (m, "Missing", "missing"), (d, "Advanced", "advanced")):
            with col.popover(f"{len(R[key])} {label}", use_container_width=True):
                st.markdown(f"**{label} skills**")
                st.markdown("\n".join(f"- {s}" for s in R[key]))
        st.markdown(f'<div class="tip">{icon("bulb", 26)}<div><b>Tip:</b> {R["tip"]}</div></div>',
                    unsafe_allow_html=True)
