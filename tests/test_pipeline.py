"""End-to-end run on a small synthetic CSV that reproduces the sheet's quirks."""
import pandas as pd
import pytest

from greenprints.cli import run
from greenprints.config import load_config
from greenprints.pipeline import build


@pytest.fixture
def result(sample_project):
    cfg = load_config(sample_project)
    cfg.settings["sanity_check"] = None
    return build(cfg)


def test_rows_and_filtering(result):
    s = result.shipments
    # In range: Sep 2023, May 2024, Jan 2025, Mar 2026, Jun 2026, Sep 2026
    assert len(s) == 6
    assert result.stats["blank_rows_removed"] == 1
    assert result.stats["totals_rows_removed"] == 1
    assert result.stats["undated_rows"] == 1
    assert set(s["chapter"]) == {"UMich"}
    assert "Lebanon" in set(s["destination"])


def test_weight_sources(result):
    s = result.shipments.set_index("recipient")
    assert s.loc["Clinic Two", "weight_source"] == "estimated_from_counts"
    assert s.loc["Clinic Two", "weight_lbs"] == pytest.approx(1956.56)
    assert s.loc["FAJR", "weight_source"] == "missing"
    # weight "0" with 5 boxes -> estimated from boxes
    assert s.loc["Edge Clinic End", "weight_lbs"] == pytest.approx(5 * 39.4)
    assert s.loc["Beirut Hospital", "weight_lbs"] == pytest.approx(7140)


def test_profiles_and_keywords(result):
    s = result.shipments.set_index("recipient")
    assert s.loc["Hope Clinic", "material_profile"] == "ppe"
    assert s.loc["Beirut Hospital", "material_profile"] == "surgical_supplies"
    assert s.loc["Beirut Hospital", "matched_keyword"] == "surgial"
    assert s.loc["FAJR", "material_profile"] == "durable_medical_equipment"
    assert s.loc["Edge Clinic End", "material_profile"] == "absorbent_and_textiles"
    assert s.loc["Clinic Two", "material_profile"] == "mixed_medical_supplies"
    assert s.loc["Clinic Two", "matched_keyword"] == ""


def test_data_quality_flags(result):
    cats = result.issues.groupby("category")["recipient"].apply(set).to_dict()
    assert "FAJR" in cats["missing_weight"]
    assert "Bad Date Clinic" in cats["unparseable_date"]
    assert "Detroit Free Clinic" in cats["odd_shipment_type"]
    assert "Clinic Two" in cats["estimated_weight"]
    assert "Beirut Hospital" in cats["non_numeric_value"]
    assert len(cats["excluded_totals_row"]) == 1
    # Out-of-range rows must not clutter the report
    assert "Old Clinic" not in set(result.issues["recipient"])


def test_emission_columns(result):
    s = result.shipments
    hope = s[s["recipient"] == "Hope Clinic"].iloc[0]
    # 1 short ton of ppe central: 0.85*1.89 + 0.15*5.76
    assert hope["avoided_mtco2e_landfilling_central"] == pytest.approx(0.85 * 1.89 + 0.15 * 5.76)
    assert (s["avoided_mtco2e_landfilling_low"].sum()
            < s["avoided_mtco2e_landfilling_central"].sum()
            < s["avoided_mtco2e_landfilling_high"].sum())


def test_cli_writes_outputs(sample_project):
    assert run(sample_project) == 0
    out = sample_project / "data" / "processed"
    for f in ["shipments_clean.csv", "greenprints_results.xlsx", "data_quality_report.md",
              "METHODOLOGY.md"]:
        assert (out / f).exists(), f
    assert (sample_project / "METHODOLOGY.md").exists()
    xl = pd.ExcelFile(out / "greenprints_results.xlsx")
    assert xl.sheet_names == ["Summary", "By Year", "By Shipment Type", "By Destination",
                              "By Material Profile", "Shipment Detail", "Assumptions",
                              "Data Quality"]
    clean = pd.read_csv(out / "shipments_clean.csv")
    for c in ["date", "academic_year", "weight_lbs", "weight_source", "material_profile",
              "matched_keyword", "short_tons", "avoided_mtco2e_central", "avoided_mtco2e_low",
              "avoided_mtco2e_high", "avoided_mtco2e_combustion_central",
              "disposal_only_mtco2e_landfilling_central"]:
        assert c in clean.columns, c


def test_missing_raw_file_gives_instructions(sample_project, capsys):
    (sample_project / "data" / "raw" / "master_shipments.csv").unlink()
    assert run(sample_project) == 3
    assert "File > Download > Comma Separated Values" in capsys.readouterr().err
