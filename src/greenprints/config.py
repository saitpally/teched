"""Load and validate everything in config/. No factors or assumptions live in Python."""
from __future__ import annotations

import datetime as dt
import os
from dataclasses import dataclass
from pathlib import Path

import yaml

SCENARIOS = ("low", "central", "high")
SHARE_TOLERANCE = 1e-6


class ConfigError(ValueError):
    """Raised when a config file is missing or inconsistent."""


def project_root() -> Path:
    """The greenprints/ folder. Override with the GREENPRINTS_HOME env variable."""
    env = os.environ.get("GREENPRINTS_HOME")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[2]


@dataclass
class Config:
    root: Path
    settings: dict
    warm: dict
    materials: dict

    # -- convenience accessors -------------------------------------------
    @property
    def raw_file(self) -> Path:
        return self.root / self.settings["raw_file"]

    @property
    def output_dir(self) -> Path:
        return self.root / self.settings["output_dir"]

    @property
    def start_date(self) -> dt.date:
        return _to_date(self.settings["date_range"]["start"])

    @property
    def end_date(self) -> dt.date:
        return _to_date(self.settings["date_range"]["end"])

    @property
    def alternative(self) -> str:
        return self.settings["scenario"]["alternative"]

    @property
    def headline_baseline(self) -> str:
        return self.settings["scenario"]["headline_baseline"]

    @property
    def baselines(self) -> list[str]:
        """Headline baseline first, then sensitivity baselines."""
        out = [self.headline_baseline]
        for b in self.settings["scenario"].get("sensitivity_baselines", []) or []:
            if b not in out:
                out.append(b)
        return out

    @property
    def lbs_per_short_ton(self) -> float:
        return float(self.settings["lbs_per_short_ton"])

    @property
    def factors(self) -> dict:
        return self.warm["factors"]

    @property
    def profiles(self) -> dict:
        return self.materials["profiles"]

    @property
    def default_profile(self) -> str:
        return self.materials["default_profile"]

    def profile_shares(self, profile: str, scenario: str = "central") -> dict[str, float]:
        p = self.profiles[profile]
        return p.get(scenario) or p["central"]


def _to_date(value) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        raise ConfigError(f"Missing config file: {path}")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ConfigError(f"Config file is empty or malformed: {path}")
    return data


def load_config(root: Path | None = None) -> Config:
    root = Path(root) if root else project_root()
    cfg = Config(
        root=root,
        settings=_read_yaml(root / "config" / "settings.yaml"),
        warm=_read_yaml(root / "config" / "warm_factors.yaml"),
        materials=_read_yaml(root / "config" / "material_profiles.yaml"),
    )
    validate(cfg)
    return cfg


def validate_profile_shares(name: str, shares: dict[str, float]) -> None:
    total = sum(float(v) for v in shares.values())
    if abs(total - 1.0) > SHARE_TOLERANCE:
        raise ConfigError(
            f"Material profile '{name}' shares add up to {total:.4f}, not 1.0: {shares}"
        )
    for mat, v in shares.items():
        if float(v) < 0:
            raise ConfigError(f"Material profile '{name}' has a negative share for {mat}")


def validate(cfg: Config) -> None:
    practices = set(cfg.warm.get("practices", {}))
    s = cfg.settings["scenario"]
    for key in [s["alternative"], *cfg.baselines]:
        if key not in practices:
            raise ConfigError(f"settings.yaml scenario uses unknown WARM practice '{key}'")

    if cfg.start_date > cfg.end_date:
        raise ConfigError("settings.yaml date_range.start is after date_range.end")

    factors = cfg.factors
    if not cfg.profiles:
        raise ConfigError("material_profiles.yaml has no profiles")
    if cfg.default_profile not in cfg.profiles:
        raise ConfigError(f"default_profile '{cfg.default_profile}' is not a defined profile")

    needed_practices = [cfg.alternative, *cfg.baselines]
    for pname, p in cfg.profiles.items():
        if "central" not in p:
            raise ConfigError(f"Material profile '{pname}' needs a 'central' scenario")
        for scen in SCENARIOS:
            shares = p.get(scen)
            if shares is None:
                continue
            validate_profile_shares(f"{pname}.{scen}", shares)
            for mat in shares:
                if mat not in factors:
                    raise ConfigError(
                        f"Profile '{pname}.{scen}' uses material '{mat}', which is not in "
                        "warm_factors.yaml. Add the official WARM factor (do not guess)."
                    )
                for prac in needed_practices:
                    if factors[mat].get(prac) is None:
                        raise ConfigError(
                            f"WARM has no '{prac}' factor for '{mat}' (used by profile '{pname}')"
                        )

    for rule in cfg.materials.get("keyword_rules", []):
        if rule["profile"] not in cfg.profiles:
            raise ConfigError(f"Keyword rule points to unknown profile '{rule['profile']}'")
