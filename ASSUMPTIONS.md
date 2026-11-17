# Assumptions and judgment calls

Choices made while building the MVP, where the brief left room for interpretation. Every
numeric assumption lives in `config/`; this file explains the *why*.

## Environment
- **Python 3.9+ instead of 3.11+.** The build machine only had Python 3.9.6. The code uses
  nothing 3.11-specific, so it runs on 3.9, 3.10, 3.11, 3.12 and later. `pyproject.toml`
  declares `requires-python >= 3.9`.
- `requirements.txt` ends with `-e .`, which installs the project itself so that
  `python -m greenprints run` works from any folder.
- `data/raw/*.csv` and `data/processed/` are in `.gitignore`. The shipment sheet names
  recipients and partner clinics, so keep it out of public repositories.

## Data cleaning
- **Dates** are month + year only. Each shipment is dated to the **1st of its month**. Accepted
  formats: `September 2023`, `Sept 2023`, `Nov 2017`, `May2024`, `9/2024`, `2024-09`.
  Anything else (including blanks) is listed under "Unparseable dates" and left out of totals,
  because we can't tell which period it belongs to.
- **Date filter**: inclusive at both ends (`2023-09-01` to `2026-09-30`). Because dates are
  month-level, that means September 2023 through September 2026: **37 months, not 36**.
  September 2026 therefore shows up as a one-month "2026-27" academic year. To report only
  three whole academic years, change `date_range.end` to `2026-08-31`.
- **A totals row** is any row with no date, chapter, destination *or* recipient but with
  something else filled in (for example `264,896.00`). **Blank spacer rows** have every cell
  empty. Both are removed. The totals row is listed in the report; blank rows are only counted.
- **A recorded weight of 0 (or negative) is treated as missing**, then estimated from box/pallet
  counts if those exist. A real shipment can't weigh 0 lbs.
- **Number cells holding text** (for example `N/A, see notes` in Number of Boxes) are treated as
  blank and listed in the report, so the note can be read by a person.
- **Chapter names**: whitespace is trimmed everywhere, and names are matched case-insensitively
  through `chapter_aliases` in `settings.yaml` (`umich` → `UMich`).
- **Shipment Type is never changed.** Rows are flagged for review when:
  - the type is not Local, National or International; or
  - the row is National/International but the destination or recipient mentions a Michigan
    place (list in `michigan_patterns`); or
  - the row is Local but nothing mentions a Michigan place. This check is noisy on purpose,
    since many local clinic names don't include a city.
- **Duplicates** = same month, destination, recipient and weight.
- **Outliers** = weight more than 3× the median for the same Shipment Type, within the date
  range. They're flagged, not removed.

## Missing weights
- The formula follows the brief exactly: `pallets × 489.14 + boxes × 39.4`. If a row has
  **both** pallets and boxes, the boxes may already be on the pallets, so this could count them
  twice. Those rows get a note in the data-quality report so a person can check them.
- Rows with neither weight nor counts are **excluded from totals** (not zero-filled) and listed
  first in the data-quality report.

## Material profiles
- **Matching**: case-insensitive regular expressions. A few short words use word boundaries,
  so `cane` doesn't match "Hurricane" and `PPE`/`DME` don't match inside other words. I also
  added `durable medical` to the durable-medical-equipment rule so the FAJR row
  ("durable medical equipment") is caught. The rules are checked in order (first match wins).
  Within a rule, the columns are checked in the order Comments → Recipient Name → Shipping
  Destination. The matched text and column are saved on every row.
- **Low / central / high scenarios exist for every profile**, not just the default. Otherwise
  keyword-matched shipments would show no uncertainty at all. Central values are exactly the
  ones given in the brief.
- **How low/high were built**: only the cardboard/paper share moves, and the ratio between the
  remaining materials stays fixed.
  - Supplies profiles (mixed, surgical, PPE): ±10–15 percentage points of cardboard.
  - Equipment profiles: about −4.5 / +9 points.
  - Absorbent/textiles: ±15 points of paper.

  Cardboard/paper has the largest WARM benefit under **both** landfill and combustion
  baselines, so this guarantees low ≤ central ≤ high under either baseline (there's a test for
  it). Shifting plastics against metals would not, because their order flips between landfill
  (metals higher) and combustion (plastics higher).
- These are **placeholders**. Replace them with real sample weights when B4P sorts boxes.

## Emissions
- **Headline** = landfilling baseline, central scenario. **Sensitivity** = combustion baseline.
  Every baseline × scenario combination is calculated and saved in `shipments_clean.csv`.
- **The "landfill-only" number** is called *disposal-only* in the outputs:
  `short tons × EF_baseline`. It is calculated for each baseline. The Summary sheet also shows
  how much of the headline benefit comes from avoided manufacturing
  (`1 − disposal-only / avoided`).
- **Freight**: `emissions.transport_mtco2e()` returns 0 and raises an error if
  `transport.enabled` is switched on before a method is written. That way nobody can turn it on
  by accident and get silently wrong numbers.
- Missing-weight rows have empty emissions (NaN) and add nothing to the sums.

## Sanity check
- The expected totals from the brief (46 rows, 83,444 recorded lbs, split by type) are stored
  under `sanity_check` in `settings.yaml`. Every run compares against them (±5%) and prints
  `CHECK` lines if they drift. Update or delete that block when the date range changes.
