
from pathlib import Path
import os
import html
import plotly.io as pio
import pandas as pd

from analysis import build_insights, priority_index
from figures import (
    NAVY, CRIMSON, GOLD, SLATE,
    fig_stage, fig_categorical_compare, fig_brand, fig_ev_rate,
    fig_ranked_compare, fig_demographics
)
from themes import tag_themes, sample_quotes

BASE = Path(__file__).resolve().parent
OUT_DIR = BASE / "dashboard_output"
OUT_DIR.mkdir(exist_ok=True)
OUT_PATH = OUT_DIR / "index.html"
PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.35.2.min.js"
CFG = {"displayModeBar": False, "responsive": True}


def div(fig, id_):
    return pio.to_html(fig, full_html=False, include_plotlyjs=False, config=CFG, div_id=id_)


def esc(x):
    return html.escape(str(x))


def top(series):
    if series is None or len(series) == 0:
        return "Data unavailable", 0
    return str(series.index[0]), float(series.iloc[0])


def section_insight(text):
    return f"""
    <div class="insight">
      <div class="insight-title">BUSINESS INSIGHT</div>
      <div class="insight-text">{esc(text)}</div>
    </div>
    """


def build():
    ins = build_insights()
    fw, tw = ins["fw"], ins["tw"]

    charts = {}
    charts["stage"] = div(fig_stage(ins["stage"]), "chart-stage")
    charts["purpose"] = div(fig_categorical_compare(ins["purpose"]["fw"], ins["purpose"]["tw"]), "chart-purpose")
    charts["vehicle_fw"] = div(fig_categorical_compare(ins["vehicle_type"]["fw"], pd.Series(dtype=float)), "chart-vt-fw")
    charts["vehicle_tw"] = div(fig_categorical_compare(pd.Series(dtype=float), ins["vehicle_type"]["tw"]), "chart-vt-tw")
    charts["brand_fw"] = div(fig_brand(ins["brand"]["fw"], NAVY), "chart-brand-fw")
    charts["brand_tw"] = div(fig_brand(ins["brand"]["tw"], CRIMSON), "chart-brand-tw")
    charts["brand_importance"] = div(fig_categorical_compare(ins["brand_importance"]["fw"], ins["brand_importance"]["tw"]), "chart-brand-importance")
    charts["brand_approach"] = div(fig_categorical_compare(ins["brand_approach"]["fw"], ins["brand_approach"]["tw"]), "chart-brand-approach")
    charts["ev_rate"] = div(fig_ev_rate(ins["ev_rate"]), "chart-ev-rate")
    charts["ev_drivers"] = div(fig_ranked_compare(ins["ev_drivers"]["fw"], ins["ev_drivers"]["tw"], 7), "chart-ev-drivers")
    charts["factors"] = div(fig_ranked_compare(ins["factors"]["fw"], ins["factors"]["tw"], 8), "chart-factors")
    charts["sources"] = div(fig_ranked_compare(ins["sources"]["fw"], ins["sources"]["tw"], 9), "chart-sources")
    charts["challenges"] = div(fig_ranked_compare(ins["challenges"]["fw"], ins["challenges"]["tw"], 10), "chart-challenges")
    charts["attributes"] = div(fig_ranked_compare(ins["attributes"]["fw"], ins["attributes"]["tw"], 11), "chart-attributes")
    charts["demographics"] = div(fig_demographics(ins["demographics"]), "chart-demographics")

    # Voice of market
    fw_text = fw["Q13. What makes brand trustworthy in Nepal (Open-ended)"]
    tw_text = tw["q19_market_feedback_suggestions"]
    fw_themes = tag_themes(fw_text) / max(len(fw), 1) * 100
    tw_themes = tag_themes(tw_text) / max(len(tw), 1) * 100
    charts["themes"] = div(
        fig_categorical_compare(fw_themes.round(1), tw_themes.round(1), topn=7),
        "chart-themes"
    )

    quotes_fw = sample_quotes(fw_text, 3)
    quotes_tw = sample_quotes(tw_text, 3)

    brand_fw, brand_fw_pct = top(ins["brand"]["fw"])
    brand_tw, brand_tw_pct = top(ins["brand"]["tw"])

    kpis = [
        ("Total respondents", f"{ins['total_n']}", f"{ins['fw_n']} four-wheeler · {ins['tw_n']} two-wheeler"),
        ("EV consideration", f"{(ins['ev_rate']['fw'].get('Yes',0)+ins['ev_rate']['tw'].get('Yes',0))/2:.0f}%",
         f"4W {ins['ev_rate']['fw'].get('Yes',0):.0f}% · 2W {ins['ev_rate']['tw'].get('Yes',0):.0f}%"),
        ("Buying within 12 months",
         f"{(ins['stage']['fw'].get('I plan to purchase a four-wheeler within the next 12 months.',0)+ins['stage']['tw'].get('I plan to purchase a two-wheeler within the next 12 months.',0))/2:.0f}%",
         "Near-term purchase intent"),
        ("Leading brands", f"{brand_fw} / {brand_tw}", f"{brand_fw_pct:.0f}% 4W · {brand_tw_pct:.0f}% 2W"),
    ]

    kpi_html = "".join(
        f'<div class="kpi"><div class="kpi-label">{esc(a)}</div>'
        f'<div class="kpi-value">{esc(b)}</div><div class="kpi-sub">{esc(c)}</div></div>'
        for a,b,c in kpis
    )

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nepal Vehicle Market — Buyer Insights Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
<script src="{PLOTLY_CDN}"></script>
<style>{CSS}</style>
</head>
<body>
<header class="topbar">
  <div class="flagbar"></div>
  <div class="topbar-inner">
    <div class="brand"><div class="brand-mark">NP</div>
      <div><div class="brand-title">Nepal Vehicle Market</div>
      <div class="brand-sub">Buyer Insights Dashboard · Four-Wheeler &amp; Two-Wheeler Survey 2026</div></div>
    </div>
    <nav class="topnav">
      <a href="#snapshot">Snapshot</a><a href="#journey">Journey</a><a href="#brands">Brands</a>
      <a href="#ev">EV</a><a href="#factors">Decision Factors</a><a href="#voice">Voice</a>
    </nav>
  </div>
</header>

<main>
<section class="hero" id="snapshot">
  <div class="eyebrow">Executive decision dashboard</div>
  <h1>What Nepal's vehicle buyers value — and what businesses should do next</h1>
  <p class="lede">A decision-focused view of {ins['fw_n']} four-wheeler and {ins['tw_n']} two-wheeler responses. Rankings are converted into a priority index so the most important issues are immediately visible.</p>
  <div class="kpi-row">{kpi_html}</div>
</section>

<section class="panel">
  <div class="panel-head"><span class="tag">Executive decisions</span></div>
  <div class="decision-grid">
    <div class="decision"><b>CONVERSION</b><span>Focus on buyers planning within 12 months.</span></div>
    <div class="decision"><b>EV</b><span>Sell practical ownership benefits, not only environmental benefits.</span></div>
    <div class="decision"><b>MARKETING</b><span>Prioritize the channels buyers actually use for research.</span></div>
    <div class="decision"><b>PRODUCT</b><span>Lead communication with the highest-ranked decision factors.</span></div>
  </div>
</section>

<section class="panel" id="journey">
  <div class="panel-head"><h2>Purchase journey stage</h2><p>Where respondents sit today. Empty stages are not fabricated; unavailable categories remain at zero.</p></div>
  <div class="chart-card full">{charts["stage"]}</div>
  {section_insight(ins["business_insights"]["journey"])}
</section>

<section class="panel">
  <div class="panel-head"><h2>Vehicle type &amp; purpose</h2><p>What buyers intend to use and the formats they prefer.</p></div>
  <div class="grid-2">
    <div class="chart-card"><h3>Four-wheeler type</h3>{charts["vehicle_fw"]}</div>
    <div class="chart-card"><h3>Two-wheeler type</h3>{charts["vehicle_tw"]}</div>
  </div>
  <div class="chart-card full"><h3>Primary purchase purpose</h3>{charts["purpose"]}</div>
</section>

<section class="panel" id="brands">
  <div class="panel-head"><h2>Brand preference</h2><p>Preferred brands by respondent share.</p></div>
  <div class="grid-2">
    <div class="chart-card"><h3>Four-wheeler</h3>{charts["brand_fw"]}</div>
    <div class="chart-card"><h3>Two-wheeler</h3>{charts["brand_tw"]}</div>
  </div>
  {section_insight(ins["business_insights"]["brands"])}
</section>

<section class="panel">
  <div class="panel-head"><h2>How buyers evaluate brands</h2><p>Brand importance and selection mindset.</p></div>
  <div class="grid-2">
    <div class="chart-card"><h3>Brand importance</h3>{charts["brand_importance"]}</div>
    <div class="chart-card"><h3>Brand selection approach</h3>{charts["brand_approach"]}</div>
  </div>
</section>

<section class="panel" id="ev">
  <div class="panel-head"><h2>EV outlook</h2><p>Willingness to consider EVs and the factors that could move interested buyers toward purchase.</p></div>
  <div class="grid-2">
    <div class="chart-card"><h3>Considering an EV</h3>{charts["ev_rate"]}</div>
    <div class="chart-card"><h3>What would move EV-curious buyers</h3>{charts["ev_drivers"]}</div>
  </div>
  {section_insight(ins["business_insights"]["ev"])}
</section>

<section class="panel" id="factors">
  <div class="panel-head"><h2>Purchase decision factors</h2><p>Priority index: 100 = highest priority. This replaces unreadable raw ranking strings.</p></div>
  <div class="chart-card full">{charts["factors"]}</div>
  {section_insight(ins["business_insights"]["factors"])}
</section>

<section class="panel">
  <div class="panel-head"><h2>Discovery channels</h2><p>Top research channels extracted from the rank columns. Higher priority index means more important.</p></div>
  <div class="chart-card full">{charts["sources"]}</div>
  {section_insight(ins["business_insights"]["discovery"])}
</section>

<section class="panel">
  <div class="panel-head"><h2>Barriers to purchase</h2><p>The strongest friction points between purchase intent and conversion.</p></div>
  <div class="chart-card full">{charts["challenges"]}</div>
  {section_insight(ins["business_insights"]["barriers"])}
</section>

<section class="panel">
  <div class="panel-head"><h2>Brand attributes that matter most</h2><p>What buyers want from a trustworthy brand beyond the vehicle itself.</p></div>
  <div class="chart-card full">{charts["attributes"]}</div>
  {section_insight(ins["business_insights"]["attributes"])}
</section>

<section class="panel">
  <div class="panel-head"><h2>Who responded</h2><p>Age, gender, income and occupation mix.</p></div>
  <div class="chart-card full">{charts["demographics"]}</div>
</section>

<section class="panel" id="voice">
  <div class="panel-head"><h2>Voice of the market</h2><p>Open-ended brand-trust and market-feedback themes.</p></div>
  <div class="chart-card full">{charts["themes"]}</div>
  <div class="grid-2">
    <div class="quote-card"><h3>Four-wheeler respondents</h3>
      {''.join(f'<div class="quote">“{esc(q)}”</div>' for q in quotes_fw)}
    </div>
    <div class="quote-card"><h3>Two-wheeler respondents</h3>
      {''.join(f'<div class="quote">“{esc(q)}”</div>' for q in quotes_tw)}
    </div>
  </div>
</section>

<footer class="footer">
  <div class="ridge"></div>
  <p>Source: supplied four-wheeler survey (n={ins['fw_n']}) and two-wheeler survey (n={ins['tw_n']}). Dashboard generated from the supplied CSV files.</p>
</footer>
</main>
</body>
</html>"""

    OUT_PATH.write_text(html_doc, encoding="utf-8")
    print(f"Dashboard created: {OUT_PATH}")


CSS = f"""
:root{{--navy:{NAVY};--crimson:{CRIMSON};--gold:{GOLD};--slate:{SLATE};--ink:#1C2536;--bg:#F5F6FA;--grid:#E7E9EE}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:Inter,Arial,sans-serif}}
h1,h2,h3,.brand-title{{font-family:"Space Grotesk",Inter,sans-serif}}
.topbar{{position:sticky;top:0;z-index:50;background:var(--navy);box-shadow:0 2px 14px rgba(11,37,69,.25)}}
.flagbar{{height:4px;background:linear-gradient(90deg,var(--crimson) 0 50%,var(--navy) 50%)}}
.topbar-inner{{max-width:1240px;margin:auto;padding:14px 28px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}}
.brand{{display:flex;align-items:center;gap:12px}}
.brand-mark{{width:38px;height:38px;border-radius:8px;background:var(--crimson);color:white;display:flex;align-items:center;justify-content:center;font-weight:800}}
.brand-title{{color:white;font-size:17px;font-weight:700}}
.brand-sub{{color:#B9C4D6;font-size:12px;margin-top:2px}}
.topnav{{display:flex;gap:18px;flex-wrap:wrap}}
.topnav a{{color:#CBD5E6;text-decoration:none;font-size:12.5px}}
main{{max-width:1240px;margin:auto;padding:0 28px 60px}}
.hero{{padding:42px 0 20px}}
.eyebrow{{text-transform:uppercase;letter-spacing:1.5px;font-size:11px;font-weight:800;color:var(--crimson);margin-bottom:8px}}
.hero h1{{font-size:34px;line-height:1.15;margin:0 0 10px;max-width:850px}}
.lede{{color:var(--slate);max-width:820px;line-height:1.55;font-size:15px}}
.kpi-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:24px}}
.kpi{{background:white;border:1px solid var(--grid);border-radius:12px;padding:17px 18px;border-top:3px solid var(--navy)}}
.kpi-label{{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--slate);font-weight:700}}
.kpi-value{{font-family:"Space Grotesk";font-size:25px;font-weight:700;margin:6px 0 3px}}
.kpi-sub{{font-size:11.5px;color:var(--slate)}}
.panel{{margin-top:38px}}
.panel-head{{margin-bottom:14px;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}}
.panel-head h2{{font-size:21px;margin:0}}
.panel-head p{{font-size:13px;color:var(--slate);margin:2px 0 0}}
.tag{{display:inline-block;background:var(--navy);color:white;padding:6px 10px;border-radius:20px;font-size:10px;font-weight:800;letter-spacing:.7px}}
.decision-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
.decision{{background:white;border:1px solid var(--grid);border-radius:12px;padding:16px}}
.decision b{{display:block;color:var(--crimson);font-size:11px;letter-spacing:.8px;margin-bottom:7px}}
.decision span{{font-size:13px;line-height:1.45;color:var(--ink)}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}}
.chart-card,.quote-card{{background:white;border:1px solid var(--grid);border-radius:14px;padding:16px 18px 8px}}
.chart-card h3,.quote-card h3{{font-size:14px;margin:0 0 5px}}
.insight{{background:#FFFDF7;border:1px solid #E7D8A7;border-left:4px solid var(--gold);border-radius:10px;padding:14px 16px;margin-top:12px}}
.insight-title{{font-size:10px;font-weight:800;letter-spacing:1px;color:#7A5A00;margin-bottom:5px}}
.insight-text{{font-size:13.5px;line-height:1.55}}
.quote{{font-size:13px;line-height:1.5;font-style:italic;border-left:3px solid var(--gold);padding:6px 0 6px 12px;margin-bottom:10px}}
.footer{{margin-top:55px;color:var(--slate);font-size:11.5px;text-align:center;line-height:1.6}}
.ridge{{height:20px;margin-bottom:12px;background:linear-gradient(115deg,transparent 48%,var(--grid) 48% 52%,transparent 52%),linear-gradient(65deg,transparent 68%,var(--grid) 68% 72%,transparent 72%)}}
@media(max-width:860px){{.kpi-row,.decision-grid{{grid-template-columns:1fr 1fr}}.grid-2{{grid-template-columns:1fr}}.topnav{{display:none}}.hero h1{{font-size:27px}}}}
@media(max-width:520px){{.kpi-row,.decision-grid{{grid-template-columns:1fr}}main{{padding:0 14px 40px}}}}
"""

if __name__ == "__main__":
    build()
