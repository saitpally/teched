# Project Greenprints

This tool estimates the **greenhouse gas emissions avoided** by Blueprints for Pangaea
(B4P) shipments, measured in metric tons of CO2 equivalent (MTCO2e). It uses the
EPA's Waste Reduction Model (WARM).

You give it the shipment spreadsheet. It gives you:

| File (in `data/processed/`) | What it is |
|---|---|
| `greenprints_results.xlsx` | The main results: summary, by year, by type, by destination, by material, every shipment, every assumption, data problems |
| `shipments_clean.csv` | One cleaned row per shipment with its emissions numbers |
| `data_quality_report.md` | Rows in the sheet that need a human to fix or confirm |
| `METHODOLOGY.md` | Plain-English explanation of the method (also copied to the main folder) |

There's also an interactive dashboard (see step 5).

You don't need to know Python. Follow the steps below exactly, typing each command
into the **Terminal** app (Mac) or **Command Prompt** (Windows).

---

## One-time setup (about 5 minutes)

1. **Install Python** (3.9 or newer) from <https://www.python.org/downloads/> if you don't
   have it. On Windows, tick **"Add Python to PATH"** during install.
2. **Open a terminal in the `greenprints` folder.**
   - Mac: open Terminal, type `cd ` (with a space), drag the `greenprints` folder onto the
     window, then press Enter.
   - Windows: open the folder in File Explorer, click the address bar, type `cmd`, press Enter.
3. **Create a private Python environment and install the tool:**

   Mac / Linux:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
   Windows:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

Each time you open a **new** terminal later, re-run only the `activate` line
(`source .venv/bin/activate` or `.venv\Scripts\activate`). You'll see `(.venv)` at the
start of the line when it's active.

---

## Every year: re-run the numbers

### 1. Export the shipment data from Google Sheets
1. Open the Google Sheet **"Master Shipment Database"**.
2. Click the tab that holds the full shipment list. For the 2023-2026 report this was
   **"[OLD] Master Shipment List <11/04/2026"**.
3. Go to **File → Download → Comma Separated Values (.csv)**. This downloads only the tab
   that's open.
4. Rename the downloaded file to exactly **`master_shipments.csv`**.
5. Move it into **`greenprints/data/raw/`**, replacing last year's file.

Never edit this file by hand. Fix problems in the Google Sheet and export again.

The tool expects the same column names as the current sheet (`Date of Shipment`,
`Poundage of shipments (lbs)`, `Number of Boxes`, `Number of Pallets`, `Shipment Type`,
`Comments`, and so on). If someone renames a column, the tool will stop and tell you which
one is missing.

### 2. Set the date range
Open **`config/settings.yaml`** in any text editor (TextEdit, Notepad, VS Code) and change:
```yaml
date_range:
  start: 2023-09-01
  end: 2026-09-30
```
Also update the `sanity_check` numbers below it (expected row count and pounds) if you know
them, or delete the whole `sanity_check:` block.

### 3. Run it
```
python -m greenprints run
```
It prints the headline numbers and writes everything to `data/processed/`. If you see
`CHECK` lines, the totals differ from what `sanity_check` expected. Open
`data/processed/data_quality_report.md` to see why.

### 4. Fix data problems and re-run
Open `data/processed/data_quality_report.md`. The most important sections are at the top:
- **Missing weights**: shipments with no weight *and* no box/pallet count. These are **not**
  counted at all, so fill in a weight in the sheet.
- **Unparseable dates**: write the date like `September 2025` in the sheet.
- **Shipment Type to double-check**: for example, a Michigan clinic marked National. The tool
  never changes these itself.
- **Unusually heavy shipments** and **possible duplicates**: confirm they're right.

Fix the Google Sheet, export again (step 1), and re-run (step 3).

### 5. Open the dashboard
```
streamlit run app/dashboard.py
```
A browser tab opens. Use the left sidebar to change the date range, the baseline (landfill
or combustion), the material scenario (low, central, high) and whether to include estimated
weights. Press `Ctrl+C` in the terminal to stop it.

### 6. (Optional) Check the tool still works
```
pytest
```
Every test should pass.

---

## Changing the assumptions (no coding needed)

All numbers live in the `config/` folder. Edit them in a text editor, save, and re-run
step 3. `METHODOLOGY.md` and the Excel **Assumptions** sheet update automatically.

| I want to... | Edit this |
|---|---|
| Change the date range | `config/settings.yaml` → `date_range` |
| Change lbs per box / per pallet used for missing weights | `config/settings.yaml` → `estimation` |
| Change what supplies are assumed to be made of | `config/material_profiles.yaml` → `profiles` |
| Make a keyword map to a different profile | `config/material_profiles.yaml` → `keyword_rules` |
| Use a new EPA WARM version | `config/warm_factors.yaml` (replace the **whole** table plus `warm_version`) |

**Updating material profiles after sampling real boxes.** Weigh the contents of several
typical boxes by material (plastic, cardboard, metal, paper), work out each material's share
of the total weight, and enter the shares under `central:`. Shares must add up to exactly
1.0, or the tool stops with an error telling you which profile is off. Material names must
match a name in `warm_factors.yaml` exactly.

**Adding a keyword.** Rules are checked top to bottom, and the first match wins. Separate
alternatives with `|`. For example, to send "syringe" to surgical supplies:
```yaml
  - profile: surgical_supplies
    pattern: "surgical|surgial|syringe"
```

**Never type in an emission factor you didn't copy from an official EPA WARM document.**

---

## How it works (for the curious)

```
data/raw/master_shipments.csv
   → load.py        clean dates, numbers, whitespace; drop blank and totals rows
   → estimate.py    fill missing weights from box/pallet counts
   → materials.py   pick a material profile from keywords in Comments/Recipient/Destination
   → emissions.py   avoided MTCO2e = short tons × (EF_baseline − EF_source_reduction)
   → quality.py     flag odd types, outliers, duplicates
   → report.py      Excel, CSV, data-quality report, METHODOLOGY.md
```
See `METHODOLOGY.md` for the method and `ASSUMPTIONS.md` for every judgment call.
