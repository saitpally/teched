"""Run every stage: load -> clean -> estimate -> materials -> emissions -> checks."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from greenprints import estimate, load, materials, quality
from greenprints.config import Config, load_config
from greenprints.emissions import add_emissions

# Issue categories reported even if the row falls outside the date range
# (we can't tell what range an undated row belongs to).
ALWAYS_REPORT = {"unparseable_date", "excluded_totals_row"}

ISSUE_ORDER = [
    "missing_weight", "unparseable_date", "odd_shipment_type", "outlier_weight",
    "possible_duplicate", "estimated_weight", "zero_weight", "non_numeric_value",
    "excluded_totals_row",
]


@dataclass
class Result:
    cfg: Config
    all_rows: pd.DataFrame          # every parsed shipment row (any date), with emissions
    shipments: pd.DataFrame         # rows inside the configured date range
    issues: pd.DataFrame
    stats: dict = field(default_factory=dict)
    sanity: list = field(default_factory=list)   # list of (ok: bool, message: str)


def build(cfg: Config | None = None) -> Result:
    cfg = cfg or load_config()
    raw = load.read_raw(cfg.raw_file)
    rows, issues = load.clean(raw, cfg)
    rows, est_issues = estimate.fill_weights(rows, cfg)
    rows = materials.assign_profiles(rows, cfg)
    rows = add_emissions(rows, cfg)

    shipments = load.filter_dates(rows, cfg.start_date, cfg.end_date)
    in_range = set(shipments["sheet_row"])
    all_issues = [i for i in issues + est_issues
                  if i["category"] in ALWAYS_REPORT or i["sheet_row"] in in_range]
    all_issues += quality.run_checks(shipments, cfg)

    issues_df = pd.DataFrame(all_issues, columns=[
        "sheet_row", "category", "date_raw", "chapter", "destination", "recipient", "detail"])
    if not issues_df.empty:
        order = {c: i for i, c in enumerate(ISSUE_ORDER)}
        issues_df["_o"] = issues_df["category"].map(lambda c: order.get(c, 99))
        issues_df = issues_df.sort_values(["_o", "sheet_row"]).drop(columns="_o")
        issues_df = issues_df.reset_index(drop=True)

    stats = {
        "raw_rows": len(raw),
        "blank_rows_removed": rows.attrs.get("n_blank_rows", 0),
        "totals_rows_removed": rows.attrs.get("n_totals_rows", 0),
        "parsed_rows": len(rows),
        "undated_rows": int(rows["date"].isna().sum()),
        "rows_outside_range": int(rows["date"].notna().sum() - len(shipments)),
        "rows_in_range": len(shipments),
    }
    res = Result(cfg=cfg, all_rows=rows, shipments=shipments, issues=issues_df, stats=stats)
    res.sanity = sanity_check(shipments, cfg)
    return res


def sanity_check(df: pd.DataFrame, cfg: Config) -> list[tuple[bool, str]]:
    sc = cfg.settings.get("sanity_check")
    if not sc:
        return []
    tol = float(sc.get("tolerance_pct", 5)) / 100
    out = []

    def _cmp(label, actual, expected):
        if expected in (None, 0):
            return
        ok = abs(actual - expected) <= tol * abs(expected)
        out.append((ok, f"{label}: got {actual:,.0f}, expected about {expected:,.0f}"))

    rec = df[df["weight_source"] == estimate.RECORDED]
    _cmp("Shipment rows in range", len(df), sc.get("expected_rows"))
    _cmp("Recorded lbs", rec["weight_lbs"].sum(), sc.get("expected_recorded_lbs"))
    for t, exp in (sc.get("expected_recorded_lbs_by_type") or {}).items():
        _cmp(f"Recorded lbs ({t})", rec.loc[rec["shipment_type"] == t, "weight_lbs"].sum(), exp)
    return out
