"""Data-quality checks that need the cleaned, in-range shipments."""
from __future__ import annotations

import re

import pandas as pd

from greenprints.config import Config

_US_PATTERN = re.compile(r"\b(usa|united states|u\.s\.)\b", re.IGNORECASE)


def _issue(row, category: str, detail: str) -> dict:
    return {
        "sheet_row": int(row["sheet_row"]),
        "category": category,
        "date_raw": row.get("Date of Shipment", ""),
        "chapter": row.get("Chapters", ""),
        "destination": row.get("Shipping Destination", ""),
        "recipient": row.get("Recipient Name", ""),
        "detail": detail,
    }


def check_shipment_types(df: pd.DataFrame, cfg: Config) -> list[dict]:
    valid = set(cfg.settings.get("valid_shipment_types", []))
    mi = [re.compile(p, re.IGNORECASE) for p in cfg.settings.get("michigan_patterns", [])]
    issues = []
    for _, r in df.iterrows():
        t = r["shipment_type"]
        where = f"{r['destination']} | {r['recipient']}"
        looks_mi = any(p.search(where) for p in mi)
        if t not in valid:
            issues.append(_issue(r, "odd_shipment_type",
                                 f"Shipment Type '{t}' is not one of {sorted(valid)}"))
        elif t != "Local" and looks_mi:
            issues.append(_issue(r, "odd_shipment_type",
                                 f"Marked '{t}' but destination/recipient looks like Michigan "
                                 f"('{where}'). Check whether it should be Local."))
        elif t == "Local" and not looks_mi:
            issues.append(_issue(r, "odd_shipment_type",
                                 f"Marked Local but destination/recipient does not mention a "
                                 f"Michigan place ('{where}'). Probably fine; please confirm."))
        elif t == "International" and _US_PATTERN.search(where):
            issues.append(_issue(r, "odd_shipment_type",
                                 f"Marked International but destination mentions the US "
                                 f"('{where}')."))
    return issues


def check_outliers(df: pd.DataFrame, cfg: Config) -> list[dict]:
    mult = float(cfg.settings.get("outlier_multiplier", 3))
    issues = []
    w = df[df["weight_lbs"].notna()]
    for t, grp in w.groupby("shipment_type"):
        med = grp["weight_lbs"].median()
        for _, r in grp[grp["weight_lbs"] > mult * med].iterrows():
            issues.append(_issue(r, "outlier_weight",
                                 f"{r['weight_lbs']:,.0f} lbs is more than {mult:g}x the "
                                 f"median {t} shipment ({med:,.0f} lbs). Please confirm."))
    return issues


def check_duplicates(df: pd.DataFrame) -> list[dict]:
    key = ["date", "destination", "recipient", "weight_lbs"]
    d = df[df["weight_lbs"].notna()]
    dup = d[d.duplicated(subset=key, keep=False)]
    issues = []
    for _, grp in dup.groupby(key, dropna=False):
        rows = ", ".join(str(x) for x in grp["sheet_row"])
        for _, r in grp.iterrows():
            issues.append(_issue(r, "possible_duplicate",
                                 f"Same month, destination, recipient and weight as sheet "
                                 f"rows {rows}. Check it isn't entered twice."))
    return issues


def run_checks(df: pd.DataFrame, cfg: Config) -> list[dict]:
    return check_shipment_types(df, cfg) + check_outliers(df, cfg) + check_duplicates(df)
