import math

import pytest

from greenprints.config import ConfigError, validate, validate_profile_shares
from greenprints.emissions import avoided_mtco2e, blended_factor, disposal_mtco2e


def test_mixed_plastics_landfill_baseline(cfg):
    v = avoided_mtco2e(2000, {"Mixed Plastics": 1.0}, cfg.factors, "landfilling",
                       "source_reduction", cfg.lbs_per_short_ton)
    assert v == pytest.approx(1.89)


def test_corrugated_landfill_baseline(cfg):
    v = avoided_mtco2e(2000, {"Corrugated Containers": 1.0}, cfg.factors, "landfilling",
                       "source_reduction", cfg.lbs_per_short_ton)
    assert v == pytest.approx(5.76)


def test_combustion_baseline(cfg):
    # 1 short ton mixed plastics: 1.26 - (-1.87) = 3.13
    v = avoided_mtco2e(2000, {"Mixed Plastics": 1.0}, cfg.factors, "combustion",
                       "source_reduction", cfg.lbs_per_short_ton)
    assert v == pytest.approx(3.13)


def test_disposal_only(cfg):
    assert disposal_mtco2e(2000, {"Mixed Plastics": 1.0}, cfg.factors, "landfilling",
                           cfg.lbs_per_short_ton) == pytest.approx(0.02)


def test_fifty_fifty_mix_is_average(cfg):
    mix = {"Mixed Plastics": 0.5, "Corrugated Containers": 0.5}
    v = avoided_mtco2e(2000, mix, cfg.factors, "landfilling", "source_reduction",
                       cfg.lbs_per_short_ton)
    assert v == pytest.approx((1.89 + 5.76) / 2)
    for prac in ("landfilling", "source_reduction", "combustion"):
        expected = (cfg.factors["Mixed Plastics"][prac]
                    + cfg.factors["Corrugated Containers"][prac]) / 2
        assert blended_factor(mix, cfg.factors, prac) == pytest.approx(expected)


def test_missing_weight_gives_nan(cfg):
    assert math.isnan(avoided_mtco2e(float("nan"), {"Mixed Plastics": 1.0}, cfg.factors,
                                     "landfilling", "source_reduction", 2000))


def test_shares_not_summing_to_one_raise():
    with pytest.raises(ConfigError):
        validate_profile_shares("bad", {"Mixed Plastics": 0.6, "Corrugated Containers": 0.3})
    validate_profile_shares("ok", {"Mixed Plastics": 0.6, "Corrugated Containers": 0.4})


def test_bad_profile_in_config_fails_validation(cfg_copy):
    cfg_copy.materials["profiles"]["ppe"]["central"] = {"Mixed Plastics": 0.9}
    with pytest.raises(ConfigError, match="ppe.central"):
        validate(cfg_copy)


def test_unknown_material_fails_validation(cfg_copy):
    cfg_copy.materials["profiles"]["ppe"]["central"] = {"Unobtainium": 1.0}
    with pytest.raises(ConfigError, match="not in warm_factors"):
        validate(cfg_copy)


def test_real_profiles_low_central_high_ordering(cfg):
    """Low < central < high per short ton, under every configured baseline."""
    from greenprints.emissions import avoided_per_short_ton
    for p in cfg.profiles:
        for b in cfg.baselines:
            lo, c, hi = (avoided_per_short_ton(cfg.profile_shares(p, s), cfg.factors, b,
                                               cfg.alternative)
                         for s in ("low", "central", "high"))
            assert lo <= c <= hi, (p, b, lo, c, hi)
