"""Read the raw Master Shipment List CSV and clean it. Never modifies the raw file."""
from __future__ import annotations

import datetime as dt
import math
import re
from pathlib import Path

import pandas as pd

from greenprints.config import Config

EXPECTED_COLUMNS = [
    "Chapters", "Shipping Destination", "Date of Shipment", "Sponsor", "Recipient Name",
    "Transportation", "Liability Covered", "Insurance", "Poundage of shipments (lbs)",
    "Estimated Shipment Valuation", "Shipment Cost", "Number of Boxes", "Number of Pallets",
    "Transport Size", "HQ VPO", "COO/CP", "Shipment Type", "Comments",
    "Link to documentation of shipment",
]
REQUIRED_COLUMNS = [
    "Chapters", "Shipping Destination", "Date of Shipment", "Recipient Name",
    "Poundage of shipments (lbs)", "Number of Boxes", "Number of Pallets",
    "Shipment Type", "Comments",
]
NUMERIC_COLUMNS = {
    "Poundage of shipments (lbs)": "weight_lbs_recorded",
    "Estimated Shipment Valuation": "valuation_usd",
    "Shipment Cost": "shipment_cost_usd",
    "Number of Boxes": "boxes",
    "Number of Pallets": "pallets",
}

EXPORT_INSTRUCTIONS = """\
The shipment data file was not found at:
    {path}

How to export it from Google Sheets:
  1. Open the Google Sheet "Master Shipment Database".
  2. Click the tab "[OLD] Master Shipment List <11/04/2026" at the bottom
     (for later years: the tab that holds the full shipment list).
  3. File > Download > Comma Separated Values (.csv).
     (This downloads ONLY the tab you have open.)
  4. Rename the downloaded file to:  master_shipments.csv
  5. Move it into the folder:        greenprints/data/raw/
  6. Run again:  python -m greenprints run
"""

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
_MONTH_YEAR = re.compile(r"^([A-Za-z]+)\.?[\s,\-/]*(\d{4})$")
_YEAR_MONTH_NAME = re.compile(r"^(\d{4})[\s,\-/]*([A-Za-z]+)\.?$")
_NUMERIC_DATE = re.compile(r"^(\d{1,2})[/\-](?:(\d{1,2})[/\-])?(\d{2}|\d{4})$")
_ISO_DATE = re.compile(r"^(\d{4})-(\d{1,2})(?:-(\d{1,2}))?")
_NA_TOKENS = {"", "n/a", "na", "none", "null", "-", "--", "tbd", "?", "unknown", "nan"}


class RawDataMissing(FileNotFoundError):
    pass


# ---------------------------------------------------------------------------
# Parsers (pure functions, unit tested)
# ---------------------------------------------------------------------------
def _month_from_name(name: str) -> int | None:
    key = name.strip().lower()[:3]
    if len(name.strip()) < 3:
        return None
    return _MONTHS.get(key)


def _full_year(y: str) -> int:
    year = int(y)
    return year + 2000 if year < 100 else year


def parse_month_year(value) -> dt.date | None:
    """Parse month-year text such as 'September 2023', 'Nov 2017', 'May2024'
    to the first of that month. Returns None for blanks or unparseable text."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if isinstance(value, dt.datetime):
        return value.date().replace(day=1)
    if isinstance(value, dt.date):
        return value.replace(day=1)
    s = " ".join(str(value).split())
    if not s:
        return None
    try:
        m = _MONTH_YEAR.match(s)
        if m:
            month = _month_from_name(m.group(1))
            return dt.date(int(m.group(2)), month, 1) if month else None
        m = _YEAR_MONTH_NAME.match(s)
        if m:
            month = _month_from_name(m.group(2))
            return dt.date(int(m.group(1)), month, 1) if month else None
        m = _ISO_DATE.match(s)
        if m:
            return dt.date(int(m.group(1)), int(m.group(2)), 1)
        m = _NUMERIC_DATE.match(s)
        if m:  # M/YYYY or M/D/YYYY (US order)
            return dt.date(_full_year(m.group(3)), int(m.group(1)), 1)
    except ValueError:
        return None
    return None


def parse_number(value) -> float:
    """Parse '7,140.00', '$124,379.99', '12' etc. Returns NaN for blanks, N/A and
    any text that is not purely a number (e.g. 'N/A, see notes')."""
    if value is None:
        return math.nan
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if s.lower() in _NA_TOKENS:
        return math.nan
    s = s.replace("$", "").replace(",", "").replace(" ", "")
    negative = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        n = float(s)
    except ValueError:
        return math.nan
    return -n if negative else n


def is_non_numeric_text(value) -> bool:
    """True if a cell holds text that is neither blank/N/A nor a number."""
    if value is None:
        return False
    s = str(value).strip()
    return s.lower() not in _NA_TOKENS and math.isnan(parse_number(s))


def academic_year(d: dt.date, start_month: int = 9) -> str:
    start = d.year if d.month >= start_month else d.year - 1
    return f"{start}-{(start + 1) % 100:02d}"


def normalize_text(value) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return ""
    return " ".join(str(value).split())


# ---------------------------------------------------------------------------
# Reading + cleaning
# ---------------------------------------------------------------------------
def read_raw(path: Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise RawDataMissing(EXPORT_INSTRUCTIONS.format(path=path))
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df.columns = [normalize_text(c) for c in df.columns]

    # Some exports put a title row above the header; find the real header row.
    if not set(REQUIRED_COLUMNS).issubset(df.columns):
        raw = pd.read_csv(path, dtype=str, keep_default_na=False, header=None,
                          encoding="utf-8-sig")
        for i in range(min(10, len(raw))):
            cols = [normalize_text(c) for c in raw.iloc[i]]
            if set(REQUIRED_COLUMNS).issubset(cols):
                df = raw.iloc[i + 1:].reset_index(drop=True)
                df.columns = cols
                df.attrs["header_offset"] = i
                break
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"The CSV is missing required columns: {missing}. "
            f"Columns found: {list(df.columns)}. Did you export the right tab?"
        )
    return df


def clean(raw: pd.DataFrame, cfg: Config) -> tuple[pd.DataFrame, list[dict]]:
    """Return (all shipment rows with parsed fields, data-quality issues).

    Blank spacer rows and the totals row are removed (and logged). Rows with an
    unparseable date are kept with date=NaT and logged; the date filter later
    excludes them from totals.
    """
    issues: list[dict] = []
    df = raw.copy()
    header_offset = raw.attrs.get("header_offset", 0)
    # Spreadsheet row number: header is row 1 (+ any title rows above it).
    df.insert(0, "sheet_row", df.index + 2 + header_offset)

    text_cols = [c for c in df.columns if c != "sheet_row"]
    for c in text_cols:
        df[c] = df[c].map(normalize_text)

    aliases = {k.lower(): v for k, v in (cfg.settings.get("chapter_aliases") or {}).items()}
    df["Chapters"] = df["Chapters"].map(lambda s: aliases.get(s.lower(), s))

    # --- drop blank spacer rows and totals rows ---------------------------
    is_blank = (df[text_cols] == "").all(axis=1)
    identity_cols = ["Chapters", "Shipping Destination", "Recipient Name", "Date of Shipment"]
    no_identity = (df[identity_cols] == "").all(axis=1)
    is_totals = no_identity & ~is_blank
    for _, r in df[is_totals].iterrows():
        issues.append(_issue(r, "excluded_totals_row",
                             f"Row with no date/chapter/destination/recipient excluded "
                             f"(looks like a totals row; weight cell = "
                             f"'{r['Poundage of shipments (lbs)']}')"))
    n_blank = int(is_blank.sum())
    df = df[~is_blank & ~is_totals].copy()

    # --- dates -------------------------------------------------------------
    df["date"] = pd.to_datetime(df["Date of Shipment"].map(parse_month_year))
    for _, r in df[df["date"].isna()].iterrows():
        raw_d = r["Date of Shipment"]
        issues.append(_issue(
            r, "unparseable_date",
            "Date is blank" if raw_d == "" else f"Could not read date '{raw_d}'"))

    start_month = int(cfg.settings.get("academic_year_start_month", 9))
    df["academic_year"] = df["date"].map(
        lambda d: academic_year(d, start_month) if pd.notna(d) else "")
    df["calendar_year"] = df["date"].dt.year.astype("Int64")

    # --- numbers -----------------------------------------------------------
    for col, new in NUMERIC_COLUMNS.items():
        if col not in df.columns:
            df[new] = math.nan
            continue
        df[new] = df[col].map(parse_number)
        for _, r in df[df[col].map(is_non_numeric_text)].iterrows():
            issues.append(_issue(r, "non_numeric_value",
                                 f"'{col}' contains text, treated as blank: '{r[col]}'"))

    # A recorded weight of 0 (or negative) is not a real weight: treat as missing.
    bad_w = df["weight_lbs_recorded"] <= 0
    for _, r in df[bad_w].iterrows():
        issues.append(_issue(r, "zero_weight",
                             f"Weight recorded as '{r['Poundage of shipments (lbs)']}', "
                             "treated as missing"))
    df.loc[bad_w, "weight_lbs_recorded"] = math.nan

    df["shipment_type"] = df["Shipment Type"]
    df["chapter"] = df["Chapters"]
    df["destination"] = df["Shipping Destination"]
    df["recipient"] = df["Recipient Name"]

    df.attrs["n_blank_rows"] = n_blank
    df.attrs["n_totals_rows"] = int(is_totals.sum())
    return df.reset_index(drop=True), issues


def filter_dates(df: pd.DataFrame, start: dt.date, end: dt.date) -> pd.DataFrame:
    """Keep rows with start <= date <= end (inclusive). Rows without a date are dropped."""
    mask = (df["date"] >= pd.Timestamp(start)) & (df["date"] <= pd.Timestamp(end))
    return df[mask].copy().reset_index(drop=True)


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
