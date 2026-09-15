"""
dashboard/app.py

Streamlit dashboard for the Waste Infrastructure Gap Recommender.

This is the "anyone can understand it" layer on top of the FastAPI service
(api/main.py): a coloured map of Ireland's 31 local authorities plus a
plain-language lookup, instead of raw JSON. No technical knowledge needed
to read it.

Run (with the API already running separately, e.g. `docker compose up` or
`uvicorn api.main:app --reload`):

    streamlit run dashboard/app.py

By default it talks to the API at http://localhost:8000. To point it at a
different API (e.g. once the API is deployed - see README), set the
WASTE_API_URL environment variable before launching:

    WASTE_API_URL=https://your-deployed-api.example.com streamlit run dashboard/app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make sure the project root is importable regardless of how/where this
# script is launched from (streamlit run inserts this script's own folder
# into sys.path, not the project root) - same reasoning as pytest.ini for
# the test suite.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import folium
import geopandas as gpd
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

from dashboard.logic import priority_color, priority_label

API_BASE_URL = os.environ.get("WASTE_API_URL", "http://localhost:8000").rstrip("/")
BOUNDARIES_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "raw", "local_authority_boundaries.geojson"
)

st.set_page_config(
    page_title="Waste Infrastructure Gap Recommender",
    page_icon="♻️",
    layout="wide",
)


@st.cache_data(ttl=300)
def fetch_underserved_index() -> pd.DataFrame | None:
    """Pull the full ranked list from the API. Returns None if it can't be reached."""
    try:
        resp = requests.get(f"{API_BASE_URL}/underserved-index", timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return None
    return pd.DataFrame(resp.json())


@st.cache_data
def load_boundaries() -> gpd.GeoDataFrame:
    return gpd.read_file(BOUNDARIES_PATH)


st.title("♻️ Where does Ireland need more e-waste recycling facilities?")
st.markdown(
    "Built from a Master's thesis that compared **how much e-waste each area "
    "is likely producing** against **how many licensed recycling facilities "
    "it actually has**. Darker red means a bigger gap between the two."
)

data = fetch_underserved_index()

if data is None:
    st.error(
        "Can't reach the API right now. Make sure it's running "
        f"(expected at `{API_BASE_URL}`) - e.g. run `docker compose up` "
        "or `uvicorn api.main:app --reload` in another terminal, then "
        "refresh this page."
    )
    st.stop()

boundaries = load_boundaries()
merged = boundaries.merge(data, on="local_authority", how="left")
merged["priority"] = merged["underserved_index"].apply(priority_label)
merged["priority_score_pct"] = (merged["underserved_index"] * 100).round(0).astype(int)

left, right = st.columns([2, 1])

with left:
    st.subheader("Priority map")
    # Plain OpenStreetMap tiles - no API key required (some other free
    # basemap providers, e.g. CartoDB's, now require one).
    m = folium.Map(location=[53.4, -8.0], zoom_start=6.7, tiles="OpenStreetMap")

    folium.GeoJson(
        merged,
        style_function=lambda feature: {
            "fillColor": priority_color(feature["properties"]["underserved_index"]),
            "color": "#333333",
            "weight": 1,
            "fillOpacity": 0.75,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "local_authority",
                "priority",
                "priority_score_pct",
                "facility_count",
                "cluster_label",
            ],
            aliases=[
                "Local authority:",
                "Priority:",
                "Priority score (0-100):",
                "Licensed facilities:",
                "Area type:",
            ],
            sticky=True,
        ),
    ).add_to(m)

    st_folium(m, width=None, height=560, returned_objects=[])

    st.caption(
        "\U0001f7e5 High priority   \U0001f7e7 Medium priority   \U0001f7e9 Lower priority "
        "— hover any area for details."
    )

with right:
    st.subheader("Look up a specific area")
    options = sorted(merged["local_authority"].tolist())
    choice = st.selectbox("Local authority", options, index=options.index("Fingal") if "Fingal" in options else 0)

    row = merged[merged["local_authority"] == choice].iloc[0]
    st.metric("Priority score", f"{row['priority_score_pct']} / 100", help="0 = well served, 100 = most underserved")
    st.markdown(f"**{row['priority']}** · {row['cluster_label']} area")
    st.markdown(
        f"- Licensed e-waste facilities: **{int(row['facility_count'])}**\n"
        f"- Households: **{int(row['total_households']):,}**"
    )
    if int(row["facility_count"]) == 0 and row["underserved_index"] >= 0.5:
        st.warning(
            f"{choice} has no licensed e-waste recycling facilities and a "
            "high estimated need. This is one of the gaps the original "
            "thesis identified."
        )

st.divider()
st.subheader("Full ranking, most underserved first")
table = merged.sort_values("underserved_index", ascending=False)[
    ["local_authority", "priority", "priority_score_pct", "cluster_label", "facility_count"]
].rename(
    columns={
        "local_authority": "Local authority",
        "priority": "Priority",
        "priority_score_pct": "Score (0-100)",
        "cluster_label": "Area type",
        "facility_count": "Facilities",
    }
)
st.dataframe(table, hide_index=True, width="stretch")

st.caption(
    "Data: CSO Census 2022, Pobal HP Deprivation Index 2022, EPA Licensed Waste "
    "Facilities register. Methodology: Master's thesis, "
    "“Multi-Scale Spatial Clustering Framework for E-Waste Infrastructure "
    "Planning”, University of Limerick."
)
