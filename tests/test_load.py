import datetime as dt
import math

import pandas as pd
import pytest

from greenprints.estimate import estimate_weight
from greenprints.load import academic_year, filter_dates, parse_month_year, parse_number


@pytest.mark.parametrize("text,expected", [
    ("May2024", dt.date(2024, 5, 1)),
    ("Nov 2017", dt.date(2017, 11, 1)),
    ("September 2023", dt.date(2023, 9, 1)),
    ("  Sept 2023 ", dt.date(2023, 9, 1)),
    ("sep. 2025", dt.date(2025, 9, 1)),
    ("9/2024", dt.date(2024, 9, 1)),
])
def test_parse_month_year(text, expected):
    assert parse_month_year(text) == expected


@pytest.mark.parametrize("text", ["", "   ", None, "Sumtember 2024", "TBD", "2024"])
def test_parse_month_year_blank_or_bad(text):
    assert parse_month_year(text) is None


@pytest.mark.parametrize("text,expected", [
    ("7,140.00", 7140.0),
    ("$124,379.99", 124379.99),
    (" 12 ", 12.0),
    ("0", 0.0),
])
def test_parse_number(text, expected):
    assert parse_number(text) == pytest.approx(expected)


@pytest.mark.parametrize("text", ["N/A", "", "  ", "N/A, see notes", None, "na"])
def test_parse_number_blank(text):
    assert math.isnan(parse_number(text))


def test_estimate_four_pallets():
    assert estimate_weight(4, float("nan"), 489.14, 39.4) == pytest.approx(1956.56)


def test_estimate_uses_config_constants(cfg):
    est = cfg.settings["estimation"]
    assert estimate_weight(4, float("nan"), est["lbs_per_pallet"],
                           est["lbs_per_box"]) == pytest.approx(1956.56)
    assert estimate_weight(0, 10, est["lbs_per_pallet"], est["lbs_per_box"]) == \
        pytest.approx(394.0)
    assert math.isnan(estimate_weight(float("nan"), float("nan"), 489.14, 39.4))


def test_date_filter_inclusive_both_ends():
    df = pd.DataFrame({"date": pd.to_datetime([
        "2023-08-01", "2023-09-01", "2025-01-01", "2026-09-01", "2026-10-01", None])})
    out = filter_dates(df, dt.date(2023, 9, 1), dt.date(2026, 9, 30))
    assert list(out["date"].dt.strftime("%Y-%m")) == ["2023-09", "2025-01", "2026-09"]


def test_academic_year():
    assert academic_year(dt.date(2023, 9, 1)) == "2023-24"
    assert academic_year(dt.date(2024, 8, 1)) == "2023-24"
    assert academic_year(dt.date(2026, 9, 1)) == "2026-27"
