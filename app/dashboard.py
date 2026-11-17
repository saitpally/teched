"""Project Greenprints dashboard.  Run:  streamlit run app/dashboard.py"""
from __future__ import annotations

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
from greenprints.estimate import ESTIMATED, MISSING  # noqa: E402
from greenprints.load import RawDataMissing  # noqa: E402
from greenprints.pipeline import build  # noqa: E402

# B4P blues + validated categorical slots (blue, orange, aqua) for shipment type.
NAVY = "#1F4E79"
BLUE = "#2a78d6"
TYPE_COLORS = {"Local": "#1baf7a", "National": "#eb6834", "International": BLUE}
TYPE_ORDER = ["Local", "National", "International"]
GRID = "#e6e9ee"

st.set_page_config(page_title="Project Greenprints", page_icon="🌱", layout="wide")
st.markdown(f"""
<style>
  h1, h2, h3 {{ color: {NAVY}; }}
  div[data-testid="stMetric"] {{
    background: #F2F7FC; border: 1px solid #D6E4F2; border-left: 5px solid {NAVY};
    border-radius: 8px; padding: 14px 18px;
  }}
  div[data-testid="stMetricValue"] {{ color: {NAVY}; }}
</style>""", unsafe_allow_html=True)


@st.cache_data(show_spinner="Calculating...")
def load_data():
    cfg = load_config(ROOT)
    res = build(cfg)
    return cfg, res.all_rows, res.issues


try:
    cfg, rows, issues = load_data()
except RawDataMissing as e:
    st.title("Project Greenprints")
    st.error("Shipment data not found.")
    st.code(str(e), language=None)
    st.stop()
except ConfigError as e:
    st.error(f"Configuration problem: {e}")
    st.stop()

dated = rows[rows["date"].notna()]
label = lambda b: report.practice_label(cfg, b)  # noqa: E731

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Controls")
    dmin, dmax = dated["date"].min().date(), dated["date"].max().date()
    default = (max(cfg.start_date, dmin), min(cfg.end_date, dmax))
    date_range = st.slider("Shipment dates", min_value=dmin, max_value=dmax, value=default,
                           format="MMM YYYY")
    baseline = st.radio("Baseline (what would have happened)", cfg.baselines,
                        format_func=lambda b: f"{label(b)}" + (
                            " (headline)" if b == cfg.headline_baseline else " (sensitivity)"))
    scenario = st.radio("Material scenario", ["central", "low", "high"], horizontal=True)
    include_est = st.toggle("Include estimated weights", value=True,
                            help="Shipments with no recorded weight, estimated from "
                                 "box/pallet counts.")
    st.caption(f"EPA WARM v{cfg.warm['warm_version']} · alternative: {label(cfg.alternative)}"
               " · freight emissions not counted")

start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
in_range = dated[(dated["date"] >= start) & (dated["date"] <= end)].copy()
counted = in_range[in_range["weight_source"] != MISSING]
if not include_est:
    counted = counted[counted["weight_source"] != ESTIMATED]
val_col = col_avoided(baseline, scenario)

# ---------------------------------------------------------------- header
st.title("Project Greenprints")
st.markdown(f"Greenhouse gas emissions avoided by redistributing surplus medical supplies, "
            f"**{start:%b %Y} – {end:%b %Y}**.")

c1, c2, c3 = st.columns(3)
c1.metric("Pounds diverted", f"{counted['weight_lbs'].sum():,.0f} lbs")
tot = {s: counted[col_avoided(baseline, s)].sum() for s in ("low", "central", "high")}
c2.metric(f"MTCO2e avoided ({scenario})", f"{tot[scenario]:,.1f}")
c2.caption(f"Range {tot['low']:,.1f} – {tot['high']:,.1f} MTCO2e (low – high) · "
           f"{label(baseline)} baseline")
c3.metric("Shipments", f"{len(in_range)}")
n_missing = int((in_range["weight_source"] == MISSING).sum())
n_est = int((in_range["weight_source"] == ESTIMATED).sum())
c3.caption(f"{n_est} with estimated weight ({'included' if include_est else 'excluded'}) · "
           f"{n_missing} with no weight (not counted)")


def style(fig, height=380):
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white",
        paper_bgcolor="white", font=dict(color="#333"), hoverlabel=dict(bgcolor="white"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None))
    fig.update_xaxes(showgrid=False, linecolor="#bbb")
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig


# ---------------------------------------------------------------- charts
left, right = st.columns([3, 2])
with left:
    st.subheader("MTCO2e avoided by academic year")
    by_ay = (counted.groupby(["academic_year", "shipment_type"])[val_col].sum()
             .reset_index().rename(columns={val_col: "MTCO2e"}))
    types = [t for t in TYPE_ORDER if t in set(by_ay["shipment_type"])] + sorted(
        set(by_ay["shipment_type"]) - set(TYPE_ORDER))
    fig = px.bar(by_ay, x="academic_year", y="MTCO2e", color="shipment_type",
                 category_orders={"shipment_type": types,
                                  "academic_year": sorted(by_ay["academic_year"].unique())},
                 color_discrete_map=TYPE_COLORS, labels={"academic_year": "Academic year"})
    fig.update_traces(marker_line_color="white", marker_line_width=2,
                      hovertemplate="%{x} · %{fullData.name}<br>%{y:,.1f} MTCO2e<extra></extra>")
    fig.update_layout(bargap=0.45)
    st.plotly_chart(style(fig))
    st.caption("Academic years run September–August.")

with right:
    st.subheader("By material profile")
    by_p = (counted.groupby("material_profile")
            .agg(MTCO2e=(val_col, "sum"), lbs=("weight_lbs", "sum"), n=("sheet_row", "count"))
            .reset_index().sort_values("MTCO2e"))
    by_p["profile"] = (by_p["material_profile"].str.replace("_", " ").str.capitalize()
                       .str.replace(r"\bPpe\b", "PPE", regex=True))
    fig = go.Figure(go.Bar(
        x=by_p["MTCO2e"], y=by_p["profile"], orientation="h", marker_color=BLUE,
        customdata=by_p[["lbs", "n"]], text=by_p["MTCO2e"].map(lambda v: f"{v:,.1f}"),
        textposition="outside", cliponaxis=False,
        hovertemplate="%{y}<br>%{x:,.1f} MTCO2e<br>%{customdata[0]:,.0f} lbs · "
                      "%{customdata[1]} shipments<extra></extra>"))
    fig.update_layout(bargap=0.4, xaxis_title="MTCO2e avoided")
    st.plotly_chart(style(fig))
    st.caption("Profiles are assumed material mixes, not measurements.")

st.subheader("Cumulative pounds diverted")
monthly = counted.groupby("date")["weight_lbs"].sum().sort_index()
if not monthly.empty:
    idx = pd.date_range(monthly.index.min(), end, freq="MS")
    cum = monthly.reindex(idx, fill_value=0).cumsum()
    fig = go.Figure(go.Scatter(
        x=cum.index, y=cum.values, mode="lines", line=dict(color=NAVY, width=2),
        fill="tozeroy", fillcolor="rgba(31,78,121,0.08)",
        hovertemplate="%{x|%b %Y}<br>%{y:,.0f} lbs to date<extra></extra>"))
    fig.update_layout(hovermode="x unified", yaxis_title="lbs")
    st.plotly_chart(style(fig, 320))

# ---------------------------------------------------------------- table
st.subheader("Shipments")
f1, f2, f3 = st.columns([1, 1, 2])
type_sel = f1.multiselect("Shipment type", sorted(in_range["shipment_type"].unique()))
prof_sel = f2.multiselect("Material profile", sorted(in_range["material_profile"].unique()))
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
    "Destination": t["destination"], "Recipient": t["recipient"], "Type": t["shipment_type"],
    "lbs": t["weight_lbs"].round(0), "Weight source": t["weight_source"],
    "Profile": t["material_profile"], "Keyword": t["matched_keyword"],
    f"MTCO2e ({label(baseline)}, {scenario})": t[val_col].round(2),
    "Comments": t["Comments"],
}).sort_values("Row")
st.dataframe(show, width="stretch", hide_index=True)
st.download_button("Download this table (CSV)", show.to_csv(index=False),
                   "greenprints_shipments.csv", "text/csv")

if not issues.empty:
    with st.expander(f"Data-quality items ({len(issues)})"):
        st.dataframe(issues, width="stretch", hide_index=True)

with st.expander("Methodology"):
    meth = ROOT / "METHODOLOGY.md"
    text = meth.read_text(encoding="utf-8") if meth.exists() else report.methodology_md(cfg)
    st.markdown(text.split("\n", 1)[1] if text.startswith("# ") else text)  # drop H1
