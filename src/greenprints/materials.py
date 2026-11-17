"""Assign each shipment a material profile via the keyword rules in material_profiles.yaml."""
from __future__ import annotations

import re

import pandas as pd

from greenprints.config import Config


def compile_rules(cfg: Config) -> list[tuple[str, re.Pattern]]:
    return [(r["profile"], re.compile(r["pattern"], re.IGNORECASE))
            for r in cfg.materials.get("keyword_rules", [])]


def match_profile(texts: dict[str, str], rules, default: str) -> tuple[str, str, str]:
    """Return (profile, matched_keyword, matched_column). First rule that matches
    any of the columns wins; columns are checked in the given order."""
    for profile, pattern in rules:
        for col, text in texts.items():
            m = pattern.search(text or "")
            if m:
                return profile, m.group(0), col
    return default, "", ""


def assign_profiles(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    rules = compile_rules(cfg)
    cols = cfg.materials.get("keyword_columns",
                             ["Comments", "Recipient Name", "Shipping Destination"])
    df = df.copy()
    out = [match_profile({c: r.get(c, "") for c in cols}, rules, cfg.default_profile)
           for _, r in df.iterrows()]
    df["material_profile"] = [o[0] for o in out]
    df["matched_keyword"] = [o[1] for o in out]
    df["matched_column"] = [o[2] for o in out]
    return df
