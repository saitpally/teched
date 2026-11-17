"""Fill missing shipment weights using B4P's Estimates Calculator constants."""
from __future__ import annotations

import math

import pandas as pd

from greenprints.config import Config

RECORDED = "recorded"
ESTIMATED = "estimated_from_counts"
MISSING = "missing"


def estimate_weight(pallets: float, boxes: float, lbs_per_pallet: float,
                    lbs_per_box: float) -> float:
    """pallets x lbs_per_pallet + boxes x lbs_per_box. NaN if neither count is > 0."""
    p = 0.0 if pallets is None or math.isnan(pallets) else max(float(pallets), 0.0)
    b = 0.0 if boxes is None or math.isnan(boxes) else max(float(boxes), 0.0)
    if p == 0 and b == 0:
        return math.nan
    return p * lbs_per_pallet + b * lbs_per_box


def fill_weights(df: pd.DataFrame, cfg: Config) -> tuple[pd.DataFrame, list[dict]]:
    est = cfg.settings["estimation"]
    lbs_pallet = float(est["lbs_per_pallet"])
    lbs_box = float(est["lbs_per_box"])
    df = df.copy()
    issues: list[dict] = []

    weights, sources = [], []
    for _, r in df.iterrows():
        w = r["weight_lbs_recorded"]
        if pd.notna(w):
            weights.append(float(w))
            sources.append(RECORDED)
            continue
        e = estimate_weight(r["pallets"], r["boxes"], lbs_pallet, lbs_box)
        if math.isnan(e):
            weights.append(math.nan)
            sources.append(MISSING)
            issues.append(_issue(r, "missing_weight",
                                 "No weight and no box/pallet count. Please fill in the "
                                 "weight in the sheet."))
        else:
            weights.append(e)
            sources.append(ESTIMATED)
            parts = []
            if pd.notna(r["pallets"]) and r["pallets"] > 0:
                parts.append(f"{r['pallets']:g} pallets x {lbs_pallet:g}")
            if pd.notna(r["boxes"]) and r["boxes"] > 0:
                parts.append(f"{r['boxes']:g} boxes x {lbs_box:g}")
            note = " + ".join(parts)
            if len(parts) == 2:
                note += " (both counts present: boxes may already be on the pallets, so " \
                        "this may double count)"
            issues.append(_issue(r, "estimated_weight",
                                 f"Weight estimated as {e:,.2f} lbs = {note}"))
    df["weight_lbs"] = weights
    df["weight_source"] = sources
    return df, issues


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
