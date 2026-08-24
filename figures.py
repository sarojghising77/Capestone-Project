
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

NAVY = "#102A43"
CRIMSON = "#C1123F"
GOLD = "#C89B3C"
SLATE = "#62748A"
LIGHT = "#EEF2F7"


def empty_fig(message="No usable data available"):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5, y=0.5, xref="paper", yref="paper",
        showarrow=False, font=dict(size=15, color=SLATE)
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=20))
    return fig


def base(fig, height=390):
    fig.update_layout(
        height=height,
        margin=dict(l=15, r=30, t=20, b=45),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Inter, Arial", color="#1C2536"),
        legend=dict(orientation="h", y=1.08, x=0),
        hovermode="y unified",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E7E9EE", zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


def fig_stage(stage):
    fw, tw = stage["fw"], stage["tw"]
    if len(fw) == 0 and len(tw) == 0:
        return empty_fig("Purchase journey data is unavailable.")

    labels = [
        "Owns a vehicle",
        "Buying within 12 months",
        "Buying in 1–3 years",
        "Previously owned",
        "No immediate plans",
    ]

    def val(series, phrase):
        for k, v in series.items():
            if phrase.lower() in str(k).lower():
                return float(v)
        return 0

    fw_vals = [
        val(fw, "currently own"),
        val(fw, "within the next 12 months"),
        val(fw, "next 1–3 years"),
        val(fw, "owned"),
        val(fw, "no immediate plans"),
    ]
    tw_vals = [
        val(tw, "currently own"),
        val(tw, "within the next 12 months"),
        val(tw, "next 1–3 years"),
        0,
        0,
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Four-wheeler", y=labels, x=fw_vals, orientation="h",
                         marker_color=NAVY, text=[f"{x:.0f}%" for x in fw_vals],
                         textposition="outside"))
    fig.add_trace(go.Bar(name="Two-wheeler", y=labels, x=tw_vals, orientation="h",
                         marker_color=CRIMSON, text=[f"{x:.0f}%" for x in tw_vals],
                         textposition="outside"))
    fig.update_layout(barmode="group", xaxis_title="Share of respondents (%)",
                      yaxis_title="", xaxis_range=[0, 45])
    return base(fig, 410)


def fig_categorical_compare(fw, tw, title=None, topn=8):
    if len(fw) == 0 and len(tw) == 0:
        return empty_fig("No usable responses available.")

    keys = list(dict.fromkeys(list(fw.index) + list(tw.index)))
    keys = sorted(keys, key=lambda k: max(float(fw.get(k, 0)), float(tw.get(k, 0))), reverse=True)[:topn]
    keys = list(reversed(keys))

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Four-wheeler", y=keys, x=[fw.get(k, 0) for k in keys],
                         orientation="h", marker_color=NAVY,
                         text=[f"{fw.get(k,0):.0f}%" for k in keys], textposition="outside"))
    fig.add_trace(go.Bar(name="Two-wheeler", y=keys, x=[tw.get(k, 0) for k in keys],
                         orientation="h", marker_color=CRIMSON,
                         text=[f"{tw.get(k,0):.0f}%" for k in keys], textposition="outside"))
    fig.update_layout(barmode="group", xaxis_title="Share of respondents (%)", yaxis_title="")
    return base(fig, max(350, 55 * len(keys)))


def fig_brand(series, color, topn=8):
    if len(series) == 0:
        return empty_fig("Brand preference data is unavailable.")
    s = series.head(topn).sort_values()
    fig = go.Figure(go.Bar(
        y=[str(x) for x in s.index], x=s.values, orientation="h",
        marker_color=color, text=[f"{x:.1f}%" for x in s.values], textposition="outside"
    ))
    fig.update_layout(xaxis_title="Share of respondents (%)", yaxis_title="")
    return base(fig, max(350, 48 * len(s)))


def fig_ev_rate(ev):
    fw, tw = ev["fw"], ev["tw"]
    labels = ["Four-wheeler", "Two-wheeler"]
    vals = [fw.get("Yes", 0), tw.get("Yes", 0)]
    fig = go.Figure(go.Bar(
        x=labels, y=vals, marker_color=[NAVY, CRIMSON],
        text=[f"{x:.0f}%" for x in vals], textposition="outside"
    ))
    fig.update_layout(yaxis_title="Share saying Yes (%)", yaxis_range=[0, 100], showlegend=False)
    return base(fig, 330)


def fig_ranked_compare(fw, tw, rank_max, topn=6):
    if len(fw) == 0 and len(tw) == 0:
        return empty_fig("Ranking data is unavailable.")

    # Convert average rank to a 0–100 priority index. Higher = more important.
    def idx(s):
        return ((rank_max - s) / max(rank_max - 1, 1) * 100).round(1)

    fi, ti = idx(fw), idx(tw)
    keys = list(dict.fromkeys(list(fi.index) + list(ti.index)))
    keys = sorted(keys, key=lambda k: max(float(fi.get(k, 0)), float(ti.get(k, 0))), reverse=True)[:topn]
    keys = list(reversed(keys))

    def short(x):
        x = str(x)
        replacements = {
            "Family members": "Family members",
            "Friends/Relatives": "Friends & relatives",
            "Social media": "Social media",
            "YouTube": "YouTube / vehicle reviews",
            "Online reviews": "Online reviews",
            "Automobile websites": "Automobile websites",
            "Dealer showroom": "Dealer showroom",
            "Newspaper/Magazine": "Newspaper / magazine",
            "Auto exhibitions/events": "Auto exhibitions / events",
            "High taxes/import duties": "Taxes / import duties",
            "Limited financing options": "Limited financing",
            "Limited vehicle availability": "Limited model availability",
            "Charging infrastructure (for EVs)": "Charging infrastructure",
            "Lower running costs": "Lower running costs",
            "Better charging infrastructure": "Better charging infrastructure",
            "Environmentally friendly (Hybrid/EV)": "Eco-friendly / EV",
            "Innovative technology": "Smart technology",
        }
        return replacements.get(x, x)

    labels = [short(x) for x in keys]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Four-wheeler", y=labels, x=[fi.get(k, 0) for k in keys],
                         orientation="h", marker_color=NAVY,
                         text=[f"{fi.get(k,0):.0f}" if k in fi else "—" for k in keys],
                         textposition="outside",
                         customdata=[fw.get(k, np.nan) for k in keys],
                         hovertemplate="%{y}<br>Priority index: %{x:.1f}<br>Average rank: %{customdata:.2f}<extra>Four-wheeler</extra>"))
    fig.add_trace(go.Bar(name="Two-wheeler", y=labels, x=[ti.get(k, 0) for k in keys],
                         orientation="h", marker_color=CRIMSON,
                         text=[f"{ti.get(k,0):.0f}" if k in ti else "—" for k in keys],
                         textposition="outside",
                         customdata=[tw.get(k, np.nan) for k in keys],
                         hovertemplate="%{y}<br>Priority index: %{x:.1f}<br>Average rank: %{customdata:.2f}<extra>Two-wheeler</extra>"))
    fig.update_layout(
        barmode="group",
        xaxis_title="Priority index (higher = more important)",
        yaxis_title="",
        xaxis_range=[0, 115],
    )
    return base(fig, max(390, 58 * len(keys)))


def fig_demographics(demo):
    categories = ["Age", "Gender", "Income", "Occupation"]
    fig = make_subplots(rows=2, cols=2, subplot_titles=categories, vertical_spacing=0.18, horizontal_spacing=0.12)
    for i, cat in enumerate(categories):
        row, col = divmod(i, 2)
        fw, tw = demo["fw"][cat], demo["tw"][cat]
        keys = list(dict.fromkeys(list(fw.index) + list(tw.index)))
        keys = sorted(keys, key=lambda k: max(fw.get(k,0), tw.get(k,0)), reverse=True)[:7]
        keys = list(reversed(keys))
        fig.add_trace(go.Bar(name="Four-wheeler", y=[str(k) for k in keys], x=[fw.get(k,0) for k in keys],
                             orientation="h", marker_color=NAVY, showlegend=(i==0)), row=row+1, col=col+1)
        fig.add_trace(go.Bar(name="Two-wheeler", y=[str(k) for k in keys], x=[tw.get(k,0) for k in keys],
                             orientation="h", marker_color=CRIMSON, showlegend=(i==0)), row=row+1, col=col+1)
        fig.update_xaxes(title_text="%", row=row+1, col=col+1, showgrid=True, gridcolor="#E7E9EE")
    fig.update_layout(barmode="group", height=760, margin=dict(l=20,r=20,t=55,b=25),
                      paper_bgcolor="white", plot_bgcolor="white",
                      font=dict(family="Inter, Arial", color="#1C2536"))
    return fig
