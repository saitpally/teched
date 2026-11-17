"""WARM math.

avoided_MTCO2e = short_tons x (EF_baseline - EF_alternative)

where each EF for a shipment is the share-weighted average of the WARM factors
of the materials in its profile. All factors come from config/warm_factors.yaml.
"""
from __future__ import annotations

import math

import pandas as pd

from greenprints.config import SCENARIOS, Config


def lbs_to_short_tons(lbs: float, lbs_per_short_ton: float) -> float:
    return lbs / lbs_per_short_ton


def blended_factor(shares: dict[str, float], factors: dict, practice: str) -> float:
    """Share-weighted WARM factor (MTCO2e / short ton) for one management practice."""
    total = 0.0
    for material, share in shares.items():
        ef = factors[material][practice]
        if ef is None:
            raise ValueError(f"WARM has no '{practice}' factor for '{material}'")
        total += float(share) * float(ef)
    return total


def avoided_per_short_ton(shares: dict[str, float], factors: dict, baseline: str,
                          alternative: str) -> float:
    return blended_factor(shares, factors, baseline) - blended_factor(shares, factors, alternative)


def avoided_mtco2e(lbs: float, shares: dict[str, float], factors: dict, baseline: str,
                   alternative: str, lbs_per_short_ton: float) -> float:
    if lbs is None or math.isnan(lbs):
        return math.nan
    tons = lbs_to_short_tons(lbs, lbs_per_short_ton)
    return tons * avoided_per_short_ton(shares, factors, baseline, alternative)


def disposal_mtco2e(lbs: float, shares: dict[str, float], factors: dict, baseline: str,
                    lbs_per_short_ton: float) -> float:
    """What disposing of the supplies would have emitted: short_tons x EF_baseline."""
    if lbs is None or math.isnan(lbs):
        return math.nan
    return lbs_to_short_tons(lbs, lbs_per_short_ton) * blended_factor(shares, factors, baseline)


def transport_mtco2e(df: pd.DataFrame, cfg: Config) -> pd.Series:
    """Freight emissions per shipment. NOT counted in this version (returns 0).

    Extension point: when settings.yaml `transport.enabled` is true, implement e.g.
    tonne-km x mode-specific factor here using Shipment Type / Transportation, with
    factors stored in config/. Net impact = avoided - transport.
    """
    if (cfg.settings.get("transport") or {}).get("enabled"):
        raise NotImplementedError(
            "Transport emissions are not implemented yet. Set transport.enabled: false "
            "in settings.yaml, or add the method here with factors in config/.")
    return pd.Series(0.0, index=df.index)


def col_avoided(baseline: str, scenario: str) -> str:
    return f"avoided_mtco2e_{baseline}_{scenario}"


def col_disposal(baseline: str, scenario: str) -> str:
    return f"disposal_only_mtco2e_{baseline}_{scenario}"


def add_emissions(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Add short tons and avoided/disposal MTCO2e columns for every baseline x scenario."""
    df = df.copy()
    lpt = cfg.lbs_per_short_ton
    factors = cfg.factors
    alt = cfg.alternative
    df["short_tons"] = df["weight_lbs"] / lpt

    for base in cfg.baselines:
        for scen in SCENARIOS:
            per_ton = {p: avoided_per_short_ton(cfg.profile_shares(p, scen), factors, base, alt)
                       for p in cfg.profiles}
            disp_per_ton = {p: blended_factor(cfg.profile_shares(p, scen), factors, base)
                            for p in cfg.profiles}
            df[col_avoided(base, scen)] = df["short_tons"] * df["material_profile"].map(per_ton)
            df[col_disposal(base, scen)] = (df["short_tons"]
                                            * df["material_profile"].map(disp_per_ton))

    df["transport_mtco2e"] = transport_mtco2e(df, cfg)
    return df
