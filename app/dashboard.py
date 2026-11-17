"""Project Greenprints dashboard.  Run:  streamlit run app/dashboard.py"""
from __future__ import annotations

import base64
import html
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_ROOT / "src"))  # works even without `pip install -e .`
ROOT = Path(os.environ.get("GREENPRINTS_HOME", APP_ROOT))

from greenprints import report  # noqa: E402
from greenprints.config import ConfigError, load_config  # noqa: E402
from greenprints.emissions import col_avoided  # noqa: E402
from greenprints.estimate import ESTIMATED, MISSING, RECORDED  # noqa: E402
from greenprints.load import RawDataMissing  # noqa: E402
from greenprints.pipeline import build  # noqa: E402

# ---------------------------------------------------------------- theme
NAVY = "#08113F"
BLUE = "#2F65E3"
INDIGO = "#343A82"
GREEN = "#3A7A4E"
INK = "#141B3C"
MUTED = "#6B7280"
LINE = "#E3E8F3"
GRID = "#EDF0F7"
# Shipment-type colors (pairwise OKLab dE >= 18, normal and deuteranopia).
TYPE_COLORS = {"Local": GREEN, "National": INDIGO, "International": BLUE}
TYPE_ORDER = ["Local", "National", "International"]

st.set_page_config(page_title="Greenprints · Blueprints for Pangaea", page_icon="🌱",
                   layout="wide")

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Poppins:wght@400;500;600&display=swap');
html, body, .stApp, .stMarkdown, button, input, textarea, select,
[data-testid="stWidgetLabel"] p {{ font-family: 'Poppins', sans-serif; }}
.stApp {{ background: #F0F3FC; color: {INK}; }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stToolbar"], #MainMenu, footer {{ visibility: hidden; }}
.block-container {{ padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1360px; }}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {{ background: {NAVY}; }}
[data-testid="stSidebarHeader"] {{ display: none; }}
[data-testid="stSidebarUserContent"] {{ padding-top: 0; }}
[data-testid="stSidebarContent"] {{ padding-top: 0; }}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {{ color: #D5DAEE; }}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
  color: #8E97BF; font-size: 12px; font-weight: 500; }}
[data-testid="stSidebar"] [data-testid="stSliderTickBarMin"],
[data-testid="stSidebar"] [data-testid="stSliderTickBarMax"] {{ color: #8E97BF; }}
.gp-logo {{ background: #fff; margin: 0 -1.5rem 0; padding: 22px 1.5rem 18px; }}
.gp-logo img {{ width: 150px; display: block; }}
.gp-app {{ padding: 20px 0 14px; border-bottom: 1px solid rgba(255,255,255,.08);
  margin-bottom: 18px; }}
.gp-app .t {{ font-family: 'Playfair Display', serif; color: #fff; font-size: 21px;
  font-weight: 700; line-height: 1.2; }}
.gp-app .s {{ color: #8E97BF; font-size: 12.5px; }}
.gp-nav-label {{ color: #8E97BF; font-size: 12px; margin: 6px 0 4px; }}
.gp-side-note {{ color: #8E97BF; font-size: 11.5px; line-height: 1.55;
  border-top: 1px solid rgba(255,255,255,.08); padding-top: 14px; margin-top: 10px; }}

/* ---------- top bar ---------- */
.gp-top {{ display:flex; align-items:center; justify-content:space-between;
  margin-bottom: 18px; gap: 12px; flex-wrap: wrap; }}
.gp-top .left {{ display:flex; gap:8px; flex-wrap:wrap; }}
.gp-user {{ display:flex; align-items:center; gap:10px; }}
.gp-avatar {{ width:34px; height:34px; border-radius:50%; background:{INDIGO}; color:#fff;
  display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:600; }}
.gp-user .n {{ font-weight:600; font-size:13.5px; line-height:1.1; }}
.gp-user .r {{ color:{MUTED}; font-size:11.5px; }}

/* ---------- pills & chips ---------- */
.gp-pill {{ display:inline-flex; align-items:center; gap:6px; border-radius:999px;
  padding:3px 11px; font-size:12px; font-weight:500; border:1px solid; white-space:nowrap; }}
.gp-pill.orange {{ background:#FFF4E5; border-color:#F2C89A; color:#A85A12; }}
.gp-pill.green  {{ background:#E9F4EC; border-color:#E9F4EC; color:{GREEN}; }}
.gp-pill.blue   {{ background:#EAF0FD; border-color:#EAF0FD; color:{BLUE}; }}
.gp-pill.navy   {{ background:#ECEDF7; border-color:#ECEDF7; color:{INDIGO}; }}
.gp-chip {{ display:inline-flex; align-items:center; gap:5px; border:1px solid #CFE3D4;
  color:#2F6B40; border-radius:999px; padding:3px 12px; font-size:12.5px; margin:0 6px 6px 0; }}

/* ---------- headings ---------- */
.gp-h1 {{ font-family:'Playfair Display', serif; font-weight:700; font-size:34px;
  color:{INK}; margin:0; line-height:1.15; }}
.gp-sub {{ color:#4B5368; font-size:14px; margin:4px 0 16px; }}

/* ---------- banner ---------- */
.gp-banner {{ display:flex; align-items:center; gap:12px; border-radius:12px;
  padding:12px 16px; font-weight:500; font-size:14px; margin-bottom:18px; }}
.gp-banner.ok {{ background:#E6F3E9; border:1px solid #CBE5D2; color:#2F6B40; }}
.gp-banner.info {{ background:#EAF0FD; border:1px solid #D3DEF8; color:{INDIGO}; }}
.gp-banner .ic {{ width:30px; height:30px; border-radius:8px; background:rgba(255,255,255,.6);
  display:flex; align-items:center; justify-content:center; }}

/* ---------- cards (st.container(key="card_...")) ---------- */
[class*="st-key-card"] {{ background:#fff; border:1px solid {LINE}; border-radius:14px;
  padding:18px 20px 14px; box-shadow:0 1px 2px rgba(16,24,64,.04); gap: 0.6rem; }}
[class*="st-key-card_blue"]  {{ border-top:4px solid {BLUE}; }}
[class*="st-key-card_navy"]  {{ border-top:4px solid {INDIGO}; }}
[class*="st-key-card_green"] {{ border-top:4px solid {GREEN}; }}
.gp-card-head {{ display:flex; justify-content:space-between; align-items:baseline;
  font-weight:600; font-size:15px; color:{INK}; line-height:1.6; padding-bottom:6px; }}
.gp-card-head .r {{ font-weight:400; font-size:12.5px; color:#4B5368; }}
.gp-card-head .r b {{ color:{GREEN}; }}
.gp-cap {{ color:{MUTED}; font-size:12px; margin-top:-4px; }}

/* hero */
.gp-hero {{ display:flex; gap:22px; align-items:center; flex-wrap:wrap; }}
.gp-hero .meta {{ flex:1; min-width:300px; }}
.gp-hero .org {{ display:flex; gap:8px; align-items:center; flex-wrap:wrap;
  font-size:13px; color:#3B4258; font-weight:500; }}
.gp-hero .title {{ font-family:'Playfair Display', serif; font-weight:700; font-size:27px;
  margin:4px 0 2px; color:{INK}; }}
.gp-hero .money {{ color:{GREEN}; font-weight:600; font-size:14px; }}
.gp-hero .money span {{ color:#4B5368; font-weight:500; }}
.gp-hero .desc {{ font-size:13.5px; color:#3B4258; margin:8px 0 10px; }}
.gp-stats {{ display:flex; gap:0; border:1px solid {LINE}; border-radius:12px;
  overflow:hidden; }}
.gp-stat {{ padding:12px 18px; min-width:124px; border-right:1px solid {LINE}; }}
.gp-stat:last-child {{ border-right:none; }}
.gp-stat .k {{ color:{MUTED}; font-size:11.5px; }}
.gp-stat .v {{ font-weight:600; font-size:19px; color:{INK}; }}
.gp-stat .u {{ color:{MUTED}; font-size:11px; }}

/* breakdown bars */
.gp-bar {{ margin:6px 0 12px; }}
.gp-bar .row {{ display:flex; justify-content:space-between; font-size:13.5px;
  font-weight:500; }}
.gp-bar .row b {{ font-weight:600; }}
.gp-bar .row b span {{ color:{MUTED}; font-weight:400; }}
.gp-bar .track {{ height:5px; background:#EEF1F6; border-radius:4px; margin:6px 0 4px; }}
.gp-bar .fill {{ height:5px; border-radius:4px; }}
.gp-bar .note {{ color:{MUTED}; font-size:11.5px; }}

/* checklist */
.gp-check {{ display:flex; align-items:center; justify-content:space-between; gap:10px;
  border:1px solid {LINE}; background:#F8FAFD; border-radius:8px; padding:8px 12px;
  font-size:13px; margin-bottom:7px; }}
.gp-check .l {{ display:flex; align-items:center; gap:10px; }}
.gp-check .ic {{ width:18px; height:18px; border-radius:50%; display:flex;
  align-items:center; justify-content:center; font-size:10px; font-weight:700; flex:none; }}
.gp-check.pass .ic {{ background:#E3F1E7; color:{GREEN}; }}
.gp-check.warn {{ background:#FFF7EC; border-color:#F6DDBA; }}
.gp-check.warn .ic {{ background:#FCE7C8; color:#A85A12; }}
.gp-check.warn .s {{ color:#A85A12; }}
.gp-check.fail {{ background:#FDEEEE; border-color:#F5C9C9; }}
.gp-check.fail .ic {{ background:#F9D6D6; color:#C0392B; }}
.gp-check.fail .s {{ color:#C0392B; }}
.gp-check .s {{ font-size:12px; font-weight:500; white-space:nowrap; color:{MUTED}; }}

/* top shipments list */
.gp-item {{ display:flex; gap:12px; align-items:center; padding:7px 0; }}
.gp-item .box {{ width:52px; min-width:52px; height:48px; border-radius:9px;
  border:1px solid {LINE}; background:#F6F8FD; display:flex; flex-direction:column;
  align-items:center; justify-content:center; }}
.gp-item .box b {{ font-size:15px; color:{INK}; line-height:1.1; }}
.gp-item .box span {{ font-size:9.5px; color:{MUTED}; }}
.gp-item .box.hot {{ background:#FFF4E5; border-color:#F2C89A; }}
.gp-item .box.hot b {{ color:#A85A12; }}
.gp-item .t {{ font-weight:600; font-size:13.5px; color:{INK}; line-height:1.25; }}
.gp-item .m {{ color:{MUTED}; font-size:12px; }}

/* widgets in cards */
[data-testid="stExpander"] details {{ background:#fff; border:1px solid {LINE};
  border-radius:14px; }}
[data-testid="stExpander"] summary p {{ font-weight:600; }}
.stDownloadButton button {{ border-radius:10px; border:1px solid {LINE}; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def H(s: str) -> str:
    return html.escape(str(s))


def md(markup: str, where=st) -> None:
    where.markdown(markup, unsafe_allow_html=True)


def card_head(title: str, right: str = "") -> None:
    md(f'<div class="gp-card-head"><span>{title}</span><span class="r">{right}</span></div>')


# ---------------------------------------------------------------- data
@st.cache_data(show_spinner="Calculating...")
def load_data():
    cfg = load_config(ROOT)
    res = build(cfg)
    return cfg, res.all_rows, res.issues, res.sanity


def sidebar_brand():
    logo = APP_ROOT / "app" / "assets" / "b4p_logo.png"
    img = ""
    if logo.exists():
        b64 = base64.b64encode(logo.read_bytes()).decode()
        img = f'<img src="data:image/png;base64,{b64}" alt="Blueprints for Pangaea">'
    md(f'<div class="gp-logo">{img}</div>'
       '<div class="gp-app"><div class="t">Greenprints</div>'
       '<div class="s">Operations · emissions impact</div></div>', st.sidebar)


try:
    cfg, rows, issues, sanity = load_data()
except RawDataMissing as e:
    sidebar_brand()
    md('<div class="gp-h1">Greenprints</div>')
    st.error("Shipment data not found.")
    st.code(str(e), language=None)
    st.stop()
except ConfigError as e:
    st.error(f"Configuration problem: {e}")
    st.stop()

dated = rows[rows["date"].notna()]
label = lambda b: report.practice_label(cfg, b)  # noqa: E731


def profile_name(p: str) -> str:
    return "PPE" if p == "ppe" else p.replace("_", " ").capitalize()


# ---------------------------------------------------------------- sidebar
sidebar_brand()
with st.sidebar:
    md('<div class="gp-nav-label">Reporting period</div>')
    dmin, dmax = dated["date"].min().date(), dated["date"].max().date()
    default = (max(cfg.start_date, dmin), min(cfg.end_date, dmax))
    date_range = st.slider("Shipment dates", min_value=dmin, max_value=dmax, value=default,
                           format="MMM YYYY", label_visibility="collapsed")
    md('<div class="gp-nav-label">Scenario</div>')
    baseline = st.radio("Baseline: what would have happened", cfg.baselines,
                        format_func=lambda b: label(b) + (
                            " (headline)" if b == cfg.headline_baseline else " (sensitivity)"))
    scenario = st.radio("Material mix", ["central", "low", "high"], horizontal=True,
                        format_func=str.capitalize)
    include_est = st.toggle("Include estimated weights", value=True,
                            help="Shipments with no recorded weight, estimated from "
                                 "box/pallet counts.")
    md(f'<div class="gp-side-note">EPA WARM v{cfg.warm["warm_version"]} '
       f'({H(cfg.warm.get("release_date", ""))})<br>Alternative: {H(label(cfg.alternative))}'
       '<br>Freight emissions not counted</div>', st.sidebar)

start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
is_default_range = (date_range[0], date_range[1]) == default
in_range = dated[(dated["date"] >= start) & (dated["date"] <= end)].copy()
counted = in_range[in_range["weight_source"] != MISSING]
if not include_est:
    counted = counted[counted["weight_source"] != ESTIMATED]
val_col = col_avoided(baseline, scenario)
tot = {s: counted[col_avoided(baseline, s)].sum() for s in ("low", "central", "high")}
lbs = counted["weight_lbs"].sum()
n_missing = int((in_range["weight_source"] == MISSING).sum())
n_est = int((in_range["weight_source"] == ESTIMATED).sum())
n_rec = int((in_range["weight_source"] == RECORDED).sum())

# ---------------------------------------------------------------- top bar
md('<div class="gp-top"><div class="left">'
   f'<span class="gp-pill orange">● Material mixes are placeholder assumptions</span>'
   f'<span class="gp-pill blue">EPA WARM v{cfg.warm["warm_version"]}</span></div>'
   '<div class="gp-user"><div class="gp-avatar">OP</div><div>'
   '<div class="n">Operations</div><div class="r">Project Greenprints</div></div></div></div>')

md('<div class="gp-h1">Emissions Impact</div>'
   f'<div class="gp-sub">Greenhouse gas emissions avoided by redistributing surplus medical '
   f'supplies, {start:%b %Y} – {end:%b %Y}.</div>')

if is_default_range and sanity and all(ok for ok, _ in sanity):
    md('<div class="gp-banner ok"><div class="ic">✓</div>'
       f'Reconciled with the Master Shipment List: {len(in_range)} shipments and '
       f'{in_range.loc[in_range["weight_source"] == RECORDED, "weight_lbs"].sum():,.0f} '
       'recorded lbs match the expected totals</div>')
elif not is_default_range:
    md('<div class="gp-banner info"><div class="ic">i</div>Custom period selected. '
       f'The reporting period in settings.yaml is {cfg.start_date:%b %Y} – '
       f'{cfg.end_date:%b %Y}.</div>')

# ---------------------------------------------------------------- hero card
ring = (
    '<svg width="104" height="104" viewBox="0 0 104 104" role="img" '
    f'aria-label="{tot[scenario]:,.0f} MTCO2e avoided">'
    f'<circle cx="52" cy="52" r="45" fill="none" stroke="#E3EFE6" stroke-width="7"/>'
    f'<circle cx="52" cy="52" r="45" fill="none" stroke="{GREEN}" stroke-width="7" '
    f'stroke-linecap="round" stroke-dasharray="{2*3.1416*45*0.999:.1f} 999" '
    'transform="rotate(-90 52 52)"/>'
    f'<text x="52" y="54" text-anchor="middle" font-family="Poppins" font-weight="600" '
    f'font-size="24" fill="{INK}">{tot[scenario]:,.0f}</text>'
    f'<text x="52" y="72" text-anchor="middle" font-family="Poppins" font-size="10" '
    f'fill="{GREEN}">MTCO2e</text></svg>')
type_lbs = counted.groupby("shipment_type")["weight_lbs"].sum()
chips = "".join(f'<span class="gp-chip">✓ {H(t)} · {type_lbs.get(t, 0):,.0f} lbs</span>'
                for t in TYPE_ORDER if t in type_lbs.index)
combustion_note = ""
for b in cfg.baselines:
    if b != baseline:
        alt_val = counted[col_avoided(b, scenario)].sum()
        combustion_note = (f'<div class="gp-stat"><div class="k">If {H(label(b).lower())}'
                           f'</div><div class="v">{alt_val:,.1f}</div>'
                           '<div class="u">MTCO2e (sensitivity)</div></div>')
        break
with st.container(key="card_hero"):
    md(f'<div class="gp-hero">{ring}<div class="meta">'
       '<div class="org">Blueprints for Pangaea'
       f'<span class="gp-pill green">{H(label(baseline))} baseline</span>'
       f'<span class="gp-pill navy">{H(scenario.capitalize())} mix</span>'
       + ('<span class="gp-pill orange">Estimated weights excluded</span>'
          if not include_est and n_est else '') +
       '</div>'
       '<div class="title">Emissions avoided</div>'
       f'<div class="money">{tot["low"]:,.1f} – {tot["high"]:,.1f} MTCO2e '
       '<span>· low – high range</span></div>'
       f'<div class="desc">{lbs:,.0f} lbs of surplus medical supplies reused instead of '
       f'thrown away, so new ones did not have to be made.</div>{chips}</div>'
       '<div class="gp-stats">'
       f'<div class="gp-stat"><div class="k">Pounds diverted</div>'
       f'<div class="v">{lbs:,.0f}</div><div class="u">lbs</div></div>'
       f'<div class="gp-stat"><div class="k">Shipments</div><div class="v">{len(in_range)}'
       f'</div><div class="u">{n_rec} recorded · {n_est} est. · {n_missing} missing</div></div>'
       f'{combustion_note}</div></div>')


def style(fig, height=330):
    fig.update_layout(
        height=height, margin=dict(l=4, r=4, t=36, b=4), plot_bgcolor="white",
        paper_bgcolor="white", font=dict(family="Poppins, sans-serif", color="#4B5368",
                                         size=12),
        hoverlabel=dict(bgcolor="white", bordercolor=LINE, font_family="Poppins"),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, x=0, title=None))
    fig.update_xaxes(showgrid=False, linecolor=LINE, title=None)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, title=None)
    return fig


st.write("")
# ---------------------------------------------------------------- row: year + quality
left, right = st.columns([1.6, 1], gap="medium")
with left:
    with st.container(key="card_blue_year"):
        by_ay = (counted.groupby(["academic_year", "shipment_type"])[val_col].sum()
                 .reset_index().rename(columns={val_col: "MTCO2e"}))
        yearly = by_ay.groupby("academic_year")["MTCO2e"].sum()
        card_head("MTCO2e avoided by academic year",
                  " + ".join(f"{v:,.0f}" for v in yearly.values)
                  + f" = <b>{yearly.sum():,.0f}</b>")
        types = [t for t in TYPE_ORDER if t in set(by_ay["shipment_type"])] + sorted(
            set(by_ay["shipment_type"]) - set(TYPE_ORDER))
        fig = px.bar(by_ay, x="academic_year", y="MTCO2e", color="shipment_type",
                     category_orders={"shipment_type": types,
                                      "academic_year": sorted(by_ay["academic_year"].unique())},
                     color_discrete_map=TYPE_COLORS)
        fig.update_traces(marker_line_color="white", marker_line_width=2,
                          marker_cornerradius=4,
                          hovertemplate="%{x} · %{fullData.name}<br>%{y:,.1f} MTCO2e"
                                        "<extra></extra>")
        fig.update_layout(bargap=0.5)
        st.plotly_chart(style(fig), config={"displayModeBar": False})
        md('<div class="gp-cap">Academic years run September – August, split by shipment '
           'type.</div>')

with right:
    with st.container(key="card_navy_quality"):
        cnt = issues["category"].value_counts() if not issues.empty else pd.Series(dtype=int)
        checks = []
        rec_lbs = in_range.loc[in_range["weight_source"] == RECORDED, "weight_lbs"].sum()
        if sanity:
            ok = all(o for o, _ in sanity)
            checks.append(("pass" if ok else "fail", "Matches the shipment sheet totals",
                           f"{rec_lbs:,.0f} lbs" if ok else "Mismatch"))
        checks += [
            ("pass" if not cnt.get("unparseable_date") else "fail", "All dates readable",
             "" if not cnt.get("unparseable_date") else f"{cnt['unparseable_date']} rows"),
            ("pass" if not cnt.get("missing_weight") else "fail", "Every shipment has a weight",
             "" if not cnt.get("missing_weight") else f"{cnt['missing_weight']} missing"),
            ("pass" if not cnt.get("estimated_weight") else "warn", "Weights recorded, not estimated",
             "" if not cnt.get("estimated_weight") else f"{cnt['estimated_weight']} estimated"),
            ("pass" if not cnt.get("outlier_weight") else "warn", "No unusually heavy shipments",
             "" if not cnt.get("outlier_weight") else f"{cnt['outlier_weight']} to confirm"),
            ("pass" if not cnt.get("odd_shipment_type") else "warn",
             "Shipment types look consistent",
             "" if not cnt.get("odd_shipment_type") else f"{cnt['odd_shipment_type']} to review"),
            ("pass" if not cnt.get("possible_duplicate") else "warn", "No duplicate rows",
             "" if not cnt.get("possible_duplicate") else f"{cnt['possible_duplicate']} rows"),
        ]
        n_pass = sum(c[0] == "pass" for c in checks)
        card_head("Data quality", f"{n_pass} of {len(checks)} pass")
        icon = {"pass": "✓", "warn": "!", "fail": "✕"}
        md("".join(f'<div class="gp-check {s}"><div class="l"><span class="ic">{icon[s]}'
                   f'</span>{H(t)}</div><span class="s">{H(note)}</span></div>'
                   for s, t, note in checks))
        md('<div class="gp-cap">Details per row: data/processed/data_quality_report.md</div>')

# ---------------------------------------------------------------- row: profiles + top
left, right = st.columns([1.6, 1], gap="medium")
with left:
    with st.container(key="card_green_profiles"):
        by_p = (counted.groupby("material_profile")
                .agg(m=(val_col, "sum"), lbs=("weight_lbs", "sum"), n=("sheet_row", "count"))
                .sort_values("m", ascending=False))
        card_head("Breakdown by material profile", f"<b>{by_p['m'].sum():,.1f}</b> MTCO2e")
        top = by_p["m"].max() if len(by_p) else 1
        bars = []
        for i, (p, r) in enumerate(by_p.iterrows()):
            mix = cfg.profile_shares(p, scenario)
            mix_txt = ", ".join(f"{int(round(v * 100))}% {k.lower()}" for k, v in mix.items())
            bars.append(
                f'<div class="gp-bar"><div class="row"><span>{H(profile_name(p))}</span>'
                f'<b>{r["m"]:,.1f}<span> MTCO2e</span></b></div>'
                f'<div class="track"><div class="fill" style="width:{100 * r["m"] / top:.1f}%;'
                f'background:{GREEN if i == 0 else BLUE}"></div></div>'
                f'<div class="note">{int(r["n"])} shipment{"s" if r["n"] != 1 else ""} · '
                f'{r["lbs"]:,.0f} lbs · '
                f'assumed mix: {H(mix_txt)}</div></div>')
        md("".join(bars))

with right:
    with st.container(key="card_blue_top"):
        card_head("Biggest shipments by impact", "Top 5")
        top5 = counted.sort_values(val_col, ascending=False).head(5)
        items = []
        for i, (_, r) in enumerate(top5.iterrows()):
            who = r["recipient"] or r["destination"]
            items.append(
                f'<div class="gp-item"><div class="box{" hot" if i == 0 else ""}">'
                f'<b>{r[val_col]:,.1f}</b><span>MTCO2e</span></div><div>'
                f'<div class="t">{H(who)}</div><div class="m">{H(r["destination"])} · '
                f'{r["date"]:%b %Y} · {r["weight_lbs"]:,.0f} lbs</div></div></div>')
        md("".join(items))

# ---------------------------------------------------------------- cumulative
with st.container(key="card_navy_cum"):
    monthly = counted.groupby("date")["weight_lbs"].sum().sort_index()
    card_head("Cumulative pounds diverted", f"<b>{lbs:,.0f}</b> lbs to date")
    if not monthly.empty:
        idx = pd.date_range(monthly.index.min(), end, freq="MS")
        cum = monthly.reindex(idx, fill_value=0).cumsum()
        fig = go.Figure(go.Scatter(
            x=cum.index, y=cum.values, mode="lines", line=dict(color=INDIGO, width=2),
            fill="tozeroy", fillcolor="rgba(52,58,130,0.07)",
            hovertemplate="%{x|%b %Y}<br>%{y:,.0f} lbs to date<extra></extra>"))
        fig.update_layout(hovermode="x unified", showlegend=False)
        st.plotly_chart(style(fig, 290), config={"displayModeBar": False})

# ---------------------------------------------------------------- table
with st.container(key="card_table"):
    card_head("Shipments", f"{len(in_range)} in period")
    f1, f2, f3 = st.columns([1, 1, 2])
    type_sel = f1.multiselect("Shipment type", sorted(in_range["shipment_type"].unique()))
    prof_sel = f2.multiselect("Material profile", sorted(in_range["material_profile"].unique()),
                              format_func=profile_name)
    search = f3.text_input("Search destination, recipient or comments")
    t = in_range
    if type_sel:
        t = t[t["shipment_type"].isin(type_sel)]
    if prof_sel:
        t = t[t["material_profile"].isin(prof_sel)]
    if search:
        blob = (t["destination"] + " " + t["recipient"] + " " + t["Comments"]).str.lower()
        t = t[blob.str.contains(search.lower(), regex=False)]
    show = pd.DataFrame({
        "Row": t["sheet_row"], "Month": t["date"].dt.strftime("%b %Y"),
        "Destination": t["destination"], "Recipient": t["recipient"],
        "Type": t["shipment_type"], "lbs": t["weight_lbs"].round(0),
        "Weight source": t["weight_source"].str.replace("_", " "),
        "Profile": t["material_profile"].map(profile_name), "Keyword": t["matched_keyword"],
        "MTCO2e": t[val_col], "Comments": t["Comments"],
    }).sort_values("Row")
    st.dataframe(
        show, hide_index=True, width="stretch", height=380,
        column_config={
            "lbs": st.column_config.NumberColumn(format="localized"),
            "MTCO2e": st.column_config.ProgressColumn(
                f"MTCO2e ({label(baseline).lower()}, {scenario})", format="%.2f",
                min_value=0, max_value=float(in_range[val_col].max() or 1)),
        })
    st.download_button("Download this table (CSV)", show.to_csv(index=False),
                       "greenprints_shipments.csv", "text/csv")

st.write("")
with st.expander("Methodology"):
    meth = ROOT / "METHODOLOGY.md"
    text = meth.read_text(encoding="utf-8") if meth.exists() else report.methodology_md(cfg)
    st.markdown(text.split("\n", 1)[1] if text.startswith("# ") else text)  # drop H1
