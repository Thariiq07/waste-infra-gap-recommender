"""
data/build_boundaries.py

One-off (already run) script that produces
data/raw/local_authority_boundaries.geojson: simplified polygon boundaries
for the current 31 Irish local authorities, keyed by the exact
`local_authority` names produced by data/ingest.py.

Why this exists: the CSO/Pobal/EPA datasets used elsewhere in this project
carry no geometry at all, just codes and numbers. The dashboard (Week 4)
needs actual shapes to draw a map. Ireland's *current* 31 local authorities
date from the 2014 local government reform, which merged three pairs of
pre-2014 administrative counties (Limerick City + Limerick County,
Waterford City + Waterford County, North Tipperary + South Tipperary) into
single authorities. The land boundaries of each merged authority didn't
change, only which council administers them, so this script takes a public
pre-2014 boundary set (34 areas) and dissolves those three pairs together
to get the current 31-area map.

Source geometry: CSO Census 2011 "Administrative Counties" boundaries
(generalised to 20m, i.e. already simplified for web/display use, not
survey-accuracy), mirrored on GitHub at
https://github.com/conormag/ireland-maps
(original: CSO Census 2011 boundary files, cso.ie).

Run:
    python data/build_boundaries.py
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd

RAW_DIR = Path(__file__).parent / "raw"
SOURCE_GEOJSON = RAW_DIR / "Census2011_Admin_Counties_generalised20m.geojson"
OUTPUT_GEOJSON = RAW_DIR / "local_authority_boundaries.geojson"

# 2011 COUNTYNAME -> current (2014-reform) local_authority name, matching
# data/ingest.py's GEOGID_TO_LOCAL_AUTHORITY values exactly. Three pairs
# collapse onto the same output name so geopandas.dissolve() merges them.
COUNTYNAME_TO_CURRENT_LA = {
    "Limerick City": "Limerick",
    "Limerick County": "Limerick",
    "North Tipperary": "Tipperary",
    "South Tipperary": "Tipperary",
    "Waterford City": "Waterford",
    "Waterford County": "Waterford",
    "Galway City": "Galway City",
    "Galway County": "Galway County",
    "Leitrim County": "Leitrim",
    "Mayo County": "Mayo",
    "Roscommon County": "Roscommon",
    "Sligo County": "Sligo",
    "Cavan County": "Cavan",
    "Donegal County": "Donegal",
    "Monaghan County": "Monaghan",
    "Carlow County": "Carlow",
    "Dublin City": "Dublin City",
    "South Dublin": "South Dublin",
    "Fingal": "Fingal",
    "Dún Laoghaire-Rathdown": "Dún Laoghaire-Rathdown",
    "Kildare County": "Kildare",
    "Kilkenny County": "Kilkenny",
    "Laois County": "Laois",
    "Longford County": "Longford",
    "Louth County": "Louth",
    "Meath County": "Meath",
    "Offaly County": "Offaly",
    "Westmeath County": "Westmeath",
    "Wexford County": "Wexford",
    "Wicklow County": "Wicklow",
    "Clare County": "Clare",
    "Cork City": "Cork City",
    "Cork County": "Cork County",
    "Kerry County": "Kerry",
}


def main() -> None:
    gdf = gpd.read_file(SOURCE_GEOJSON)
    assert len(gdf) == 34, f"expected 34 pre-2014 areas in source file, got {len(gdf)}"

    gdf["local_authority"] = gdf["COUNTYNAME"].map(COUNTYNAME_TO_CURRENT_LA)
    unmapped = gdf[gdf["local_authority"].isna()]
    assert unmapped.empty, f"unmapped COUNTYNAME values: {unmapped['COUNTYNAME'].tolist()}"

    merged = gdf.dissolve(by="local_authority", as_index=False)[["local_authority", "geometry"]]
    assert len(merged) == 31, f"expected 31 local authorities after merge, got {len(merged)}"

    # Simplify further for a lighter dashboard payload (already 20m-generalised
    # in the source; this trims it further for faster map rendering).
    merged["geometry"] = merged["geometry"].simplify(tolerance=0.002, preserve_topology=True)

    merged.to_file(OUTPUT_GEOJSON, driver="GeoJSON")
    print(f"Wrote {len(merged)} local authority boundaries -> {OUTPUT_GEOJSON}")


if __name__ == "__main__":
    main()
