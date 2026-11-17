"""Output tables, Excel workbook, data-quality report and METHODOLOGY.md."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd

from greenprints.config import SCENARIOS, Config
from greenprints.emissions import avoided_per_short_ton, blended_factor, col_avoided, col_disposal
from greenprints.estimate import ESTIMATED, MISSING, RECORDED

BLUE = "1F4E79"
LIGHT_BLUE = "DDEBF7"

ISSUE_TITLES = {
    "missing_weight": "Missing weights (no weight and no box/pallet count)",
    "unparseable_date": "Unparseable or blank dates (excluded from totals)",
    "odd_shipment_type": "Shipment Type values to double-check (not changed)",
    "outlier_weight": "Unusually heavy shipments",
    "possible_duplicate": "Possible duplicate rows",
    "estimated_weight": "Weights estimated from box/pallet counts",
    "zero_weight": "Weight recorded as 0 (treated as missing)",
    "non_numeric_value": "Text in number columns (treated as blank)",
    "excluded_totals_row": "Totals rows excluded",
}


def practice_label(cfg: Config, key: str) -> str:
    return cfg.warm.get("practices", {}).get(key, key)


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------
def aggregate(df: pd.DataFrame, cfg: Config, by: str | list[str] | None = None) -> pd.DataFrame:
    """Totals of weight and emissions, optionally grouped."""
    base = cfg.headline_baseline
    d = df.assign(
        lbs_recorded=df["weight_lbs"].where(df["weight_source"] == RECORDED, 0.0),
        lbs_estimated=df["weight_lbs"].where(df["weight_source"] == ESTIMATED, 0.0),
        missing_weight=(df["weight_source"] == MISSING).astype(int),
    )
    agg = {
        "Shipments": ("sheet_row", "count"),
        "Missing weight (rows)": ("missing_weight", "sum"),
        "Total lbs": ("weight_lbs", "sum"),
        "Recorded lbs": ("lbs_recorded", "sum"),
        "Estimated lbs": ("lbs_estimated", "sum"),
        "Short tons": ("short_tons", "sum"),
    }
    for b in cfg.baselines:
        lab = practice_label(cfg, b)
        for s in ("central", "low", "high"):
            agg[f"MTCO2e avoided ({lab}, {s})"] = (col_avoided(b, s), "sum")
    agg[f"Disposal-only MTCO2e ({practice_label(cfg, base)}, central)"] = (
        col_disposal(base, "central"), "sum")
    if by is None:
        row = {k: d[c].sum() if f == "sum" else d[c].count() for k, (c, f) in agg.items()}
        return pd.DataFrame([row])
    return d.groupby(by, dropna=False).agg(**agg).reset_index()


def with_total_row(table: pd.DataFrame, label_col: str | list[str]) -> pd.DataFrame:
    cols = [label_col] if isinstance(label_col, str) else label_col
    tot = table.drop(columns=cols).sum(numeric_only=True).to_frame().T
    for i, c in enumerate(cols):
        tot.insert(i, c, "TOTAL" if i == 0 else "")
    return pd.concat([table, tot], ignore_index=True)


def headline(df: pd.DataFrame, cfg: Config, baseline: str | None = None) -> dict:
    b = baseline or cfg.headline_baseline
    return {
        "shipments": int(len(df)),
        "lbs": float(df["weight_lbs"].sum()),
        "lbs_recorded": float(df.loc[df["weight_source"] == RECORDED, "weight_lbs"].sum()),
        "lbs_estimated": float(df.loc[df["weight_source"] == ESTIMATED, "weight_lbs"].sum()),
        "n_missing": int((df["weight_source"] == MISSING).sum()),
        "n_estimated": int((df["weight_source"] == ESTIMATED).sum()),
        "short_tons": float(df["short_tons"].sum()),
        **{s: float(df[col_avoided(b, s)].sum()) for s in SCENARIOS},
        "disposal_central": float(df[col_disposal(b, "central")].sum()),
    }


def summary_rows(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    h = headline(df, cfg)
    base = cfg.headline_baseline
    rows = [
        ("Date range", f"{cfg.start_date:%b %Y} - {cfg.end_date:%b %Y}", "Inclusive"),
        ("WARM version", f"v{cfg.warm['warm_version']} ({cfg.warm.get('release_date', '')})",
         cfg.warm.get("source", "").strip()),
        ("Shipments", h["shipments"], ""),
        ("  with recorded weight", h["shipments"] - h["n_estimated"] - h["n_missing"], ""),
        ("  with estimated weight", h["n_estimated"], "From box/pallet counts"),
        ("  with missing weight (not counted)", h["n_missing"], "See Data Quality"),
        ("Total lbs diverted", h["lbs"], "Recorded + estimated"),
        ("  recorded lbs", h["lbs_recorded"], ""),
        ("  estimated lbs", h["lbs_estimated"], ""),
        ("Short tons (2,000 lbs)", h["short_tons"], ""),
    ]
    for b in cfg.baselines:
        lab = practice_label(cfg, b)
        tag = "HEADLINE" if b == base else "Sensitivity"
        hb = headline(df, cfg, b)
        rows += [
            (f"MTCO2e avoided - {lab} baseline (central)", hb["central"], tag),
            (f"MTCO2e avoided - {lab} baseline (low)", hb["low"], "Low material scenario"),
            (f"MTCO2e avoided - {lab} baseline (high)", hb["high"], "High material scenario"),
        ]
    share = 1 - h["disposal_central"] / h["central"] if h["central"] else float("nan")
    rows += [
        (f"Disposal-only MTCO2e ({practice_label(cfg, base)}, central)", h["disposal_central"],
         "Emissions disposal itself would have caused"),
        ("Share of headline benefit from avoided manufacturing", share,
         "1 - disposal-only / avoided"),
        ("Freight emissions", "Not counted", "See METHODOLOGY.md limitations"),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value", "Notes"])


def top_shipments(df: pd.DataFrame, cfg: Config, n: int = 5) -> pd.DataFrame:
    c = col_avoided(cfg.headline_baseline, "central")
    cols = ["sheet_row", "date", "chapter", "destination", "recipient", "shipment_type",
            "weight_lbs", "weight_source", "material_profile", c]
    return df.sort_values(c, ascending=False).head(n)[cols]


# ---------------------------------------------------------------------------
# Clean shipment table
# ---------------------------------------------------------------------------
def clean_table(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    base = cfg.headline_baseline
    cols = {
        "sheet_row": "sheet_row",
        "date": "date",
        "academic_year": "academic_year",
        "calendar_year": "calendar_year",
        "chapter": "chapter",
        "destination": "destination",
        "recipient": "recipient",
        "shipment_type": "shipment_type",
        "boxes": "boxes",
        "pallets": "pallets",
        "weight_lbs_recorded": "weight_lbs_recorded",
        "weight_lbs": "weight_lbs",
        "weight_source": "weight_source",
        "material_profile": "material_profile",
        "matched_keyword": "matched_keyword",
        "matched_column": "matched_column",
        "short_tons": "short_tons",
    }
    out = df[list(cols)].rename(columns=cols).copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    # Headline columns (spec names) first, then every baseline x scenario.
    for s in SCENARIOS:
        out[f"avoided_mtco2e_{s}"] = df[col_avoided(base, s)]
    for b in cfg.baselines:
        for s in SCENARIOS:
            out[col_avoided(b, s)] = df[col_avoided(b, s)]
    for b in cfg.baselines:
        for s in SCENARIOS:
            out[col_disposal(b, s)] = df[col_disposal(b, s)]
    out["transport_mtco2e"] = df["transport_mtco2e"]
    out["comments"] = df["Comments"]
    return out


# ---------------------------------------------------------------------------
# Assumptions tables
# ---------------------------------------------------------------------------
def assumptions_tables(cfg: Config) -> dict[str, pd.DataFrame]:
    s = cfg.settings
    consts = pd.DataFrame([
        ("Date range start", str(cfg.start_date), "settings.yaml"),
        ("Date range end", str(cfg.end_date), "settings.yaml"),
        ("Academic year start month", s.get("academic_year_start_month", 9), "settings.yaml"),
        ("lbs per short ton", cfg.lbs_per_short_ton, "settings.yaml"),
        ("lbs per box (estimates)", s["estimation"]["lbs_per_box"], "settings.yaml"),
        ("lbs per pallet (estimates)", s["estimation"]["lbs_per_pallet"], "settings.yaml"),
        ("Alternative scenario", practice_label(cfg, cfg.alternative), "settings.yaml"),
        ("Headline baseline", practice_label(cfg, cfg.headline_baseline), "settings.yaml"),
        ("Sensitivity baselines",
         ", ".join(practice_label(cfg, b) for b in cfg.baselines[1:]) or "none", "settings.yaml"),
        ("Freight emissions counted", bool((s.get("transport") or {}).get("enabled")),
         "settings.yaml"),
        ("Outlier rule", f"> {s.get('outlier_multiplier', 3)}x median weight for type",
         "settings.yaml"),
        ("WARM version", cfg.warm["warm_version"], "warm_factors.yaml"),
        ("WARM source", cfg.warm.get("source", "").strip(), cfg.warm.get("url", "")),
    ], columns=["Item", "Value", "Where it's set"])

    practices = list(cfg.warm["practices"])
    factors = pd.DataFrame(
        [{"Material": m, **{cfg.warm["practices"][p]: f.get(p) for p in practices}}
         for m, f in cfg.factors.items()])

    prof_rows, per_ton_rows = [], []
    for pname, p in cfg.profiles.items():
        for scen in SCENARIOS:
            shares = cfg.profile_shares(pname, scen)
            for mat, sh in shares.items():
                prof_rows.append((pname, scen, mat, sh))
            row = {"Profile": pname, "Scenario": scen}
            for b in cfg.baselines:
                row[f"Avoided MTCO2e/short ton ({practice_label(cfg, b)} baseline)"] = \
                    avoided_per_short_ton(shares, cfg.factors, b, cfg.alternative)
            row[f"Disposal-only MTCO2e/short ton ({practice_label(cfg, cfg.headline_baseline)})"] \
                = blended_factor(shares, cfg.factors, cfg.headline_baseline)
            per_ton_rows.append(row)
    profiles = pd.DataFrame(prof_rows, columns=["Profile", "Scenario", "Material", "Share"])
    per_ton = pd.DataFrame(per_ton_rows)
    rules = pd.DataFrame(
        [(i + 1, r["profile"], r["pattern"]) for i, r in
         enumerate(cfg.materials.get("keyword_rules", []))]
        + [(len(cfg.materials.get("keyword_rules", [])) + 1, cfg.default_profile,
            "(no match: default)")],
        columns=["Order", "Profile", "Pattern (case-insensitive regex)"])
    return {
        "Constants": consts,
        "WARM factors (MTCO2e per short ton)": factors,
        "Material profiles (ASSUMPTIONS, placeholders until boxes are sampled)": profiles,
        "Resulting factor per short ton, by profile": per_ton,
        "Keyword rules (first match wins)": rules,
    }


# ---------------------------------------------------------------------------
# Excel
# ---------------------------------------------------------------------------
def write_excel(res, path: Path) -> None:
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    cfg, df = res.cfg, res.shipments
    sheets: dict[str, list[tuple[str | None, pd.DataFrame]]] = {}

    sheets["Summary"] = [(None, summary_rows(df, cfg))]
    ay = with_total_row(aggregate(df, cfg, "academic_year").rename(
        columns={"academic_year": "Academic year (Sep-Aug)"}), "Academic year (Sep-Aug)")
    cy = with_total_row(aggregate(df, cfg, "calendar_year").rename(
        columns={"calendar_year": "Calendar year"}), "Calendar year")
    hc = col_avoided(cfg.headline_baseline, "central")
    ay_type = (df.pivot_table(index="academic_year", columns="shipment_type", values=hc,
                              aggfunc="sum", fill_value=0).reset_index()
               .rename(columns={"academic_year": "Academic year"}))
    sheets["By Year"] = [
        ("Academic year (September - August)", ay),
        ("Calendar year", cy),
        (f"MTCO2e avoided ({practice_label(cfg, cfg.headline_baseline)}, central) by academic "
         "year and shipment type", ay_type),
    ]
    sheets["By Shipment Type"] = [(None, with_total_row(
        aggregate(df, cfg, "shipment_type").rename(columns={"shipment_type": "Shipment type"}),
        "Shipment type"))]
    dest = aggregate(df, cfg, ["destination", "shipment_type"]).rename(
        columns={"destination": "Destination", "shipment_type": "Shipment type"})
    dest = dest.sort_values(dest.columns[[c.startswith("MTCO2e") for c in dest.columns]][0],
                            ascending=False)
    sheets["By Destination"] = [(None, with_total_row(dest, ["Destination", "Shipment type"]))]
    sheets["By Material Profile"] = [(None, with_total_row(
        aggregate(df, cfg, "material_profile").rename(
            columns={"material_profile": "Material profile"}), "Material profile"))]
    sheets["Shipment Detail"] = [(None, clean_table(df, cfg))]
    sheets["Assumptions"] = list(assumptions_tables(cfg).items())
    sheets["Data Quality"] = [(None, res.issues.rename(columns={
        "sheet_row": "Sheet row", "category": "Issue", "date_raw": "Date (as entered)",
        "chapter": "Chapter", "destination": "Destination", "recipient": "Recipient",
        "detail": "Detail"}))]

    header_fill = PatternFill("solid", fgColor=BLUE)
    title_font = Font(bold=True, size=12, color=BLUE)
    total_fill = PatternFill("solid", fgColor=LIGHT_BLUE)

    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        for name, blocks in sheets.items():
            row = 0
            for title, table in blocks:
                if title:
                    pd.DataFrame().to_excel(xw, sheet_name=name, startrow=row)
                    xw.sheets[name].cell(row=row + 1, column=1, value=title).font = title_font
                    row += 1
                table.to_excel(xw, sheet_name=name, startrow=row, index=False)
                ws = xw.sheets[name]
                for j in range(1, len(table.columns) + 1):
                    c = ws.cell(row=row + 1, column=j)
                    c.fill = header_fill
                    c.font = Font(bold=True, color="FFFFFF")
                    c.alignment = Alignment(wrap_text=True, vertical="top")
                for i in range(len(table)):
                    first = ws.cell(row=row + 2 + i, column=1)
                    is_total = first.value == "TOTAL"
                    for j, col in enumerate(table.columns, start=1):
                        cell = ws.cell(row=row + 2 + i, column=j)
                        if is_total:
                            cell.fill = total_fill
                            cell.font = Font(bold=True)
                        if isinstance(cell.value, float):
                            if name == "Summary" and "Share" in str(first.value):
                                cell.number_format = "0.0%"
                            elif col == "Share":
                                cell.number_format = "0.000"
                            else:
                                cell.number_format = "#,##0.00"
                row += len(table) + 3
            ws = xw.sheets[name]
            ws.freeze_panes = None
            for j in range(1, ws.max_column + 1):
                letter = get_column_letter(j)
                width = max((len(str(c.value)) for c in ws[letter] if c.value is not None),
                            default=8)
                ws.column_dimensions[letter].width = min(max(10, width + 2), 60)


# ---------------------------------------------------------------------------
# Markdown reports
# ---------------------------------------------------------------------------
def _md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_None._\n"
    cols = list(df.columns)
    lines = ["| " + " | ".join(str(c) for c in cols) + " |",
             "|" + "|".join("---" for _ in cols) + "|"]
    for _, r in df.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                v = "" if pd.isna(v) else f"{v:,.2f}"
            vals.append(str(v).replace("|", "\\|").replace("\n", " "))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines) + "\n"


def data_quality_md(res) -> str:
    cfg, st = res.cfg, res.stats
    out = [
        "# Data Quality Report",
        "",
        f"_Generated {dt.datetime.now():%Y-%m-%d %H:%M} from `{cfg.settings['raw_file']}`. "
        "Row numbers refer to the row in the Google Sheet (header = row 1)._",
        "",
        "## Row accounting",
        "",
        f"- Rows in the CSV: {st['raw_rows']}",
        f"- Blank spacer rows removed: {st['blank_rows_removed']}",
        f"- Totals rows removed: {st['totals_rows_removed']}",
        f"- Shipment rows parsed: {st['parsed_rows']}",
        f"- Rows with no readable date (excluded from totals): {st['undated_rows']}",
        f"- Rows outside {cfg.start_date} to {cfg.end_date}: {st['rows_outside_range']}",
        f"- **Rows in the analysis: {st['rows_in_range']}**",
        "",
    ]
    if res.sanity:
        out += ["## Sanity check against expected totals", ""]
        for ok, msg in res.sanity:
            out.append(f"- {'OK' if ok else '**CHECK**'}: {msg}")
        out.append("")
    issues = res.issues
    for cat, title in ISSUE_TITLES.items():
        sub = issues[issues["category"] == cat] if not issues.empty else issues
        out += [f"## {title} ({len(sub)})", ""]
        out.append(_md_table(sub.drop(columns=["category"]).rename(columns={
            "sheet_row": "Row", "date_raw": "Date", "chapter": "Chapter",
            "destination": "Destination", "recipient": "Recipient", "detail": "Detail"})))
        out.append("")
    return "\n".join(out)


def methodology_md(cfg: Config, res=None) -> str:
    base, alt = cfg.headline_baseline, cfg.alternative
    sens = cfg.baselines[1:]
    est = cfg.settings["estimation"]
    lpt = cfg.lbs_per_short_ton
    w = cfg.warm
    tables = assumptions_tables(cfg)

    ex_shares = {"Mixed Plastics": 1.0} if "Mixed Plastics" in cfg.factors else \
        {next(iter(cfg.factors)): 1.0}
    ex_mat = next(iter(ex_shares))
    ex_b = cfg.factors[ex_mat][base]
    ex_a = cfg.factors[ex_mat][alt]

    lines = [
        "# Project Greenprints: Methodology",
        "",
        "_This file is generated automatically every time the tool runs, from the files in "
        "`config/`. Do not edit it by hand; edit the config and re-run._",
        "",
    ]
    if res is not None:
        h = headline(res.shipments, cfg)
        lines += [
            "## Results at a glance",
            "",
            f"Between **{cfg.start_date:%B %Y}** and **{cfg.end_date:%B %Y}**, Blueprints for "
            f"Pangaea redistributed **{h['lbs']:,.0f} lbs** ({h['short_tons']:,.1f} short tons) "
            f"of surplus medical supplies across **{h['shipments']} shipments**. We estimate "
            f"this avoided **{h['central']:,.0f} metric tons of CO2 equivalent (MTCO2e)** "
            f"(range {h['low']:,.0f} to {h['high']:,.0f}) compared with the supplies being "
            f"{'landfilled' if base == 'landfilling' else practice_label(cfg, base).lower()}.",
            "",
        ]
        for b in sens:
            hb = headline(res.shipments, cfg, b)
            lines += [f"If the supplies would instead have been sent to "
                      f"{practice_label(cfg, b).lower()} (incinerated), the estimate is "
                      f"{hb['central']:,.0f} MTCO2e (range {hb['low']:,.0f} to {hb['high']:,.0f}).",
                      ""]
        if h["n_missing"]:
            lines += [f"{h['n_missing']} shipment(s) had no weight or box/pallet count and are "
                      "**not** included in these totals.", ""]
    lines += [
        "## What we measured",
        "",
        "Blueprints for Pangaea (B4P) collects surplus medical supplies from Michigan Medicine "
        "that would otherwise be thrown away, and sends them to clinics locally, nationally "
        "and internationally. This analysis estimates the greenhouse gas emissions avoided "
        "because those supplies were reused instead of discarded.",
        "",
        "## The data",
        "",
        "- Source: B4P's *Master Shipment Database* (Google Sheet), exported as CSV.",
        f"- Date range: shipments dated **{cfg.start_date:%B %Y} through {cfg.end_date:%B %Y}**"
        " (inclusive). The sheet records month and year only, so each shipment is dated "
        "the 1st of its month.",
        "- Weight: the *Poundage of shipments (lbs)* column, which includes the boxes and "
        "packaging the supplies were shipped in.",
        f"- Academic years run September to August (for example, 2023-24 = September 2023 "
        "to August 2024).",
        "",
        "## Method: EPA Waste Reduction Model (WARM)",
        "",
        f"We use the U.S. EPA's **Waste Reduction Model (WARM), version {w['warm_version']}** "
        f"({w.get('release_date', '')}). WARM gives an emission factor, in MTCO2e per short ton "
        f"(1 short ton = {lpt:,.0f} lbs), for each material under each way of handling it.",
        "",
        "The emissions avoided are the difference between two scenarios:",
        "",
        f"- **Baseline (without B4P): {practice_label(cfg, base)}.** The supplies would have "
        "been thrown away and sent to a landfill. "
        + (f"As a sensitivity check we also report a **{', '.join(practice_label(cfg, b) for b in sens)}** "
           "baseline, because hospital waste is often incinerated. " if sens else "")
        + "The landfill figure is the headline number.",
        f"- **Alternative (what B4P does): {practice_label(cfg, alt)}.** The supplies are used "
        "by a clinic, so new supplies do not need to be manufactured. WARM credits the "
        "emissions from making those new products as avoided.",
        "",
        "```",
        "avoided MTCO2e = short tons x (baseline factor - alternative factor)",
        "```",
        "",
        f"Example: {lpt:,.0f} lbs of {ex_mat.lower()} = 1 short ton x ({ex_b:.2f} - ({ex_a:.2f}))"
        f" = **{ex_b - ex_a:.2f} MTCO2e avoided**.",
        "",
        "We also report a smaller **disposal-only** number: what disposing of the supplies "
        "would itself have emitted (short tons x baseline factor). For plastics in a landfill "
        "this is very small, because plastics barely break down. Comparing it with the "
        "headline shows that almost all of the benefit comes from avoided manufacturing.",
        "",
        "### The replacement assumption",
        "",
        "The method assumes that **every donated item replaces a new item the recipient "
        "would otherwise have bought**. If a clinic would simply have gone without, or if "
        "some donated items go unused, the true benefit is smaller than reported.",
        "",
        "## What the supplies are made of (material profiles)",
        "",
        "WARM factors are per material, but our records mostly give only a total weight and a "
        "short comment. Each shipment is therefore given a **material profile**: an assumed "
        "mix of WARM materials by weight. **These mixes are estimates, not measurements**; "
        "they are placeholders until B4P weighs and sorts sample boxes.",
        "",
        "A shipment's profile is chosen by keyword rules applied to the Comments, Recipient "
        "Name and Shipping Destination columns. The first rule that matches wins:",
        "",
        _md_table(tables["Keyword rules (first match wins)"]),
        "",
        "Each profile has a **central** (best guess), **low** and **high** version. Low "
        "assumes less cardboard/paper packaging; high assumes more. Every total is reported "
        "as a central estimate with a low-high range.",
        "",
        _md_table(tables["Material profiles (ASSUMPTIONS, placeholders until boxes are sampled)"]
                  .pivot_table(index=["Profile", "Material"], columns="Scenario",
                               values="Share", aggfunc="first")
                  .reindex(columns=list(SCENARIOS)).reset_index()),
        "",
        "Resulting emission factor for each profile (MTCO2e avoided per short ton):",
        "",
        _md_table(tables["Resulting factor per short ton, by profile"]),
        "",
        "Adult diapers, bed pads, blankets and hygiene items have no exact WARM material; "
        "they are approximated as a mix of mixed plastics and mixed paper.",
        "",
        "### WARM factors used",
        "",
        _md_table(tables["WARM factors (MTCO2e per short ton)"]),
        "",
        f"Source: {w.get('source', '').strip()}, <{w.get('url', '')}>.",
        "",
        "## Missing weights",
        "",
        "1. If a weight is recorded, we use it.",
        f"2. If not, but the number of pallets and/or boxes is known, we estimate it with B4P's "
        f"Estimates Calculator: pallets x {est['lbs_per_pallet']:g} lbs + boxes x "
        f"{est['lbs_per_box']:g} lbs.",
        "3. If neither is known, the shipment is left out of the totals and listed in the data "
        "quality report so it can be filled in.",
        "",
        "## Limitations",
        "",
        "- **Freight emissions are not counted.** Trucking and ocean/air shipping to recipients "
        "produce emissions that would reduce the net benefit, especially for international "
        "shipments. The tool is designed so this can be added later.",
        "- **Material profiles are estimates.** The low-high range shows how much the result "
        "depends on them; sampling real boxes would narrow it.",
        "- **Replacement assumption.** We assume each donated item displaces the purchase of "
        "a new one.",
        "- **WARM is a U.S. model.** Manufacturing and disposal emissions are U.S. averages "
        "and may differ for the actual products and for recipient countries.",
        "- **Shipment weight includes packaging**, which is why cardboard appears in the "
        "profiles.",
        "- **Month-level dates.** Shipments are dated to the month, not the day.",
        "",
    ]
    return "\n".join(lines)
