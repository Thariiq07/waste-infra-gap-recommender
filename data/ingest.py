"""
data/ingest.py

Standalone, documented data-ingestion pipeline for the Waste Infrastructure Gap
Recommender. Ports the data-cleaning and feature-engineering steps from the
originating thesis (Colab notebook) into a runnable script.

Produces three cleaned, feature-engineered tables:
  - Local Authority level  (31 areas)       -> data/processed/la_features.csv
  - Electoral Division level (3,417 areas)  -> data/processed/ed_features.csv
  - EPA facility counts per local authority -> data/processed/facility_counts.csv

Source datasets (place in data/raw/, gitignored):
  - CSO Census 2022, county level:      SAPS_2022_county_270923.csv
  - Pobal HP Deprivation Index 2022:    hp-deprivation-index-scores-2022.csv
  - EPA Licensed Waste Facilities:      LicensedFacilities_<date>.zip, unzipped
                                         (needs geopandas: pip install geopandas)

Run:
    python data/ingest.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).parent / "raw"
PROCESSED_DIR = Path(__file__).parent / "processed"

SAPS_COUNTY_CSV = RAW_DIR / "SAPS_2022_county_270923.csv"
POBAL_ED_CSV = RAW_DIR / "hp-deprivation-index-scores-2022.csv"
EPA_FACILITIES_SHP = RAW_DIR / "LicensedFacilities_16062026" / "LicensedFacilities_Waste_16062026.shp"


# ---------------------------------------------------------------------------
# GEOGID -> Local Authority name
# ---------------------------------------------------------------------------
# The CSO county-level SAPS file only carries 2-letter GEOGID codes (GEOGDESC
# duplicates GEOGID rather than spelling out the name), so the original
# notebook must have had its own lookup table to turn codes like "DC" into
# "Dublin City". This mapping is reconstructed from the standard CSO county
# geography codes and has NOT been verified against the original notebook —
# double-check it once the notebook is available, particularly DR (Dún
# Laoghaire-Rathdown) and WH (Westmeath), which are less commonly seen codes.
GEOGID_TO_LOCAL_AUTHORITY = {
    "DC": "Dublin City",
    "CC": "Cork City",
    "GC": "Galway City",
    "LS": "Laois",
    "LM": "Leitrim",
    "LK": "Limerick",
    "LD": "Longford",
    "LH": "Louth",
    "CW": "Carlow",
    "MO": "Mayo",
    "MH": "Meath",
    "MN": "Monaghan",
    "OY": "Offaly",
    "RN": "Roscommon",
    "SO": "Sligo",
    "TY": "Tipperary",
    "WD": "Waterford",
    "WH": "Westmeath",
    "WX": "Wexford",
    "CN": "Cavan",
    "WW": "Wicklow",
    "DR": "Dún Laoghaire-Rathdown",
    "FL": "Fingal",
    "SD": "South Dublin",
    "CE": "Clare",
    "CK": "Cork County",
    "DL": "Donegal",
    "GY": "Galway County",
    "KY": "Kerry",
    "KE": "Kildare",
    "KK": "Kilkenny",
}


def load_la_features(saps_csv: Path = SAPS_COUNTY_CSV) -> pd.DataFrame:
    """
    Local Authority level (n=31) feature engineering.

    Reproduces the four proxy features selected in the thesis (Section 3.4)
    from raw CSO Census 2022 county-level tables, after correlation analysis
    narrowed sixteen candidate variables down to these four:

      - internet_rate:      T15_2_T / T5_1T_H          (broadband access rate)
      - professional_rate:  (T9_2_HA+T9_2_HB+T9_2_HC) / T5_1T_H  (higher/lower
                             professional + managerial occupation rate)
      - ownership_rate:      (T6_3_OOH+T6_3_OMLH) / T5_1T_H  (owned outright +
                             owned with mortgage/loan)
      - total_households:    T5_1T_H

    A fifth candidate, multiple-car-ownership rate, was excluded in the
    thesis for being highly correlated with ownership_rate, so it is not
    computed here.
    """
    df = pd.read_csv(saps_csv)

    # Drop the national "Ireland" total row (GEOGID == "Ireland") — the
    # analysis operates over the 31 local authorities only.
    df = df[df["GEOGID"] != "Ireland"].copy()

    out = pd.DataFrame()
    out["geogid"] = df["GEOGID"]
    out["local_authority"] = df["GEOGID"].map(GEOGID_TO_LOCAL_AUTHORITY)

    if out["local_authority"].isna().any():
        missing = out.loc[out["local_authority"].isna(), "geogid"].tolist()
        raise ValueError(
            f"GEOGID_TO_LOCAL_AUTHORITY is missing an entry for: {missing}. "
            "Update the mapping at the top of this file."
        )

    out["internet_rate"] = df["T15_2_T"] / df["T5_1T_H"]
    out["professional_rate"] = (
        df["T9_2_HA"] + df["T9_2_HB"] + df["T9_2_HC"]
    ) / df["T5_1T_H"]
    out["ownership_rate"] = (df["T6_3_OOH"] + df["T6_3_OMLH"]) / df["T5_1T_H"]
    out["total_households"] = df["T5_1T_H"]

    return out.reset_index(drop=True)


def load_ed_features(pobal_csv: Path = POBAL_ED_CSV) -> pd.DataFrame:
    """
    Electoral Division level (n=3,417) feature engineering.

    At this finer scale, the thesis draws five features directly from the
    Pobal HP Deprivation Index dataset rather than re-deriving them from raw
    census tables (Section 3.4), since internet_rate and total_households as
    derived at LA level aren't available in the same form at ED level:

      - higher_professional_rate:  HLPROF22
      - third_level_education_rate: EDHIGH22
      - owner_occupation_rate:      OWNOCC22
      - total_population:           TOTPOP22
      - pobal_index_score:          Index22_ED_std_rel_wt  (standardised
                                     relative-weighted Pobal HP score; positive
                                     = more affluent, negative = more deprived)
    """
    # The Pobal file is encoded cp1252/latin-1, not UTF-8 (it contains fada
    # characters in Irish place names, e.g. "Dún Laoghaire").
    df = pd.read_csv(pobal_csv, encoding="cp1252")

    out = pd.DataFrame()
    out["ed_id"] = df["ED_ID_STR"]
    out["ed_name"] = df["ED_ENGLISH"]
    out["higher_professional_rate"] = df["HLPROF22"]
    out["third_level_education_rate"] = df["EDHIGH22"]
    out["owner_occupation_rate"] = df["OWNOCC22"]
    out["total_population"] = df["TOTPOP22"]
    out["pobal_index_score"] = df["Index22_ED_std_rel_wt"]

    return out.reset_index(drop=True)


EWASTE_NAME_KEYWORDS = [
    "recycl", "civic amenity", "electronic", "weee", "e-waste",
    "environmental", "transfer station", "recovery",
]

# Facilities that match a keyword above (e.g. contain "recovery") but were
# manually reviewed and excluded as not actually e-waste relevant (mostly
# soil/inert-waste recovery facilities).
EWASTE_NAME_EXCLUSIONS = [
    "Blackhall Soil Recovery Facility",
    "Brownswood Inert Waste Recovery Facility",
    "Huntstown Inert Waste Recovery Facility",
    "Glassco Recycling Limited",
]

# Facility addresses are free text (e.g. "116 Sheriff Street Upper, Dublin 1,
# Dublin"), not a structured county field, so county is recovered by scanning
# the comma-separated parts of the address, from the end, for a recognisable
# county name. Note "Dublin" alone (with no Fingal/South Dublin/Dún
# Laoghaire-Rathdown qualifier in the address) always maps to Dublin City
# ("DC") here — this is a real limitation of the source data, not a bug, and
# it's part of why Fingal, South Dublin and Dún Laoghaire-Rathdown show zero
# facilities despite likely having some: any facility whose address just says
# "Dublin" can't be distinguished between the four Dublin local authorities.
COUNTY_NAME_TO_GEOGID = {
    "Dublin": "DC", "Cork": "CC", "Kildare": "KE", "Kerry": "KY",
    "Meath": "MH", "Wicklow": "WX", "Cavan": "CN", "Waterford": "WD",
    "Leitrim": "LM", "Donegal": "DL", "Wexford": "WX", "Roscommon": "RN",
    "Clare": "CE", "Louth": "LH", "Mayo": "MO", "Laois": "LS",
    "Westmeath": "WH", "Kilkenny": "KK", "Galway": "GY", "Monaghan": "MN",
    "Carlow": "CW", "Tipperary": "TY", "Offaly": "OY", "Limerick": "LK",
    "Sligo": "SO", "Longford": "LD", "Antrim": "AN", "Tyrone": "TE",
    "Cork City": "CC", "Dublin City": "DC",
}


def _extract_county_geogid(address: str) -> str | None:
    """Scan an address's comma-separated parts, from the end, for a county name."""
    import re

    if pd.isna(address):
        return None
    parts = [p.strip() for p in str(address).split(",")]
    for part in reversed(parts):
        if not re.search(r"\d", part) and len(part) > 3:
            for county_name, geogid in COUNTY_NAME_TO_GEOGID.items():
                if county_name.lower() in part.lower():
                    return geogid
            return part  # unrecognised, kept as-is rather than dropped
    return None


def load_epa_facilities(shp_path: Path = EPA_FACILITIES_SHP) -> pd.DataFrame:
    """
    EPA Licensed Waste Facilities loader.

    Loads the EPA Licensed Waste Facilities shapefile (114 facilities of all
    types — landfills, transfer stations, recycling, etc.), filters it down
    to the e-waste-relevant subset the way the thesis notebook did, and
    counts the result per local authority.

    Filtering is name-based rather than by a formal licence-class code: a
    facility is kept if its `Name` contains any of EWASTE_NAME_KEYWORDS,
    minus a short manually-reviewed exclusion list (EWASTE_NAME_EXCLUSIONS)
    of keyword matches that turned out not to be e-waste relevant on
    inspection (e.g. "Blackhall Soil Recovery Facility" matches "recovery"
    but handles soil, not e-waste). This reproduces the thesis's reported
    figure of 26 e-waste-relevant facilities exactly.

    Returns a DataFrame indexed by `geogid` with a `facility_count` column,
    zero-filled for every local authority with no matching facility.
    """
    import geopandas as gpd

    if not shp_path.exists():
        zip_path = RAW_DIR / f"{shp_path.parent.name}.zip"
        if zip_path.exists():
            import zipfile

            # The zip's own top-level entry already matches shp_path.parent's
            # name, so extract into RAW_DIR directly rather than nesting it
            # inside another folder of the same name.
            with zipfile.ZipFile(zip_path) as z:
                z.extractall(RAW_DIR)
        else:
            raise FileNotFoundError(
                f"Neither {shp_path} nor {zip_path} exists. Place the EPA "
                "licensed facilities zip in data/raw/."
            )

    facilities = gpd.read_file(shp_path)

    is_relevant = facilities["Name"].str.lower().apply(
        lambda name: any(kw in name for kw in EWASTE_NAME_KEYWORDS)
    )
    relevant = facilities[is_relevant]
    relevant = relevant[~relevant["Name"].isin(EWASTE_NAME_EXCLUSIONS)].copy()

    relevant["geogid"] = relevant["Address"].apply(_extract_county_geogid)

    counts = (
        relevant["geogid"]
        .value_counts()
        .rename("facility_count")
        .rename_axis("geogid")
        .reset_index()
    )

    # Zero-fill every local authority with no matching facility.
    all_geogids = pd.DataFrame({"geogid": list(GEOGID_TO_LOCAL_AUTHORITY.keys())})
    counts = all_geogids.merge(counts, on="geogid", how="left")
    counts["facility_count"] = counts["facility_count"].fillna(0).astype(int)
    counts["local_authority"] = counts["geogid"].map(GEOGID_TO_LOCAL_AUTHORITY)

    return counts.sort_values("facility_count", ascending=False).reset_index(drop=True)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    la_features = load_la_features()
    la_features.to_csv(PROCESSED_DIR / "la_features.csv", index=False)
    print(f"Wrote {len(la_features)} local authority rows -> "
          f"{PROCESSED_DIR / 'la_features.csv'}")

    ed_features = load_ed_features()
    ed_features.to_csv(PROCESSED_DIR / "ed_features.csv", index=False)
    print(f"Wrote {len(ed_features)} electoral division rows -> "
          f"{PROCESSED_DIR / 'ed_features.csv'}")

    facilities = load_epa_facilities()
    facilities.to_csv(PROCESSED_DIR / "facility_counts.csv", index=False)
    print(f"Wrote {len(facilities)} local authority facility-count rows -> "
          f"{PROCESSED_DIR / 'facility_counts.csv'}")


if __name__ == "__main__":
    main()
